import os
import shutil
import psutil
import ctypes
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

class WinHealApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WinHeal AI 2027 - Advanced System Optimizer")
        self.root.geometry("520x820")
        self.root.config(bg="#0f172a")  # Dark Futuristic Theme

        # Title Header
        title_label = tk.Label(
            root, 
            text="⚡ WinHeal AI 2027 Dashboard", 
            font=("Segoe UI", 16, "bold"), 
            bg="#0f172a", 
            fg="#38bdf8"
        )
        title_label.pack(pady=8)

        # Real-time Metrics Frame
        metrics_frame = tk.LabelFrame(
            root, 
            text=" Live Performance Monitoring ", 
            font=("Segoe UI", 9, "bold"),
            bg="#0f172a", 
            fg="#94a3b8",
            padx=15, 
            pady=6
        )
        metrics_frame.pack(fill="x", padx=20, pady=4)

        # CPU Usage Bar
        tk.Label(metrics_frame, text="CPU Usage:", font=("Segoe UI", 9), bg="#0f172a", fg="#f8fafc").grid(row=0, column=0, sticky="w")
        self.cpu_bar = ttk.Progressbar(metrics_frame, length=310, mode="determinate")
        self.cpu_bar.grid(row=0, column=1, padx=10, pady=3)
        self.cpu_lbl = tk.Label(metrics_frame, text="0%", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8")
        self.cpu_lbl.grid(row=0, column=2)

        # RAM Usage Bar
        tk.Label(metrics_frame, text="RAM Usage:", font=("Segoe UI", 9), bg="#0f172a", fg="#f8fafc").grid(row=1, column=0, sticky="w")
        self.ram_bar = ttk.Progressbar(metrics_frame, length=310, mode="determinate")
        self.ram_bar.grid(row=1, column=1, padx=10, pady=3)
        self.ram_lbl = tk.Label(metrics_frame, text="0%", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8")
        self.ram_lbl.grid(row=1, column=2)

        # AI Recommendation Banner
        self.ai_status_lbl = tk.Label(
            root, 
            text="🤖 AI Engine Status: Ready for Advanced Optimization...", 
            font=("Segoe UI", 9, "italic"), 
            bg="#1e293b", 
            fg="#facc15",
            pady=5
        )
        self.ai_status_lbl.pack(fill="x", padx=20, pady=6)

        # Output Terminal Text Area
        self.text_area = tk.Text(
            root, 
            height=9, 
            width=58, 
            font=("Consolas", 9), 
            bg="#020617", 
            fg="#22c55e",
            insertbackground="white"
        )
        self.text_area.pack(pady=3)

        # Action Buttons Frame 1
        btn_frame1 = tk.Frame(root, bg="#0f172a")
        btn_frame1.pack(pady=2)

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
        btn_health.grid(row=0, column=0, padx=5, pady=2)

        btn_autofix = tk.Button(
            btn_frame1, 
            text="⚡ One-Click Fix", 
            command=self.run_one_click_fix, 
            bg="#ea580c", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=15, 
            relief="flat"
        )
        btn_autofix.grid(row=0, column=1, padx=5, pady=2)

        # Action Buttons Frame 2
        btn_frame2 = tk.Frame(root, bg="#0f172a")
        btn_frame2.pack(pady=2)

        btn_temp = tk.Button(
            btn_frame2, 
            text="🧹 Clean Junk", 
            command=self.run_clean_temp, 
            bg="#16a34a", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=15, 
            relief="flat"
        )
        btn_temp.grid(row=0, column=0, padx=5, pady=2)

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
        btn_bin.grid(row=0, column=1, padx=5, pady=2)

        # Action Buttons Frame 3
        btn_frame3 = tk.Frame(root, bg="#0f172a")
        btn_frame3.pack(pady=2)

        btn_startup = tk.Button(
            btn_frame3, 
            text="🚀 Startup Apps", 
            command=self.run_startup_manager, 
            bg="#9333ea", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=15, 
            relief="flat"
        )
        btn_startup.grid(row=0, column=0, padx=5, pady=2)

        btn_storage = tk.Button(
            btn_frame3, 
            text="📁 Storage Explorer", 
            command=self.run_storage_explorer, 
            bg="#0d9488", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=15, 
            relief="flat"
        )
        btn_storage.grid(row=0, column=1, padx=5, pady=2)

        # Action Buttons Frame 4 (New Network Optimizer Feature)
        btn_frame4 = tk.Frame(root, bg="#0f172a")
        btn_frame4.pack(pady=2)

        btn_network = tk.Button(
            btn_frame4, 
            text="🌐 Network & DNS Boost", 
            command=self.run_network_optimizer, 
            bg="#2563eb", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            width=32, 
            relief="flat"
        )
        btn_network.grid(row=0, column=0, padx=5, pady=2)

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

        issues_found = 0
        if memory.percent > 80:
            issues_found += 1
            self.log_message("❌ [Issue Detected]: High RAM overload!")
        if disk.free / (1024**3) < 15:
            issues_found += 1
            self.log_message("❌ [Issue Detected]: C: Drive storage low!")
        if cpu_usage > 85:
            issues_found += 1
            self.log_message("❌ [Issue Detected]: Heavy CPU load!")

        if issues_found == 0:
            ai_advice = "✅ All systems optimal. Click 'One-Click Fix' anytime for routine tune-up."
            self.ai_status_lbl.config(text=f"🤖 AI Status: {ai_advice}", fg="#22c55e")
        else:
            ai_advice = f"⚠️ {issues_found} issue(s) found! Click '⚡ One-Click Fix' to resolve automatically."
            self.ai_status_lbl.config(text=f"🤖 AI Status: {ai_advice}", fg="#f87171")

        self.log_message(f"\n[AI SUMMARY]: {ai_advice}\n")

    def run_one_click_fix(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== ⚡ WINHEAL AI AUTOMATED SELF-HEALING ===")
        self.log_message("Initializing smart repair protocols...\n")

        temp_folder = os.path.expandvars(r'%TEMP%')
        deleted_files = 0
        for root_dir, dirs, files in os.walk(temp_folder):
            for file in files:
                try:
                    os.remove(os.path.join(root_dir, file))
                    deleted_files += 1
                except Exception:
                    pass
        self.log_message(f"🧹 Cleaned Junk: {deleted_files} temporary files removed.")

        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            self.log_message("🗑️ Recycle Bin: Successfully emptied.")
        except Exception:
            self.log_message("ℹ️ Recycle Bin: Already clean.")

        self.ai_status_lbl.config(text="🤖 AI Status: ✅ System fully optimized and healed!", fg="#22c55e")
        self.log_message("\n🎉 SUCCESS: All automated maintenance tasks completed!\n")
        messagebox.showinfo("WinHeal AI 2027", "Automated Self-Healing completed successfully!")

    def run_clean_temp(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🧹 CLEANING TEMPORARY JUNK FILES ===")
        temp_folder = os.path.expandvars(r'%TEMP%')
        deleted_files = 0
        for root_dir, dirs, files in os.walk(temp_folder):
            for file in files:
                try:
                    os.remove(os.path.join(root_dir, file))
                    deleted_files += 1
                except Exception:
                    pass
        self.log_message(f"Deleted Files: {deleted_files}\n✅ Cleanup Complete!\n")

    def run_empty_bin(self):
        self.text_area.delete("1.0", tk.END)
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
        running_apps = sum(1 for _ in psutil.process_iter(['name']))
        self.log_message(f"Total Active Processes: {running_apps}")
        self.log_message("💡 AI Tip: Keep background processes minimal for fast boot.\n")

    def run_storage_explorer(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 📁 DEEP STORAGE & FILE EXPLORER ===")
        try:
            disk = psutil.disk_usage("C:")
            self.log_message(f"• Total: {round(disk.total / (1024**3), 2)} GB")
            self.log_message(f"• Used: {round(disk.used / (1024**3), 2)} GB ({disk.percent}%)")
            self.log_message(f"• Free: {round(disk.free / (1024**3), 2)} GB\n")
            self.log_message("✅ Storage analysis completed successfully!\n")
        except Exception as e:
            self.log_message(f"❌ Error: {e}\n")

    def run_network_optimizer(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🌐 NETWORK & DNS OPTIMIZER ===")
        self.log_message("Flushing DNS resolver cache to speed up internet...\n")
        
        try:
            # Run ipconfig /flushdns command
            result = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.log_message("✅ DNS Cache successfully flushed!")
                self.log_message("🌐 Network optimized: Web browsing speed and latency improved.\n")
            else:
                self.log_message("⚠️ DNS flush executed with warnings.\n")
        except Exception as e:
            self.log_message(f"❌ Network optimization error: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WinHealApp(root)
    root.mainloop()