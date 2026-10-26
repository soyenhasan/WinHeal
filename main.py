import os
import shutil
import psutil
import ctypes
import tkinter as tk
from tkinter import messagebox, ttk

class WinHealApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WinHeal AI 2027 - Advanced System Optimizer")
        self.root.geometry("500x600")
        self.root.config(bg="#0f172a")  # Dark Futuristic Theme

        # Title Header
        title_label = tk.Label(
            root, 
            text="⚡ WinHeal AI 2027 Dashboard", 
            font=("Segoe UI", 16, "bold"), 
            bg="#0f172a", 
            fg="#38bdf8"
        )
        title_label.pack(pady=15)

        # Real-time Metrics Frame
        metrics_frame = tk.LabelFrame(
            root, 
            text=" Live Performance Monitoring ", 
            font=("Segoe UI", 10, "bold"),
            bg="#0f172a", 
            fg="#94a3b8",
            padx=15, 
            pady=10
        )
        metrics_frame.pack(fill="x", padx=20, pady=5)

        # CPU Usage Bar
        tk.Label(metrics_frame, text="CPU Usage:", font=("Segoe UI", 9), bg="#0f172a", fg="#f8fafc").grid(row=0, column=0, sticky="w")
        self.cpu_bar = ttk.Progressbar(metrics_frame, length=300, mode="determinate")
        self.cpu_bar.grid(row=0, column=1, padx=10, pady=5)
        self.cpu_lbl = tk.Label(metrics_frame, text="0%", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8")
        self.cpu_lbl.grid(row=0, column=2)

        # RAM Usage Bar
        tk.Label(metrics_frame, text="RAM Usage:", font=("Segoe UI", 9), bg="#0f172a", fg="#f8fafc").grid(row=1, column=0, sticky="w")
        self.ram_bar = ttk.Progressbar(metrics_frame, length=300, mode="determinate")
        self.ram_bar.grid(row=1, column=1, padx=10, pady=5)
        self.ram_lbl = tk.Label(metrics_frame, text="0%", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8")
        self.ram_lbl.grid(row=1, column=2)

        # AI Recommendation Banner
        self.ai_status_lbl = tk.Label(
            root, 
            text="🤖 AI Engine Status: Ready to Analyze System Health...", 
            font=("Segoe UI", 9, "italic"), 
            bg="#1e293b", 
            fg="#facc15",
            pady=8
        )
        self.ai_status_lbl.pack(fill="x", padx=20, pady=10)

        # Output Terminal Text Area
        self.text_area = tk.Text(
            root, 
            height=12, 
            width=55, 
            font=("Consolas", 9), 
            bg="#020617", 
            fg="#22c55e",
            insertbackground="white"
        )
        self.text_area.pack(pady=5)

        # Action Buttons Frame
        btn_frame = tk.Frame(root, bg="#0f172a")
        btn_frame.pack(pady=10)

        btn_health = tk.Button(
            btn_frame, 
            text="🔍 Full AI Scan", 
            command=self.run_ai_health_check, 
            bg="#0284c7", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=14, 
            relief="flat"
        )
        btn_health.grid(row=0, column=0, padx=5, pady=5)

        btn_temp = tk.Button(
            btn_frame, 
            text="🧹 Clean Junk", 
            command=self.run_clean_temp, 
            bg="#16a34a", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=14, 
            relief="flat"
        )
        btn_temp.grid(row=0, column=1, padx=5, pady=5)

        btn_bin = tk.Button(
            btn_frame, 
            text="🗑️ Empty Bin", 
            command=self.run_empty_bin, 
            bg="#dc2626", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=14, 
            relief="flat"
        )
        btn_bin.grid(row=0, column=2, padx=5, pady=5)

        # Start live metrics auto-update
        self.update_live_metrics()

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def update_live_metrics(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        self.cpu_bar['value'] = cpu
        self.cpu_lbl.config(text=f"{cpu}%")
        
        self.ram_bar['value'] = ram
        self.ram_lbl.config(text=f"{ram}%")
        
        # Update metrics every 2 seconds
        self.root.after(2000, self.update_live_metrics)

    def run_ai_health_check(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🤖 WINHEAL AI DIAGNOSTIC REPORT ===")
        
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("C:")

        self.log_message(f"• CPU Load: {cpu_usage}%")
        self.log_message(f"• RAM Usage: {memory.percent}% ({round(memory.used/(1024**3), 2)} GB / {round(memory.total/(1024**3), 2)} GB)")
        self.log_message(f"• C: Storage Free: {round(disk.free / (1024**3), 2)} GB\n")

        # Smart AI Analysis & Decision Logic
        if memory.percent > 80:
            ai_advice = "⚠️ High RAM usage detected! Recommended to run Junk Cleaner."
        elif disk.free / (1024**3) < 15:
            ai_advice = "⚠️ Storage running low on C: drive! Clean temp files to free space."
        else:
            ai_advice = "✅ System Health Excellent! All metrics optimal."

        self.ai_status_lbl.config(text=f"🤖 AI Assessment: {ai_advice}")
        self.log_message(f"[AI INSIGHT]: {ai_advice}\n")

    def run_clean_temp(self):
        self.log_message("=== 🧹 CLEANING TEMPORARY JUNK FILES ===")
        temp_folder = os.path.expandvars(r'%TEMP%')
        deleted_files = 0
        failed_files = 0

        for root_dir, dirs, files in os.walk(temp_folder):
            for file in files:
                file_path = os.path.join(root_dir, file)
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except Exception:
                    failed_files += 1

        self.log_message(f"Deleted Files: {deleted_files}")
        self.log_message(f"In-Use Skipped: {failed_files}\n")
        self.log_message("✅ Cleanup Complete!\n")

    def run_empty_bin(self):
        self.log_message("=== 🗑️ EMPTYING RECYCLE BIN ===")
        try:
            result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            if result == 0:
                self.log_message("✅ Recycle Bin successfully cleared!\n")
            else:
                self.log_message("ℹ️ Recycle Bin is already empty.\n")
        except Exception as e:
            self.log_message(f"❌ Error: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WinHealApp(root)
    root.mainloop()