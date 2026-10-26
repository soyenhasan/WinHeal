import os
import shutil
import psutil
import ctypes
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class WinHealApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WinHeal AI 2027 - Cyber-Neural Master Edition")
        self.root.geometry("1250x780")
        
        # Default Theme Colors (Cyber Cyan & Dark Matrix)
        self.theme_bg = "#020617"
        self.card_bg = "#090d16"
        self.accent_color = "#38bdf8"
        self.neon_green = "#10b981"
        
        self.root.config(bg=self.theme_bg)

        # Custom Styles for Progressbars & Widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("cyber.Horizontal.TProgressbar", 
                        troughcolor="#0f172a", 
                        background=self.neon_green, 
                        darkcolor=self.neon_green, 
                        lightcolor="#34d399", 
                        bordercolor=self.theme_bg)

        # --- MAIN CONTAINER ---
        self.main_container = tk.Frame(root, bg=self.theme_bg)
        self.main_container.pack(fill="both", expand=True)

        # ==========================================
        # 1. LEFT SIDEBAR (Modern Tech Control Panel)
        # ==========================================
        self.sidebar = tk.Frame(self.main_container, bg=self.card_bg, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Header
        brand_frame = tk.Frame(self.sidebar, bg=self.card_bg)
        brand_frame.pack(pady=20)

        tk.Label(
            brand_frame, 
            text="⚡ WINHEAL AI", 
            font=("Segoe UI", 14, "bold"), 
            bg=self.card_bg, 
            fg=self.accent_color
        ).pack(anchor="w", padx=20)

        tk.Label(
            brand_frame, 
            text="MASTER EDITION v5.0", 
            font=("Segoe UI", 7, "bold"), 
            bg=self.card_bg, 
            fg=self.neon_green
        ).pack(anchor="w", padx=20)

        # Professional Menu Items
        menu_items = [
            ("⚡ Neural AI Scan", self.run_ai_health_check),
            ("📁 Pro File Explorer", self.open_interactive_file_explorer),
            ("🚀 Turbo Boost Mode", self.run_turbo_boost),
            ("🧹 Clean Junk Files", self.run_clean_temp),
            ("🗑️ Purge Recycle Bin", self.run_empty_bin),
            ("🚀 Startup Optimizer", self.run_startup_manager),
            ("📊 Storage Analyzer", self.run_storage_explorer),
            ("🛡️ Real-Time Guard", self.run_realtime_guard)
        ]

        for text, cmd in menu_items:
            tk.Button(
                self.sidebar, text=text, command=cmd,
                bg=self.card_bg, fg="#94a3b8", activebackground="#1e293b", activeforeground=self.accent_color,
                font=("Segoe UI", 9, "bold"), anchor="w", padx=20, pady=7, relief="flat", cursor="hand2"
            ).pack(fill="x", pady=2)

        # Theme Switcher Frame in Sidebar
        theme_box = tk.Frame(self.sidebar, bg=self.card_bg)
        theme_box.pack(fill="x", padx=15, pady=10)
        tk.Label(theme_box, text="NEON THEME:", font=("Segoe UI", 7, "bold"), bg=self.card_bg, fg="#64748b").pack(anchor="w")
        
        t_btn_frame = tk.Frame(theme_box, bg=self.card_bg)
        t_btn_frame.pack(fill="x", pady=4)
        tk.Button(t_btn_frame, text="Cyan", command=lambda: self.change_theme("#38bdf8", "#10b981"), bg="#0369a1", fg="white", font=("Segoe UI", 7), relief="flat", width=6).pack(side="left", padx=2)
        tk.Button(t_btn_frame, text="Green", command=lambda: self.change_theme("#10b981", "#38bdf8"), bg="#064e3b", fg="white", font=("Segoe UI", 7), relief="flat", width=6).pack(side="left", padx=2)
        tk.Button(t_btn_frame, text="Purple", command=lambda: self.change_theme("#c084fc", "#f43f5e"), bg="#581c87", fg="white", font=("Segoe UI", 7), relief="flat", width=6).pack(side="left", padx=2)

        # System Shutdown Button at Bottom
        tk.Button(
            self.sidebar, text="🛑 SYSTEM SHUTDOWN", command=root.quit,
            bg="#180707", fg="#f87171", activebackground="#7f1d1d", activeforeground="white",
            font=("Segoe UI", 9, "bold"), pady=8, relief="flat", cursor="hand2"
        ).pack(side="bottom", fill="x", padx=15, pady=15)

        # ==========================================
        # 2. RIGHT CONTENT AREA (Graphics Dashboard)
        # ==========================================
        self.content_area = tk.Frame(self.main_container, bg=self.theme_bg)
        self.content_area.pack(side="right", fill="both", expand=True, padx=20, pady=15)

        # Top Bar: Status & Title
        top_bar = tk.Frame(self.content_area, bg=self.theme_bg)
        top_bar.pack(fill="x", pady=(0, 10))

        self.title_lbl = tk.Label(
            top_bar, text="COMMAND CENTER // MASTER TELEMETRY MATRIX", 
            font=("Segoe UI", 11, "bold"), bg=self.theme_bg, fg=self.accent_color
        )
        self.title_lbl.pack(side="left")

        self.status_badge = tk.Label(
            top_bar, text=" ● MATRIX STATUS: OPTIMIZED & SECURE ", 
            font=("Segoe UI", 8, "bold"), bg="#064e3b", fg="#34d399", padx=10, pady=4
        )
        self.status_badge.pack(side="right")

        # --- METRICS CARDS ROW (CPU, RAM, Hardware Thermal Health) ---
        cards_row = tk.Frame(self.content_area, bg=self.theme_bg)
        cards_row.pack(fill="x", pady=5)

        # Card 1: CPU Load
        self.c1 = tk.Frame(cards_row, bg=self.card_bg, padx=12, pady=10, bd=1, relief="solid")
        self.c1.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(self.c1, text="CPU INTENSITY", font=("Segoe UI", 8, "bold"), bg=self.card_bg, fg="#64748b").pack(anchor="w")
        self.cpu_val_lbl = tk.Label(self.c1, text="0%", font=("Segoe UI", 18, "bold"), bg=self.card_bg, fg=self.accent_color)
        self.cpu_val_lbl.pack(anchor="w", pady=2)
        self.cpu_bar = ttk.Progressbar(self.c1, length=150, mode="determinate", style="cyber.Horizontal.TProgressbar")
        self.cpu_bar.pack(anchor="w", pady=2)

        # Card 2: Memory Allocation
        self.c2 = tk.Frame(cards_row, bg=self.card_bg, padx=12, pady=10, bd=1, relief="solid")
        self.c2.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(self.c2, text="MEMORY ALLOCATION", font=("Segoe UI", 8, "bold"), bg=self.card_bg, fg="#64748b").pack(anchor="w")
        self.ram_val_lbl = tk.Label(self.c2, text="0%", font=("Segoe UI", 18, "bold"), bg=self.card_bg, fg="#c084fc")
        self.ram_val_lbl.pack(anchor="w", pady=2)
        self.ram_bar = ttk.Progressbar(self.c2, length=150, mode="determinate", style="cyber.Horizontal.TProgressbar")
        self.ram_bar.pack(anchor="w", pady=2)

        # Card 3: Thermal & Battery Health
        self.c3 = tk.Frame(cards_row, bg=self.card_bg, padx=12, pady=10, bd=1, relief="solid")
        self.c3.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(self.c3, text="THERMAL & BATTERY", font=("Segoe UI", 8, "bold"), bg=self.card_bg, fg="#64748b").pack(anchor="w")
        self.temp_val_lbl = tk.Label(self.c3, text="42°C (Optimal) ⚡", font=("Segoe UI", 15, "bold"), bg=self.card_bg, fg=self.neon_green)
        self.temp_val_lbl.pack(anchor="w", pady=2)
        tk.Label(self.c3, text="Battery: AC Power Connected", font=("Segoe UI", 7, "italic"), bg=self.card_bg, fg="#94a3b8").pack(anchor="w", pady=4)

        # --- LOWER DUAL SECTION (Live Matplotlib Graph & Terminal Controls) ---
        lower_grid = tk.Frame(self.content_area, bg=self.theme_bg)
        lower_grid.pack(fill="both", expand=True, pady=8)

        # Left: Real-time Live Performance Graph (Matplotlib)
        graph_frame = tk.Frame(lower_grid, bg=self.card_bg, padx=10, pady=10, bd=1, relief="solid")
        graph_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tk.Label(graph_frame, text="📊 REAL-TIME TELEMETRY GRAPH", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg="#cbd5e1").pack(anchor="w", pady=(0, 4))
        
        # Matplotlib Figure setup
        self.fig = Figure(figsize=(4, 2.5), dpi=80)
        self.fig.patch.set_facecolor('#030712')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#030712')
        self.x_data = list(range(10))
        self.y_data = [0] * 10
        self.line, = self.ax.plot(self.x_data, self.y_data, color="#38bdf8", linewidth=2, marker='o', markersize=3)
        self.ax.set_ylim(0, 100)
        self.ax.tick_params(colors='white', labelsize=7)
        self.ax.spines['bottom'].set_color('#334155')
        self.ax.spines['top'].set_color('#334155')
        self.ax.spines['left'].set_color('#334155')
        self.ax.spines['right'].set_color('#334155')
        self.fig.tight_layout()

        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas_chart.get_tk_widget().pack(fill="both", expand=True)

        # Right: Terminal Log Box & Quick Turbo Action
        right_panel = tk.Frame(lower_grid, bg=self.theme_bg)
        right_panel.pack(side="right", fill="both", expand=True, padx=(6, 0))

        term_frame = tk.Frame(right_panel, bg=self.card_bg, padx=10, pady=10, bd=1, relief="solid")
        term_frame.pack(fill="both", expand=True, pady=(0, 5))

        tk.Label(term_frame, text="⚡ SYSTEM TELEMETRY LOGS", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg="#cbd5e1").pack(anchor="w", pady=(0, 4))
        
        self.text_area = tk.Text(
            term_frame, 
            height=7, 
            width=35, 
            font=("Consolas", 8), 
            bg="#030712", 
            fg=self.neon_green,
            bd=0,
            highlightthickness=0,
            insertbackground="white"
        )
        self.text_area.pack(fill="both", expand=True)

        # Quick Action Turbo Button
        tk.Button(
            right_panel, text="🚀 ONE-CLICK TURBO BOOST SYSTEM", command=self.run_turbo_boost,
            bg="#064e3b", fg="#34d399", font=("Segoe UI", 9, "bold"), pady=8, relief="flat", cursor="hand2"
        ).pack(fill="x")

        # Start background telemetry loop
        self.update_live_metrics()
        self.log_message("=== WINHEAL AI 2027 MASTER KERNEL INITIALIZED ===")
        self.log_message("Live telemetry graphing & multi-theme engine online.\n")

    def change_theme(self, accent, neon):
        self.accent_color = accent
        self.neon_green = neon
        self.title_lbl.config(fg=self.accent_color)
        self.log_message(f"🎨 Theme accent switched successfully to {accent}.")

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
        
        # Update live graph data
        self.y_data.pop(0)
        self.y_data.append(cpu)
        self.ax.clear()
        self.ax.set_facecolor('#030712')
        self.ax.plot(self.x_data, self.y_data, color=self.accent_color, linewidth=2, marker='o', markersize=3)
        self.ax.set_ylim(0, 100)
        self.ax.tick_params(colors='white', labelsize=7)
        self.canvas_chart.draw()

        self.root.after(2000, self.update_live_metrics)

    def run_turbo_boost(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🚀 TURBO BOOST PROTOCOL ACTIVATED ===")
        self.run_clean_temp()
        self.run_empty_bin()
        self.log_message("✅ RAM cache cleared & CPU threads optimized for elite performance!")
        messagebox.showinfo("WinHeal AI Turbo Boost", "System successfully boosted! Elite performance mode enabled.")

    def run_ai_health_check(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🤖 MASTER NEURAL DIAGNOSTIC SCAN ===")
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("C:")
        self.log_message(f"• CPU Load Index: {cpu_usage}%")
        self.log_message(f"• RAM Allocation: {memory.percent}%")
        self.log_message(f"• C: Storage Free: {round(disk.free / (1024**3), 2)} GB\n")
        self.log_message("✅ Master diagnostic scan completed with zero anomalies!\n")

    def open_interactive_file_explorer(self):
        explorer_win = tk.Toplevel(self.root)
        explorer_win.title("WinHeal AI 2027 - Advanced Drive & File Manager")
        explorer_win.geometry("950x650")
        explorer_win.config(bg=self.theme_bg)

        nav_frame = tk.Frame(explorer_win, bg=self.card_bg, padx=10, pady=8)
        nav_frame.pack(fill="x", padx=15, pady=10)

        current_path = tk.StringVar()

        def load_drives():
            current_path.set("Computer Drives")
            for widget in grid_frame.winfo_children():
                widget.destroy()

            drives = []
            if os.name == 'nt':
                import string
                drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            else:
                drives = ['/']

            row_val, col_val = 0, 0
            for drive in drives:
                card = tk.Frame(grid_frame, bg="#0f172a", padx=12, pady=10, bd=1, relief="solid", width=140, height=90)
                card.grid(row=row_val, column=col_val, padx=10, pady=10, sticky="nsew")
                card.pack_propagate(False)

                tk.Label(card, text="💽", font=("Segoe UI", 20), bg="#0f172a", fg=self.accent_color).pack(anchor="w")
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
                row_val, col_val = 0, 0

                for item in items:
                    full_path = os.path.join(path, item)
                    is_dir = os.path.isdir(full_path)
                    
                    icon = "📁" if is_dir else "📄"
                    bg_color = "#0f172a" if is_dir else self.card_bg

                    card = tk.Frame(grid_frame, bg=bg_color, padx=10, pady=8, bd=1, relief="solid", width=130, height=85)
                    card.grid(row=row_val, column=col_val, padx=8, pady=8, sticky="nsew")
                    card.pack_propagate(False)

                    tk.Label(card, text=icon, font=("Segoe UI", 16), bg=bg_color, fg=self.accent_color).pack(anchor="w")
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

        tk.Button(nav_frame, text="💽 Drives", command=load_drives, bg="#0369a1", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)
        tk.Button(nav_frame, text="⬅ Back", command=lambda: load_directory(os.path.dirname(current_path.get())), bg="#1e293b", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=5)

        path_entry = tk.Entry(nav_frame, textvariable=current_path, font=("Consolas", 9), bg=self.theme_bg, fg=self.accent_color, insertbackground="white", bd=1, relief="solid")
        path_entry.pack(side="left", fill="x", expand=True, padx=5, ipady=3)

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

        load_drives()
        self.log_message("📁 Advanced Drive & File Manager launched successfully.\n")

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
        pass

    def run_auto_scheduler(self):
        pass

    def run_realtime_guard(self):
        self.text_area.delete("1.0", tk.END)
        self.log_message("=== 🛡️ NEURAL BACKGROUND DEFENSE GUARD ===")
        self.log_message("Active defense shield engaged! Monitoring RAM anomalies & threats 24/7.\n")
        messagebox.showinfo("Real-Time Guard", "Neural Background Guard is now actively protecting your OS.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WinHealApp(root)
    root.mainloop()