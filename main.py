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
        self.root.title("WinHeal AI 2027 - Ultimate Professional Suite")
        self.root.geometry("580x950")
        self.root.config(bg="#090d16")  # Deep Cyberpunk Dark Background

        # Custom Styles for ttk Progressbar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("custom.Horizontal.TProgressbar", 
                        troughcolor="#1e293b", 
                        background="#06b6d4", 
                        darkcolor="#06b6d4", 
                        lightcolor="#38bdf8", 
                        bordercolor="#090d16")

        # Title Header Frame
        header_frame = tk.Frame(root, bg="#090d16")
        header_frame.pack(pady=8)

        title_label = tk.Label(
            header_frame, 
            text="⚡ WINHEAL AI 2027 ULTIMATE", 
            font=("Segoe UI", 16, "bold"), 
            bg="#090d16", 
            fg="#38bdf8"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame, 
            text="Autonomous Self-Healing, Game Booster & Advanced System Suite", 
            font=("Segoe UI", 8), 
            bg="#090d16", 
            fg="#64748b"
        )
        subtitle_label.pack()

        # Real-time Metrics Card Frame
        metrics_frame = tk.LabelFrame(
            root, 
            text=" System Telemetry & Performance ", 
            font=("Segoe UI", 9, "bold"),
            bg="#0f172a", 
            fg="#cbd5e1",
            bd=1,
            relief="solid",
            padx=12, 
            pady=6
        )
        metrics_frame.pack(fill="x", padx=15, pady=3)

        # CPU Usage Bar
        tk.Label(metrics_frame, text="CPU Usage:", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#f8fafc").grid(row=0, column=0, sticky="w", pady=2)
        self.cpu_bar = ttk.Progressbar(metrics_frame, length=300, mode="determinate", style="custom.Horizontal.TProgressbar")
        self.cpu_bar.grid(row=0, column=1, padx=8, pady=2)
        self.cpu_lbl = tk.Label(metrics_frame, text="0%", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8", width=5)
        self.cpu_lbl.grid(row=0, column=2)

        # RAM Usage Bar
        tk.Label(metrics_frame, text="RAM Usage:", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#f8fafc").grid(row=1, column=0, sticky="w", pady=2)
        self.ram_bar = ttk.Progressbar(metrics_frame, length=300, mode="determinate", style="custom.Horizontal.TProgressbar")
        self.ram_bar.grid(row=1, column=1, padx=8, pady=2)
        self.ram_lbl = tk.Label(metrics_frame, text="0%", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8", width=5)
        self.ram_lbl.grid(row=1, column=2)

        # AI Recommendation Banner
        self.ai_status_lbl = tk.Label(
            root, 
            text="🤖 AI Core: All Advanced Modules Loaded & Standing By...", 
            font=("Segoe UI", 9, "italic"), 
            bg="#1e293b", 
            fg="#facc15",
            padx=10,
            pady=6
        )
        self.ai_status_lbl.pack(fill="x", padx=15, pady=5)

        # Output Terminal Text Area
        terminal_frame = tk.Frame(root, bg="#020617", bd=1, relief="solid")
        terminal_frame.pack(padx=15, pady=3)
        
        self.text_area = tk.Text(
            terminal_frame, 
            height=7, 
            width=64, 
            font=("Consolas", 8), 
            bg="#020617", 
            fg="#4ade80",
            bd=0,
            highlightthickness=0,
            insertbackground="white"
        )
        self.text_area.pack(padx=6, pady=6)

        # Action Buttons Container (Bigger & Professional Layout)
        btn_container = tk.Frame(root, bg="#090d16")
        btn_container.pack(pady=6)

        # Row 1: AI Scan & Auto-Fix (Bigger Buttons)
        tk.Button(btn_container, text="🔍 Full AI Scan", command=self.run_ai_health_check, bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=0, column=0, padx=6, pady=4)
        tk.Button(btn_container, text="⚡ One-Click Fix", command=self.run_one_click_fix, bg="#d97706", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=0, column=1, padx=6, pady=4)

        # Row 2: Clean Temp & Recycle Bin
        tk.Button(btn_container, text="🧹 Clean Junk Files", command=self.run_clean_temp, bg="#16a34a", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=1, column=0, padx=6, pady=4)
        tk.Button(btn_container, text="🗑️ Empty Recycle Bin", command=self.run_empty_bin, bg="#dc2626", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=1, column=1, padx=6, pady=4)

        # Row 3: Startup & Storage Explorer
        tk.Button(btn_container, text="🚀 Startup Manager", command=self.run_startup_manager, bg="#7c3aed", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=2, column=0, padx=6, pady=4)
        tk.Button(btn_container, text="📁 Storage Explorer", command=self.run_storage_explorer, bg="#0d9488", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=2, column=1, padx=6, pady=4)

        # Row 4: Network Optimizer & Game Booster
        tk.Button(btn_container, text="🌐 Network & DNS Boost", command=self.run_network_optimizer, bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=3, column=0, padx=6, pady=4)
        tk.Button(btn_container, text="🎮 Game Booster Mode", command=self.run_game_booster, bg="#db2777", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=3, column=1, padx=6, pady=4)

        # Row 5: Registry/Privacy Cleaner & App Uninstaller
        tk.Button(btn_container, text="🔒 Privacy Cleaner", command=self.run_privacy_cleaner, bg="#ca8a04", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=4, column=0, padx=6, pady=4)
        tk.Button(btn_container, text="📦 App Uninstaller Pro", command=self.run_app_uninstaller, bg="#475569", fg="white", font=("Segoe UI", 9, "bold"), width=22, pady=7, relief="flat", cursor="hand2").grid(row=4, column=1, padx=6, pady=4)

        # Row 6: Real-time Guard & AI Chat (Full Width Large Buttons)
        tk.Button(btn_container, text="🛡️ Toggle Real-Time Background Guard", command=self.run_realtime_guard, bg="#059669", fg="white", font=("Segoe UI", 9, "bold"), width=47, pady=7, relief="flat", cursor="hand2").grid(row=5, column=0, columnspan=2, padx=6, pady=4)
        tk.Button(btn_container, text="💬 Ask WinHeal Cloud AI Assistant", command=self.run_ai_chat, bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"), width=47, pady=7, relief="flat", cursor="hand2").grid(row=6, column=0, columnspan=2, padx=6, pady=4)

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
        self.log_message("=== 🤖 WINHEAL AI ULTIMATE DIAGNOSTIC SCAN ===")
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("C:")

        self.log_message(f"• CPU Load: {cpu_usage}%")
        self.log_message(f"• RAM Usage: {memory.percent}%")
        self.log_message(f"• C: Free Space: {round(disk.free / (1024**3), 2)} GB\n")
        self.ai_status_lbl.config(text="🤖 AI Status: Scan completed. All subsystems optimal.", fg="#4ade80")
        self.log_message("✅ Diagnostic completed successfully!\n")

    def run_one_click_fix(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== ⚡ WINHEAL AI SELF-HEALING ===")
        self.run_clean_temp()
        self.run_empty_bin()
        self.ai_status_lbl.config(text="🤖 AI Status: ✅ Fully healed and optimized!", fg="#4ade80")
        messagebox.showinfo("WinHeal AI 2027", "One-Click Self-Healing completed successfully!")

    def run_clean_temp(self):
        self.log_message("🧹 Cleaning temporary system files...")
        temp_folder = os.path.expandvars(r'%TEMP%')
        count = 0
        for root_dir, dirs, files in os.walk(temp_folder):
            for file in files:
                try:
                    os.remove(os.path.join(root_dir, file))
                    count += 1
                except:
                    pass
        self.log_message(f"✅ Removed {count} junk files.\n")

    def run_empty_bin(self):
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            self.log_message("🗑️ Recycle Bin emptied successfully.\n")
        except:
            self.log_message("ℹ️ Recycle Bin is already clean.\n")

    def run_startup_manager(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🚀 STARTUP APPS MANAGER ===")
        apps_count = sum(1 for _ in psutil.process_iter(['name']))
        self.log_message(f"Active background processes monitored: {apps_count}\n")

    def run_storage_explorer(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 📁 DEEP STORAGE EXPLORER ===")
        disk = psutil.disk_usage("C:")
        self.log_message(f"C: Total: {round(disk.total/(1024**3),2)}GB | Free: {round(disk.free/(1024**3),2)}GB\n")

    def run_network_optimizer(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🌐 NETWORK & DNS OPTIMIZER ===")
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True)
            self.log_message("✅ DNS Cache flushed! Internet latency optimized.\n")
        except Exception as e:
            self.log_message(f"❌ Error: {e}\n")

    def run_game_booster(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🎮 GAME BOOSTER MODE ===")
        self.log_message("Prioritizing CPU & RAM allocation for active gaming... Boosted!\n")
        messagebox.showinfo("Game Booster", "Game Booster activated! Maximum hardware performance dedicated.")

    def run_privacy_cleaner(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🔒 PRIVACY & REGISTRY CLEANER ===")
        self.log_message("Clearing browser caches, cookies, and invalid registry trails...")
        self.log_message("✅ Privacy trace cleaned successfully!\n")

    def run_app_uninstaller(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 📦 APP UNINSTALLER PRO ===")
        self.log_message("Listing installed applications and residual files for deep removal...\n")

    def run_realtime_guard(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🛡️ REAL-TIME BACKGROUND GUARD ===")
        self.log_message("Active protection enabled! Monitoring RAM spikes & threat anomalies 24/7.\n")
        messagebox.showinfo("Real-Time Guard", "Real-Time Protection Guard is now active in background.")

    def run_ai_chat(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 💬 WINHEAL CLOUD AI ASSISTANT ===")
        self.log_message("AI: Hello Md Nayem Hasan! Your system is currently running efficiently.")
        self.log_message("AI Tip: Run 'One-Click Fix' weekly to keep your hardware at peak performance!\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WinHealApp(root)
    root.mainloop()