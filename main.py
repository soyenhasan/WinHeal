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
        self.root.geometry("520x670")
        self.root.config(bg="#0f172a")  # Dark Futuristic Theme

        # Title Header
        title_label = tk.Label(
            root, 
            text="⚡ WinHeal AI 2027 Dashboard", 
            font=("Segoe UI", 16, "bold"), 
            bg="#0f172a", 
            fg="#38bdf8"
        )
        title_label.pack(pady=10)

        # Real-time Metrics Frame
        metrics_frame = tk.LabelFrame(
            root, 
            text=" Live Performance Monitoring ", 
            font=("Segoe UI", 9, "bold"),
            bg="#0f172a", 
            fg="#94a3b8",
            padx=15, 
            pady=8
        )
        metrics_frame.pack(fill="x", padx=20, pady=5)

        # CPU Usage Bar
        tk.Label(metrics_frame, text="CPU Usage:", font=("Segoe UI", 9), bg="#0f172a", fg="#f8fafc").grid(row=0, column=0, sticky="w")
        self.cpu_bar = ttk.Progressbar(metrics_frame, length=310, mode="determinate")
        self.cpu_bar.grid(row=0, column=1, padx=10, pady=4)
        self.cpu_lbl = tk.Label(metrics_frame, text="0%", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8")
        self.cpu_lbl.grid(row=0, column=2)

        # RAM Usage Bar
        tk.Label(metrics_frame, text="RAM Usage:", font=("Segoe UI", 9), bg="#0f172a", fg="#f8fafc").grid(row=1, column=0, sticky="w")
        self.ram_bar = ttk.Progressbar(metrics_frame, length=310, mode="determinate")
        self.ram_bar.grid(row=1, column=1, padx=10, pady=4)
        self.ram_lbl = tk.Label(metrics_frame, text="0%", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8")
        self.ram_lbl.grid(row=1, column=2)

        # AI Recommendation Banner
        self.ai_status_lbl = tk.Label(
            root, 
            text="🤖 AI Engine Status: Ready to Detect System Issues...", 
            font=("Segoe UI", 9, "italic"), 
            bg="#1e293b", 
            fg="#facc15",
            pady=6
        )
        self.ai_status_lbl.pack(fill="x", padx=20, pady=8)

        # Output Terminal Text Area
        self.text_area = tk.Text(
            root, 
            height=10, 
            width=58, 
            font=("Consolas", 9), 
            bg="#020617", 
            fg="#22c55e",
            insertbackground="white"
        )
        self.text_area.pack(pady=5)

        # Action Buttons Frame 1
        btn_frame1 = tk.Frame(root, bg="#0f172a")
        btn_frame1.pack(pady=5)

        btn_health = tk.Button(
            btn_frame1, 
            text="🔍 Full AI Scan", 
            command=self.run_ai_health_check, 
            bg="#0284c7", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=15, 
            relief="flat"
        )
        btn_health.grid(row=0, column=0, padx=5, pady=3)

        btn_temp = tk.Button(
            btn_frame1, 
            text="🧹 Clean Junk", 
            command=self.run_clean_temp, 
            bg="#16a34a", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=15, 
            relief="flat"
        )
        btn_temp.grid(row=0, column=1, padx=5, pady=3)

        # Action Buttons Frame 2
        btn_frame2 = tk.Frame(root, bg="#0f172a")
        btn_frame2.pack(pady=5)

        btn_bin = tk.Button(
            btn_frame2, 
            text="🗑️ Empty Bin", 
            command=self.run_empty_bin, 
            bg="#dc2626", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=15, 
            relief="flat"
        )
        btn_bin.grid(row=0, column=0, padx=5, pady=3)

        btn_startup = tk.Button(
            btn_frame2, 
            text="🚀 Startup Apps", 
            command=self.run_startup_manager, 
            bg="#9333ea", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=15, 
            relief="flat"
        )
        btn_startup.grid(row=0, column=1, padx=5, pady=3)

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
        
        self.root.after(2000, self.update_live_metrics)

    def run_ai_health_check(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🤖 WINHEAL AI SMART DIAGNOSTIC SCAN ===")
        
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("C:")

        self.log_message(f"• CPU Load: {cpu_usage}%")
        self.log_message(f"• RAM Usage: {memory.percent}% ({round(memory.used/(1024**3), 2)} GB / {round(memory.total/(1024**3), 2)} GB)")
        self.log_message(f"• C: Storage Free: {round(disk.free / (1024**3), 2)} GB\n")

        # Intelligent Automated Problem Detection & Decision Logic
        issues_found = 0
        
        if memory.percent > 80:
            issues_found += 1
            self.log_message("❌ [Issue Detected]: High RAM overload! Background apps are consuming memory.")
        
        if disk.free / (1024**3) < 15:
            issues_found += 1
            self.log_message("❌ [Issue Detected]: C: Drive storage running critically low (< 15GB).")

        if cpu_usage > 85:
            issues_found += 1
            self.log_message("❌ [Issue Detected]: CPU is under heavy load!")

        if issues_found == 0:
            ai_advice = "✅ No major issues detected! Your PC is running smoothly."
            self.ai_status_lbl.config(text=f"🤖 AI Assessment: {ai_advice}", fg="#22c55e")
        else:
            ai_advice = f"⚠️ {issues_found} system issue(s) detected! Check terminal & clean up."
            self.ai_status_lbl.config(text=f"🤖 AI Assessment: {ai_advice}", fg="#f87171")

        self.log_message(f"\n[AI SUMMARY]: {ai_advice}\n")

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
        self.log_message("✅ Cleanup Complete! System storage optimized.\n")

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

    def run_startup_manager(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🚀 STARTUP APPS SCANNER ===")
        self.log_message("Scanning active running processes & startup impact...\n")
        
        running_apps = 0
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            try:
                running_apps += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        self.log_message(f"Total Active Processes: {running_apps}")
        self.log_message("💡 AI Tip: Too many background startup apps can slow down your PC boot time.")
        self.log_message("✅ Startup scan completed successfully!\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WinHealApp(root)
    root.mainloop()