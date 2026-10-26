import os
import shutil
import psutil
import ctypes

def check_system_health():
    print("--- 🚀 WinHeal AI: System Health Check ---")
    
    # Check CPU Usage
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_usage}%")
    
    # Check Memory (RAM) Usage
    memory = psutil.virtual_memory()
    print(f"Total RAM: {round(memory.total / (1024**3), 2)} GB")
    print(f"Used RAM: {memory.percent}%")
    
    # Check Disk Usage (C: Drive)
    disk = psutil.disk_usage("C:")
    print(f"C: Drive Total: {round(disk.total / (1024**3), 2)} GB")
    print(f"C: Drive Free: {round(disk.free / (1024**3), 2)} GB")
    print("-" * 40)

def clear_temp_files():
    print("--- 🧹 Cleaning Temporary Files ---")
    temp_folder = os.path.expandvars(r'%TEMP%')
    deleted_files = 0
    failed_files = 0

    for root, dirs, files in os.walk(temp_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                deleted_files += 1
            except Exception:
                failed_files += 1

    print(f"Successfully deleted temporary files: {deleted_files}")
    print(f"Skipped (in use) files: {failed_files}")
    print("-" * 40)

def empty_recycle_bin():
    print("--- 🗑️ Emptying Recycle Bin ---")
    try:
        # SHEmptyRecycleBinW flags: 7 means no confirmation dialog, no progress bar, no sound
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        if result == 0:
            print("Recycle Bin successfully emptied!")
        else:
            print("Recycle Bin is already empty or could not be cleared.")
    except Exception as e:
        print(f"Error clearing Recycle Bin: {e}")
    print("-" * 40)

if __name__ == "__main__":
    check_system_health()
    print("\n")
    clear_temp_files()
    print("\n")
    empty_recycle_bin()