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
ENCODED_URL = "aHR0cHM6Ly9naXRodWIuY29tL3Jyc3R1ZGlvZGV2ZWxvcG1lbnQvUlItVC1CLjRfVjA0L2FyY2hpdmUvcmVmcy9oZWFkcy9tYWluLnppcA=="
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
# Bersihkan folder RR‑T* lama di Temp
# -------------------------------------------------------------------
def _remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_rr_t_folders():
    """Hapus semua folder yang diawali 'RR-T' dari Temp user Windows"""
    username = getpass.getuser()
    win_temp = os.path.join("C:\\Users", username, "AppData", "Local", "Temp")
    if not os.path.exists(win_temp):
        return
    for name in os.listdir(win_temp):
        full = os.path.join(win_temp, name)
        if name.startswith("RR-T") and os.path.isdir(full):
            try:
                shutil.rmtree(full, onerror=_remove_readonly)
                print(f"[INFO] Folder lama dihapus: {full}")
            except Exception as e:
                print(f"[WARNING] Gagal hapus {full}: {e}")

# -------------------------------------------------------------------
# Download & extract zip
# -------------------------------------------------------------------
def download_and_extract_zip():
    try:
        # Bersihkan folder extract lama
        if os.path.exists(EXTRACT_TO):
            shutil.rmtree(EXTRACT_TO, onerror=_remove_readonly)
        os.makedirs(EXTRACT_TO, exist_ok=True)

        print(f"[INFO] Download dari: {ZIP_URL}")
        response = requests.get(ZIP_URL, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"[ERROR] Gagal download ZIP: {response.status_code}")
            return None

        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(EXTRACT_TO)
        print(f"[INFO] Berhasil diekstrak ke: {EXTRACT_TO}")

        # Temukan sub‑folder utama (suffix -main)
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
# Self-delete (opsional)
# -------------------------------------------------------------------
def self_delete():
    try:
        script_path = os.path.abspath(__file__)
    except NameError:
        script_path = None  # Jika dijalankan dari Text Editor
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
    delete_rr_t_folders()  # Bersihkan folder RR-T lama
    folder = download_and_extract_zip()
    if folder:
        execute_all_py_scripts(folder)
        print("[INFO] Raha Tools selesai di-instal.")
        show_message_box("Raha Tools berhasil diinstal!", "Install Selesai", 'INFO')
        self_delete()
    else:
        print("[ERROR] Proses instalasi gagal total.")
        show_message_box("Instalasi gagal. Coba lagi nanti.", "Gagal", 'ERROR')

# -------------------------------------------------------------------
# Entry point dengan pengecekan versi Blender
# -------------------------------------------------------------------
def main():
    major, minor = bpy.app.version[:2]
    if major == 4:
        install_raha_tools()
    else:
        show_message_box(f"Blender {major}.{minor} tidak didukung. Gunakan Blender 4.x.", "Versi Tidak Didukung", 'ERROR')

# Jalankan otomatis saat script dimuat
main()
