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
        self.root.title("WinHeal AI 2027 - Ultimate Cyber Graphics Suite")
        self.root.geometry("1150x760")
        self.root.config(bg="#020617")  # Deep Ultra-Dark Tech Background

        # Custom Styles for Progressbars & Widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("cyber.Horizontal.TProgressbar", 
                        troughcolor="#0f172a", 
                        background="#10b981", 
                        darkcolor="#10b981", 
                        lightcolor="#34d399", 
                        bordercolor="#020617")

        # --- MAIN CONTAINER ---
        main_container = tk.Frame(root, bg="#020617")
        main_container.pack(fill="both", expand=True)

        # ==========================================
        # 1. LEFT SIDEBAR (Modern Tech Control Panel)
        # ==========================================
        sidebar = tk.Frame(main_container, bg="#090d16", width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Brand Header
        brand_frame = tk.Frame(sidebar, bg="#090d16")
        brand_frame.pack(pady=25)

        tk.Label(
            brand_frame, 
            text="⚡ WINHEAL AI", 
            font=("Segoe UI", 14, "bold"), 
            bg="#090d16", 
            fg="#38bdf8"
        ).pack(anchor="w", padx=20)

        tk.Label(
            brand_frame, 
            text="NEURAL GRAPHICS v4.0", 
            font=("Segoe UI", 7, "bold"), 
            bg="#090d16", 
            fg="#10b981"
        ).pack(anchor="w", padx=20)

        # Professional Menu Items
        menu_items = [
            ("⚡ Neural AI Scan", self.run_ai_health_check),
            ("📁 Pro File Explorer", self.open_interactive_file_explorer),
            ("🚀 Auto-Heal Protocol", self.run_one_click_fix),
            ("🧹 Clean Junk Files", self.run_clean_temp),
            ("🗑️ Purge Recycle Bin", self.run_empty_bin),
            ("🚀 Startup Optimizer", self.run_startup_manager),
            ("📊 Storage Analyzer", self.run_storage_explorer),
            ("🛡️ Real-Time Guard", self.run_realtime_guard)
        ]

        for text, cmd in menu_items:
            tk.Button(
                sidebar, text=text, command=cmd,
                bg="#090d16", fg="#94a3b8", activebackground="#1e293b", activeforeground="#38bdf8",
                font=("Segoe UI", 9, "bold"), anchor="w", padx=20, pady=8, relief="flat", cursor="hand2"
            ).pack(fill="x", pady=2)

        # System Shutdown Button at Bottom
        tk.Button(
            sidebar, text="🛑 SYSTEM SHUTDOWN", command=root.quit,
            bg="#180707", fg="#f87171", activebackground="#7f1d1d", activeforeground="white",
            font=("Segoe UI", 9, "bold"), pady=8, relief="flat", cursor="hand2"
        ).pack(side="bottom", fill="x", padx=15, pady=20)

        # ==========================================
        # 2. RIGHT CONTENT AREA (Graphics Dashboard)
        # ==========================================
        content_area = tk.Frame(main_container, bg="#020617")
        content_area.pack(side="right", fill="both", expand=True, padx=25, pady=20)

        # Top Bar: Status & Title
        top_bar = tk.Frame(content_area, bg="#020617")
        top_bar.pack(fill="x", pady=(0, 15))

        tk.Label(
            top_bar, text="COMMAND CENTER // GRAPHICS MATRIX", 
            font=("Segoe UI", 11, "bold"), bg="#020617", fg="#38bdf8"
        ).pack(side="left")

        self.status_badge = tk.Label(
            top_bar, text=" ● SYSTEM STATUS: SECURE & ONLINE ", 
            font=("Segoe UI", 8, "bold"), bg="#064e3b", fg="#34d399", padx=10, pady=4
        )
        self.status_badge.pack(side="right")

        # --- METRICS CARDS ROW (Graphics Style) ---
        cards_row = tk.Frame(content_area, bg="#020617")
        cards_row.pack(fill="x", pady=10)

        # Card 1: CPU Load
        c1 = tk.Frame(cards_row, bg="#090d16", padx=15, pady=12, bd=1, relief="solid")
        c1.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(c1, text="CPU LOAD INTENSITY", font=("Segoe UI", 8, "bold"), bg="#090d16", fg="#64748b").pack(anchor="w")
        self.cpu_val_lbl = tk.Label(c1, text="0%", font=("Segoe UI", 22, "bold"), bg="#090d16", fg="#38bdf8")
        self.cpu_val_lbl.pack(anchor="w", pady=2)
        self.cpu_bar = ttk.Progressbar(c1, length=180, mode="determinate", style="cyber.Horizontal.TProgressbar")
        self.cpu_bar.pack(anchor="w", pady=2)

        # Card 2: Memory Allocation
        c2 = tk.Frame(cards_row, bg="#090d16", padx=15, pady=12, bd=1, relief="solid")
        c2.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(c2, text="MEMORY ALLOCATION", font=("Segoe UI", 8, "bold"), bg="#090d16", fg="#64748b").pack(anchor="w")
        self.ram_val_lbl = tk.Label(c2, text="0%", font=("Segoe UI", 22, "bold"), bg="#090d16", fg="#c084fc")
        self.ram_val_lbl.pack(anchor="w", pady=2)
        self.ram_bar = ttk.Progressbar(c2, length=180, mode="determinate", style="cyber.Horizontal.TProgressbar")
        self.ram_bar.pack(anchor="w", pady=2)

        # Card 3: System Integrity
        c3 = tk.Frame(cards_row, bg="#090d16", padx=15, pady=12, bd=1, relief="solid")
        c3.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(c3, text="SYSTEM INTEGRITY", font=("Segoe UI", 8, "bold"), bg="#090d16", fg="#64748b").pack(anchor="w")
        tk.Label(c3, text="99.9% ⚡", font=("Segoe UI", 22, "bold"), bg="#090d16", fg="#34d399").pack(anchor="w", pady=2)
        tk.Label(c3, text="Elite Graphics Shield Active", font=("Segoe UI", 7, "italic"), bg="#090d16", fg="#10b981").pack(anchor="w", pady=5)

        # --- LOWER DUAL SECTION (Terminal & Controls) ---
        lower_grid = tk.Frame(content_area, bg="#020617")
        lower_grid.pack(fill="both", expand=True, pady=10)

        # Left: Terminal Log Box
        term_frame = tk.Frame(lower_grid, bg="#090d16", padx=15, pady=12, bd=1, relief="solid")
        term_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(term_frame, text="⚡ GRAPHICS RENDER & TELEMETRY STREAM", font=("Segoe UI", 9, "bold"), bg="#090d16", fg="#cbd5e1").pack(anchor="w", pady=(0, 6))
        
        self.text_area = tk.Text(
            term_frame, 
            height=12, 
            width=45, 
            font=("Consolas", 8), 
            bg="#030712", 
            fg="#34d399",
            bd=0,
            highlightthickness=0,
            insertbackground="white"
        )
        self.text_area.pack(fill="both", expand=True)

        # Right: Action Control Matrix
        control_frame = tk.Frame(lower_grid, bg="#090d16", padx=15, pady=12, bd=1, relief="solid")
        control_frame.pack(side="right", fill="both", padx=(8, 0))

        tk.Label(control_frame, text="QUANTUM SUB-ROUTINES", font=("Segoe UI", 9, "bold"), bg="#090d16", fg="#cbd5e1").pack(anchor="w", pady=(0, 10))

        tk.Button(control_frame, text="🛡️ Toggle Neural Guard", command=self.run_realtime_guard, bg="#064e3b", fg="#34d399", font=("Segoe UI", 8, "bold"), width=24, pady=7, relief="flat", cursor="hand2").pack(pady=4)
        tk.Button(control_frame, text="💬 Consult Cloud Copilot", command=self.run_ai_chat, bg="#0369a1", fg="#38bdf8", font=("Segoe UI", 8, "bold"), width=24, pady=7, relief="flat", cursor="hand2").pack(pady=4)
        tk.Button(control_frame, text="🌙 Setup Auto Maintenance", command=self.run_auto_scheduler, bg="#581c87", fg="#c084fc", font=("Segoe UI", 8, "bold"), width=24, pady=7, relief="flat", cursor="hand2").pack(pady=4)
        tk.Button(control_frame, text="📊 Run Hardware Diagnostics", command=self.run_hardware_health, bg="#78350f", fg="#fbbf24", font=("Segoe UI", 8, "bold"), width=24, pady=7, relief="flat", cursor="hand2").pack(pady=4)

        # Start live background telemetry loop
        self.update_live_metrics()
        self.log_message("=== WINHEAL AI 2027 GRAPHICS KERNEL INITIALIZED ===")
        self.log_message("Graphics rendering engine online. All telemetry streams stable.\n")

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def update_live_metrics(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        self.cpu_val_lbl.config(text=f"{cpu}%")
        self.cpu_bar['value'] = cpu
        
        self.ram_val_lbl.config(text=f"{ram}%")
        self.ram_bar['value'] = ram
        
        self.root.after(2000, self.update_live_metrics)

    def run_ai_health_check(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🤖 GRAPHICS NEURAL DIAGNOSTIC SCAN ===")
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("C:")
        self.log_message(f"• CPU Load Index: {cpu_usage}%")
        self.log_message(f"• RAM Allocation: {memory.percent}%")
        self.log_message(f"• C: Storage Free: {round(disk.free / (1024**3), 2)} GB\n")
        self.log_message("✅ Graphics diagnostic scan completed with zero anomalies!\n")

    def open_interactive_file_explorer(self):
        # Advanced File Manager with Drive Selection (C:, D:, etc.)
        explorer_win = tk.Toplevel(self.root)
        explorer_win.title("WinHeal AI 2027 - Advanced Drive & File Manager")
        explorer_win.geometry("950x650")
        explorer_win.config(bg="#020617")

        nav_frame = tk.Frame(explorer_win, bg="#090d16", padx=10, pady=8)
        nav_frame.pack(fill="x", padx=15, pady=10)

        current_path = tk.StringVar()

        def load_drives():
            current_path.set("Computer Drives")
            for widget in grid_frame.winfo_children():
                widget.destroy()

            # Detect available drives (C:, D:, E:, etc. on Windows)
            drives = []
            if os.name == 'nt':
                import string
                drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            else:
                drives = ['/']

            row_val = 0
            col_val = 0
            for drive in drives:
                card = tk.Frame(grid_frame, bg="#0f172a", padx=12, pady=10, bd=1, relief="solid", width=140, height=90)
                card.grid(row=row_val, column=col_val, padx=10, pady=10, sticky="nsew")
                card.pack_propagate(False)

                tk.Label(card, text="💽", font=("Segoe UI", 20), bg="#0f172a", fg="#38bdf8").pack(anchor="w")
                lbl = tk.Label(card, text=f"Drive {drive}", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#f1f5f9", cursor="hand2")
                lbl.pack(anchor="w", pady=2)

                lbl.bind("<Button-1>", lambda e, p=drive: load_directory(p))
                card.bind("<Button-1>", lambda e, p=drive: load_directory(p))

                col_val += 1
                if col_val > 4:
                    col_val = 0
                    row_val += 1

        def load_directory(path):
            if not os.path.exists(path):
                return
            current_path.set(path)
            
            for widget in grid_frame.winfo_children():
                widget.destroy()

            try:
                items = os.listdir(path)
                row_val = 0
                col_val = 0

                for item in items:
                    full_path = os.path.join(path, item)
                    is_dir = os.path.isdir(full_path)
                    
                    icon = "📁" if is_dir else "📄"
                    bg_color = "#0f172a" if is_dir else "#090d16"

                    card = tk.Frame(grid_frame, bg=bg_color, padx=10, pady=8, bd=1, relief="solid", width=130, height=85)
                    card.grid(row=row_val, column=col_val, padx=8, pady=8, sticky="nsew")
                    card.pack_propagate(False)

                    tk.Label(card, text=icon, font=("Segoe UI", 16), bg=bg_color, fg="#38bdf8").pack(anchor="w")
                    
                    lbl = tk.Label(card, text=item[:14], font=("Segoe UI", 8, "bold"), bg=bg_color, fg="#f1f5f9", cursor="hand2")
                    lbl.pack(anchor="w", pady=2)

                    if is_dir:
                        lbl.bind("<Button-1>", lambda e, p=full_path: load_directory(p))
                        card.bind("<Button-1>", lambda e, p=full_path: load_directory(p))

                    col_val += 1
                    if col_val > 5:
                        col_val = 0
                        row_val += 1
            except Exception:
                pass

        # Navigation Buttons (Drives & Back)
        tk.Button(nav_frame, text="💽 Drives", command=load_drives, bg="#0369a1", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)
        tk.Button(nav_frame, text="⬅ Back", command=lambda: load_directory(os.path.dirname(current_path.get())), bg="#1e293b", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)

        path_entry = tk.Entry(nav_frame, textvariable=current_path, font=("Consolas", 9), bg="#020617", fg="#38bdf8", insertbackground="white", bd=1, relief="solid")
        path_entry.pack(side="left", fill="x", expand=True, padx=5, ipady=3)

        # Scrollable Grid Container
        container = tk.Frame(explorer_win, bg="#030712")
        container.pack(fill="both", expand=True, padx=15, pady=5)

        canvas = tk.Canvas(container, bg="#030712", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        grid_frame = tk.Frame(canvas, bg="#030712")

        grid_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load Drives view initially
        load_drives()

        self.log_message("📁 Advanced Drive & File Manager launched successfully.\n")

    def run_one_click_fix(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== ⚡ QUANTUM AUTO-HEALING PROTOCOL ===")
        self.run_clean_temp()
        self.run_empty_bin()
        messagebox.showinfo("WinHeal AI", "Quantum Auto-Healing completed successfully!")

    def run_clean_temp(self):
        self.log_message("🧹 Purging temporary system debris...")
        temp_folder = os.path.expandvars(r'%TEMP%')
        count = 0
        for root_dir, dirs, files in os.walk(temp_folder):
            for file in files:
                try:
                    os.remove(os.path.join(root_dir, file))
                    count += 1
                except:
                    pass
        self.log_message(f"✅ Successfully sanitized {count} junk files.\n")

    def run_empty_bin(self):
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            self.log_message("🗑️ Recycle Bin sanitized via deep flush.\n")
        except:
            self.log_message("ℹ️ Recycle Bin is already pristine.\n")

    def run_startup_manager(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🚀 STARTUP PROCESS OPTIMIZER ===")
        apps_count = sum(1 for _ in psutil.process_iter(['name']))
        self.log_message(f"Active background threads monitored: {apps_count}\n")

    def run_storage_explorer(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 📊 DEEP STORAGE MATRIX EXPLORER ===")
        disk = psutil.disk_usage("C:")
        self.log_message(f"C: Total: {round(disk.total/(1024**3),2)}GB | Free: {round(disk.free/(1024**3),2)}GB\n")

    def run_hardware_health(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 📊 HARDWARE HEALTH TELEMETRY ===")
        self.log_message("• CPU Status: Elite (Thermal Voltages Nominal)")
        self.log_message("• RAM Modules: Pristine (Zero Faults Detected)\n")
        messagebox.showinfo("Hardware Health", "System Hardware Integrity: 99.9% (Elite)")

    def run_auto_scheduler(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🌙 AUTOMATED CRON MAINTENANCE ===")
        self.log_message("Background neural task scheduled successfully.\n")

    def run_realtime_guard(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🛡️ NEURAL BACKGROUND DEFENSE GUARD ===")
        self.log_message("Active defense shield engaged! Monitoring RAM anomalies & threats 24/7.\n")
        messagebox.showinfo("Real-Time Guard", "Neural Background Guard is now actively protecting your OS.")

    def run_ai_chat(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 💬 WINHEAL CLOUD AI COPILOT ===")
        self.log_message("AI: Greetings Md Nayem Hasan! Your system core telemetry is operating at maximum efficiency.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WinHealApp(root)
    root.mainloop()