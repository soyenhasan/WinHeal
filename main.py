import os
import shutil
import psutil
import ctypes
import tkinter as tk
from tkinter import messagebox

class WinHealApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WinHeal AI - System Optimizer")
        self.root.geometry("450x500")
        self.root.config(bg="#f0f4f8")

        # Title Label
        title_label = tk.Label(root, text="🚀 WinHeal AI Dashboard", font=("Arial", 16, "bold"), bg="#f0f4f8", fg="#1e293b")
        title_label.pack(pady=15)

        # Status/Output Text Box
        self.text_area = tk.Text(root, height=15, width=50, font=("Consolas", 10), bg="#ffffff", fg="#334155")
        self.text_area.pack(pady=10)

        # Buttons Frame
        btn_frame = tk.Frame(root, bg="#f0f4f8")
        btn_frame.pack(pady=10)

        # Health Check Button
        btn_health = tk.Button(btn_frame, text="System Health", command=self.run_health_check, bg="#2563eb", fg="white", font=("Arial", 10, "bold"), width=15)
        btn_health.grid(row=0, column=0, padx=5, pady=5)

        # Clean Temp Files Button
        btn_temp = tk.Button(btn_frame, text="Clean Temp", command=self.run_clean_temp, bg="#16a34a", fg="white", font=("Arial", 10, "bold"), width=15)
        btn_temp.grid(row=0, column=1, padx=5, pady=5)

        # Empty Recycle Bin Button
        btn_bin = tk.Button(btn_frame, text="Empty Bin", command=self.run_empty_bin, bg="#dc2626", fg="white", font=("Arial", 10, "bold"), width=15)
        btn_bin.grid(row=1, column=0, columnspan=2, pady=5)

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def run_health_check(self, clear_box=True):
        if clear_box:
            self.text_area.delete("1.0", tk.END)
        self.log_message("--- 🚀 System Health Check ---")
        cpu_usage = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("C:")
        
        self.log_message(f"CPU Usage: {cpu_usage}%")
        self.log_message(f"Total RAM: {round(memory.total / (1024**3), 2)} GB")
        self.log_message(f"Used RAM: {memory.percent}%")
        self.log_message(f"C: Drive Free: {round(disk.free / (1024**3), 2)} GB\n")

    def run_clean_temp(self):
        self.log_message("--- 🧹 Cleaning Temporary Files ---")
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

        self.log_message(f"Deleted temp files: {deleted_files}")
        self.log_message(f"Skipped (in use): {failed_files}\n")

    def run_empty_bin(self):
        self.log_message("--- 🗑️ Emptying Recycle Bin ---")
        try:
            result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            if result == 0:
                self.log_message("Recycle Bin successfully emptied!\n")
            else:
                self.log_message("Recycle Bin is already empty.\n")
        except Exception as e:
            self.log_message(f"Error: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WinHealApp(root)
    root.mainloop()