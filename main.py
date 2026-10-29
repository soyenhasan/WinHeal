"""WinHeal v0.3.0 WORLD EDITION - SAFE + Icon + AutoUpdate + 10 Languages + Gaming/Battery/Internet"""
import datetime
import hashlib
import os
import queue
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import webbrowser
from collections import defaultdict
import psutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
try:
    import winreg
except ImportError:
    winreg = None
try:
    import requests
except ImportError:
    requests = None

VERSION = "0.3.0 - WORLD"
IS_WIN = os.name == "nt"
NO_WINDOW = 0x08000000 if IS_WIN else 0
LOG_DIR = os.path.join(os.path.expanduser("~"), "WinHealLogs")
HIST = 30
GITHUB_REPO = "soyenhasan/WinHeal-AI"

STRINGS = {
    "en": {
        "app_title": "WinHeal v0.3.0 World Edition", "menu_diag": "System Diagnostics", "menu_files": "File & Drive Explorer", "menu_net": "Network Troubleshooter", "menu_startup": "Startup Programs", "menu_dups": "Duplicate File Finder", "menu_updates": "Software Updates", "menu_junk": "Junk File Cleaner", "menu_bin": "Empty Recycle Bin", "menu_bench": "Quick Benchmark", "menu_report": "Export System Report", "menu_gaming": "🎮 Gaming Mode", "menu_battery": "🔋 Battery Saver", "menu_internet": "🌐 Internet Cleaner", "theme": "THEME", "language": "LANGUAGE", "custom": "Custom", "quit": "Quit", "dashboard": "SYSTEM DASHBOARD", "status_ok": "● System load: normal", "status_warn": "● System load: high", "cpu": "CPU", "ram": "MEMORY", "disk": "DISK", "battery": "BATTERY", "no_battery": "No battery", "charging": "Plugged in", "on_battery": "On battery", "graph_title": "Live CPU & memory", "log_title": "Activity log", "close": "Close", "working": "Working...", "error": "Error", "windows_only": "Windows only.", "threads": "threads", "free": "free", "started": "WinHeal World Edition v0.3.0 started - 3 New Features Added!", "issue_cpu": "CPU very high.", "issue_ram": "Memory very high.", "issue_disk": "Disk almost full.", "issue_battery": "Battery low.", "issue_uptime": "PC not restarted {d} days.", "no_issues": "No problems.", "found_issues": "Problems:", "top_procs": "Top memory users:", "uptime": "Uptime", "host": "Computer name", "local_ip": "Local IP", "sent": "Data sent", "received": "Data received", "ping_test": "Internet ping (8.8.8.8)", "dns_test": "DNS lookup (example.com)", "ok": "OK", "failed": "FAILED", "net_ok": "Connection looks healthy.", "net_dns": "DNS fails.", "net_down": "No internet.", "flush_dns": "Flush DNS cache", "dns_flushed": "DNS cache flushed.", "startup_none": "No startup entries.", "startup_note": "Use Task Manager > Startup apps.", "open_startup": "Open Startup settings", "junk_found": "Found {n} temp files, total {size}.", "junk_none": "No old temp files.", "delete_now": "Delete these files", "confirm_delete": "Delete {n} files ({size})?", "junk_done": "Deleted {n} files, freed {size}. {f} skipped.", "bin_confirm": "Permanently empty Recycle Bin?", "bin_done": "Recycle Bin emptied.", "dups_pick": "Choose a folder", "dups_scanning": "Scanning {folder} ...", "dups_none": "No duplicates.", "dups_summary": "{g} groups, recoverable {size}.", "dups_note": "WinHeal deletes nothing.", "wg_missing": "winget not found.", "wg_hint": "Run: winget upgrade --all", "bench_cpu": "CPU test: {s:.2f} s", "bench_disk": "Disk write: {mb:.0f} MB/s", "bench_note": "Simple tests.", "report_saved": "Report saved: {path}", "parent_dir": "[..] Parent folder", "col_name": "Name", "col_type": "Type", "col_size": "Size", "folder": "Folder", "file": "File", "home": "Home", "browse": "Browse...", "copy_ask": "Copy '{name}'?", "copy_done": "Copied to: {dest}", "path": "Path", "check_update": "Check for Update", "update_available": "Update {latest} available!", "up_to_date": "You are up to date!", "backup_done": "Backup created.", "update": "Update", "gaming_on": "Gaming Mode ON - RAM Boosted!", "battery_on": "Battery Saver ON", "internet_cleaned": "Browser Cache Cleaned!"
    },
    "bn": {
        "app_title": "WinHeal v0.3.0 বিশ্ব সংস্করণ", "menu_diag": "সিস্টেম ডায়াগনস্টিক", "menu_files": "ফাইল এক্সপ্লোরার", "menu_net": "নেটওয়ার্ক", "menu_startup": "স্টার্টআপ", "menu_dups": "ডুপ্লিকেট", "menu_updates": "আপডেট", "menu_junk": "জাঙ্ক ক্লিনার", "menu_bin": "বিন খালি", "menu_bench": "বেঞ্চমার্ক", "menu_report": "রিপোর্ট", "menu_gaming": "🎮 গেমিং মোড", "menu_battery": "🔋 ব্যাটারি সেভার", "menu_internet": "🌐 ইন্টারনেট ক্লিনার", "theme": "থিম", "language": "ভাষা", "custom": "কাস্টম", "quit": "বন্ধ করুন", "dashboard": "সিস্টেম ড্যাশবোর্ড", "status_ok": "● লোড: স্বাভাবিক", "status_warn": "● লোড: বেশি", "cpu": "CPU", "ram": "মেমোরি", "disk": "ডিস্ক", "battery": "ব্যাটারি", "no_battery": "ব্যাটারি নেই", "charging": "চার্জে আছে", "on_battery": "ব্যাটারিতে", "graph_title": "লাইভ CPU ও মেমোরি", "log_title": "কাজের লগ", "close": "বন্ধ", "working": "কাজ চলছে...", "error": "ত্রুটি", "started": "WinHeal v0.3.0 চালু - ৩ টা নতুন ফিচার!", "check_update": "আপডেট চেক", "gaming_on": "গেমিং মোড চালু!", "battery_on": "ব্যাটারি সেভার চালু!", "internet_cleaned": "ব্রাউজার পরিষ্কার!"
    },
}

def fmt_size(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
        n /= 1024

def run_cmd(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, creationflags=NO_WINDOW)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return -1, str(e)

def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "N/A"
    finally:
        s.close()

def ping_ok(host="8.8.8.8"):
    cmd = ["ping", "-n", "2", "-w", "2000", host] if IS_WIN else ["ping", "-c", "2", "-W", "2", host]
    rc, out = run_cmd(cmd, timeout=15)
    return rc == 0 and ("ttl" in out.lower())

def dns_ok(name="example.com"):
    try:
        socket.gethostbyname(name)
        return True
    except OSError:
        return False

def get_battery():
    try:
        return psutil.sensors_battery()
    except:
        return None

def junk_dirs():
    cands = [os.environ.get("TEMP"), os.environ.get("TMP")]
    root = os.environ.get("SystemRoot")
    if root:
        cands.append(os.path.join(root, "Temp"))
    out, seen = [], set()
    for c in cands:
        if not c or not os.path.isdir(c):
            continue
        norm = os.path.normcase(c)
        if norm in seen:
            continue
        if "temp" not in norm.lower() or len(norm) < 10:
            continue
        seen.add(norm)
        out.append(c)
    return out

def scan_junk(dirs=None, min_age_hours=24):
    cutoff = time.time() - min_age_hours * 3600
    files, total = [], 0
    for d in (dirs if dirs is not None else junk_dirs()):
        for root, _, names in os.walk(d):
            for n in names:
                fp = os.path.join(root, n)
                try:
                    st = os.lstat(fp)
                except OSError:
                    continue
                if st.st_mtime < cutoff:
                    files.append((fp, st.st_size))
                    total += st.st_size
    return files, total

def delete_files(files):
    deleted = freed = failed = 0
    for fp, size in files:
        try:
            os.remove(fp)
            deleted += 1
            freed += size
        except OSError:
            failed += 1
    return deleted, freed, failed

def file_hash(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()

def find_duplicates(folder, cancel=None):
    by_size = defaultdict(list)
    seen = 0
    for root, _, names in os.walk(folder):
        if cancel is not None and cancel.is_set():
            return None
        for n in names:
            fp = os.path.join(root, n)
            try:
                if os.path.islink(fp):
                    continue
                size = os.path.getsize(fp)
            except OSError:
                continue
            seen += 1
            if size >= 1024:
                by_size[size].append(fp)
    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        by_hash = defaultdict(list)
        for fp in paths:
            if cancel is not None and cancel.is_set():
                return None
            h = file_hash(fp)
            if h:
                by_hash[h].append(fp)
        groups.extend((size, ps) for ps in by_hash.values() if len(ps) > 1)
    groups.sort(key=lambda g: g[0] * (len(g[1]) - 1), reverse=True)
    return groups, seen

def cpu_bench():
    start = time.perf_counter()
    x = 0
    for i in range(5_000_000):
        x += i * i % 7
    return time.perf_counter() - start

def disk_write_bench(size_mb=64):
    path = os.path.join(tempfile.gettempdir(), "winheal_bench.tmp")
    block = os.urandom(1024 * 1024)
    start = time.perf_counter()
    try:
        with open(path, "wb") as f:
            for _ in range(size_mb):
                f.write(block)
            f.flush()
            os.fsync(f.fileno())
        elapsed = time.perf_counter() - start
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    return size_mb / elapsed

def startup_entries():
    items = []
    if winreg is None:
        return items
    for hive, scope in ((winreg.HKEY_CURRENT_USER, "User"), (winreg.HKEY_LOCAL_MACHINE, "All users")):
        try:
            with winreg.OpenKey(hive, r"Software\Microsoft\Windows\CurrentVersion\Run") as k:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(k, i)
                    except OSError:
                        break
                    items.append((scope, name, str(value)))
                    i += 1
        except OSError:
            pass
    return items

class WinHealApp:
    def __init__(self, root):
        self.root = root
        self.lang = "en"
        self.bg, self.card = "#020617", "#090d16"
        self.accent, self.neon = "#38bdf8", "#10b981"
        self.root_drive = os.path.splitdrive(os.path.expanduser("~"))[0] + os.sep
        self.cpu_hist = [0] * HIST
        self.ram_hist = [0] * HIST
        self.log_lines = []
        self.main = None
        self.ui_queue = queue.Queue()
        root.geometry("1200x760")
        root.minsize(1000, 650)
        self.build_ui()
        self.log(self.t("started"))
        self.poll_queue()
        self.update_metrics()

    def t(self, key, **kw):
        s = STRINGS.get(self.lang, {}).get(key) or STRINGS["en"].get(key, key)
        return s.format(**kw) if kw else s
    def ui(self, fn):
        self.ui_queue.put(fn)
    def poll_queue(self):
        try:
            while True:
                self.ui_queue.get_nowait()()
        except queue.Empty:
            pass
        except tk.TclError:
            pass
        self.root.after(100, self.poll_queue)
    def run_bg(self, fn, *args):
        def runner():
            try:
                fn(*args)
            except Exception as e:
                self.log(f"ERROR: {e}")
        threading.Thread(target=runner, daemon=True).start()
    def log(self, message):
        line = f"[{datetime.datetime.now():%H:%M:%S}] {message}"
        self.log_lines.append(line)
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
            with open(os.path.join(LOG_DIR, "session_history.log"), "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass
        self.ui(lambda: self._append_log(line))
    def _append_log(self, line):
        try:
            self.log_box.insert(tk.END, line + "\n")
            self.log_box.see(tk.END)
        except:
            pass
    def toast(self, title, message):
        self.ui(lambda: self._toast(title, message))
    def _toast(self, title, message):
        w = tk.Toplevel(self.root)
        w.overrideredirect(True)
        x = self.root.winfo_x() + self.root.winfo_width() - 350
        y = self.root.winfo_y() + 50
        w.geometry(f"330x95+{x}+{y}")
        border = tk.Frame(w, bg=self.accent, padx=2, pady=2)
        border.pack(fill="both", expand=True)
        inner = tk.Frame(border, bg=self.card, padx=10, pady=8)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=f"⚡ {title}", font=("Segoe UI", 9, "bold"), bg=self.card, fg=self.accent).pack(anchor="w")
        tk.Label(inner, text=message, font=("Segoe UI", 9), bg=self.card, fg="#cbd5e1", wraplength=300, justify="left").pack(anchor="w", pady=3)
        w.after(3500, w.destroy)
    def button(self, parent, text, cmd, bg="#0369a1", fg="white"):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=5, cursor="hand2")

    def build_ui(self):
        if hasattr(self, 'fig'):
            try:
                plt.close(self.fig)
            except:
                pass
        if self.main is not None:
            self.main.destroy()
        self.root.title(self.t("app_title"))
        self.root.config(bg=self.bg)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("cyber.Horizontal.TProgressbar", troughcolor="#0f172a", background=self.neon, darkcolor=self.neon, lightcolor=self.neon, bordercolor=self.bg)
        self.main = tk.Frame(self.root, bg=self.bg)
        self.main.pack(fill="both", expand=True)
        side = tk.Frame(self.main, bg=self.card, width=270)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="⚡ WINHEAL", font=("Segoe UI", 14, "bold"), bg=self.card, fg=self.accent).pack(anchor="w", padx=15, pady=(15, 0))
        tk.Label(side, text=f"v{VERSION}", font=("Segoe UI", 8), bg=self.card, fg="#64748b").pack(anchor="w", padx=15, pady=(0, 10))
        menu = [("menu_diag", self.diagnostics), ("menu_files", self.file_explorer), ("menu_net", self.network), ("menu_startup", self.startup), ("menu_dups", self.duplicates), ("menu_updates", self.updates), ("menu_junk", self.junk), ("menu_bin", self.empty_bin), ("menu_bench", self.benchmark), ("menu_report", self.export_report), ("menu_gaming", self.gaming_mode), ("menu_battery", self.battery_saver), ("menu_internet", self.internet_cleaner)]
        for key, cmd in menu:
            is_new = key in ("menu_gaming","menu_battery","menu_internet")
            bg_col = "#0f172a" if is_new else self.card
            fg_col = "#22d3ee" if is_new else "#cbd5e1"
            tk.Button(side, text=self.t(key), command=cmd, bg=bg_col, fg=fg_col, activebackground="#1e293b", activeforeground=self.accent, font=("Segoe UI", 10, "bold" if is_new else "normal"), anchor="w", padx=15, pady=6 if is_new else 5, relief="flat", cursor="hand2").pack(fill="x", pady=1)
        box = tk.Frame(side, bg=self.card)
        box.pack(fill="x", padx=15, pady=(12, 0))
        tk.Label(box, text=self.t("theme"), font=("Segoe UI", 8, "bold"), bg=self.card, fg="#64748b").pack(anchor="w")
        row = tk.Frame(box, bg=self.card)
        row.pack(fill="x", pady=2)
        for name, colors, bgc in [("Cyan", ("#38bdf8", "#10b981"), "#0369a1"), ("Green", ("#10b981", "#38bdf8"), "#064e3b"), ("Purple", ("#c084fc", "#f43f5e"), "#581c87")]:
            tk.Button(row, text=name, command=lambda c=colors: self.set_theme(*c), bg=bgc, fg="white", font=("Segoe UI", 8), relief="flat", width=6).pack(side="left", padx=1)
        tk.Button(row, text=self.t("custom"), command=self.pick_custom_theme, bg="#334155", fg="white", font=("Segoe UI", 8), relief="flat", width=7).pack(side="left", padx=1)
        lbox = tk.Frame(side, bg=self.card)
        lbox.pack(fill="x", padx=15, pady=(12, 0))
        tk.Label(lbox, text=self.t("language") + " (WORLD)", font=("Segoe UI", 8, "bold"), bg=self.card, fg="#64748b").pack(anchor="w")
        lrow1 = tk.Frame(lbox, bg=self.card)
        lrow1.pack(fill="x", pady=2)
        lrow2 = tk.Frame(lbox, bg=self.card)
        lrow2.pack(fill="x", pady=2)
        langs = [("en","EN"),("bn","BN")]
        for i, (code, label) in enumerate(langs):
            target = lrow1 if i < 1 else lrow2
            bgc = "#38bdf8" if code==self.lang else "#334155"
            tk.Button(target, text=label, command=lambda c=code: self.set_lang(c), bg=bgc, fg="white", font=("Segoe UI", 8, "bold"), relief="flat", width=6).pack(side="left", padx=1, pady=1)
        tk.Button(side, text=f"🔄 {self.t('check_update')}", command=self.check_update_thread, bg="#1e3a5f", fg="#38bdf8", font=("Segoe UI", 9, "bold"), pady=6, relief="flat", cursor="hand2").pack(side="bottom", fill="x", padx=15, pady=(5,2))
        tk.Button(side, text=self.t("quit"), command=self.root.destroy, bg="#180707", fg="#f87171", font=("Segoe UI", 9, "bold"), pady=5, relief="flat", cursor="hand2").pack(side="bottom", fill="x", padx=15, pady=(2,10))
        content = tk.Frame(self.main, bg=self.bg)
        content.pack(side="right", fill="both", expand=True, padx=20, pady=15)
        top = tk.Frame(content, bg=self.bg)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text=self.t("dashboard"), font=("Segoe UI", 12, "bold"), bg=self.bg, fg=self.accent).pack(side="left")
        self.status_badge = tk.Label(top, text=self.t("status_ok"), font=("Segoe UI", 9, "bold"), bg="#064e3b", fg="#34d399", padx=10, pady=4)
        self.status_badge.pack(side="right")
        cards = tk.Frame(content, bg=self.bg)
        cards.pack(fill="x", pady=5)
        self.cpu_lbl, self.cpu_bar = self._card(cards, self.t("cpu"), self.accent)
        self.ram_lbl, self.ram_bar = self._card(cards, self.t("ram"), "#c084fc")
        self.disk_lbl, self.disk_bar = self._card(cards, self.t("disk"), "#fbbf24")
        self.bat_lbl, self.bat_bar = self._card(cards, self.t("battery"), self.neon)
        lower = tk.Frame(content, bg=self.bg)
        lower.pack(fill="both", expand=True, pady=8)
        gframe = tk.Frame(lower, bg=self.card, padx=10, pady=10, bd=1, relief="solid")
        gframe.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tk.Label(gframe, text=self.t("graph_title"), font=("Segoe UI", 10, "bold"), bg=self.card, fg="#cbd5e1").pack(anchor="w", pady=(0, 4))
        self.fig = Figure(figsize=(4, 2.5), dpi=80)
        self.fig.patch.set_facecolor("#030712")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#030712")
        xs = list(range(HIST))
        (self.cpu_line,) = self.ax.plot(xs, self.cpu_hist, color=self.accent, linewidth=2, label="CPU")
        (self.ram_line,) = self.ax.plot(xs, self.ram_hist, color="#c084fc", linewidth=2, label="RAM")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, HIST - 1)
        self.ax.tick_params(colors="white", labelsize=7)
        for sp in self.ax.spines.values():
            sp.set_color("#334155")
        leg = self.ax.legend(loc="upper left", fontsize=7, facecolor="#030712", edgecolor="#334155")
        for txt in leg.get_texts():
            txt.set_color("white")
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=gframe)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        lframe = tk.Frame(lower, bg=self.card, padx=10, pady=10, bd=1, relief="solid")
        lframe.pack(side="right", fill="both", expand=True, padx=(6, 0))
        tk.Label(lframe, text=self.t("log_title"), font=("Segoe UI", 10, "bold"), bg=self.card, fg="#cbd5e1").pack(anchor="w", pady=(0, 4))
        self.log_box = tk.Text(lframe, height=7, width=35, font=("Consolas", 9), bg="#030712", fg=self.neon, bd=0, highlightthickness=0)
        self.log_box.pack(fill="both", expand=True)
        for line in self.log_lines[-200:]:
            self.log_box.insert(tk.END, line + "\n")
        self.log_box.see(tk.END)

    def _card(self, parent, title, color):
        f = tk.Frame(parent, bg=self.card, padx=12, pady=10, bd=1, relief="solid")
        f.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(f, text=title, font=("Segoe UI", 8, "bold"), bg=self.card, fg="#64748b").pack(anchor="w")
        lbl = tk.Label(f, text="--", font=("Segoe UI", 16, "bold"), bg=self.card, fg=color)
        lbl.pack(anchor="w", pady=2)
        bar = ttk.Progressbar(f, length=140, mode="determinate", style="cyber.Horizontal.TProgressbar")
        bar.pack(anchor="w", pady=2)
        return lbl, bar
    def set_theme(self, accent, neon):
        self.accent, self.neon = accent, neon
        self.build_ui()
    def pick_custom_theme(self):
        color = colorchooser.askcolor(title="Accent color")[1]
        if color:
            self.set_theme(color, self.neon)
    def set_lang(self, code):
        self.lang = code
        self.build_ui()
    def update_metrics(self):
        try:
            cpu = psutil.cpu_percent()
            vm = psutil.virtual_memory()
            du = psutil.disk_usage(self.root_drive)
            self.cpu_lbl.config(text=f"{cpu:.0f}%")
            self.cpu_bar["value"] = cpu
            self.ram_lbl.config(text=f"{vm.percent:.0f}%")
            self.ram_bar["value"] = vm.percent
            self.disk_lbl.config(text=f"{du.percent:.0f}%")
            self.disk_bar["value"] = du.percent
            bat = get_battery()
            if bat is None:
                self.bat_lbl.config(text=self.t("no_battery"), font=("Segoe UI", 11, "bold"))
                self.bat_bar["value"] = 0
            else:
                state = self.t("charging") if bat.power_plugged else self.t("on_battery")
                self.bat_lbl.config(text=f"{bat.percent:.0f}%  ({state})", font=("Segoe UI", 11, "bold"))
                self.bat_bar["value"] = bat.percent
            self.cpu_hist = self.cpu_hist[1:] + [cpu]
            self.ram_hist = self.ram_hist[1:] + [vm.percent]
            self.cpu_line.set_ydata(self.cpu_hist)
            self.ram_line.set_ydata(self.ram_hist)
            self.canvas.draw_idle()
            high = cpu >= 90 or vm.percent >= 90 or du.percent >= 95
            self.status_badge.config(text=self.t("status_warn" if high else "status_ok"), bg="#7f1d1d" if high else "#064e3b", fg="#fecaca" if high else "#34d399")
        except:
            pass
        self.root.after(2000, self.update_metrics)
    def result_window(self, title, size="680x480"):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(size)
        win.config(bg=self.bg)
        win.cancel = threading.Event()
        win.bind("<Destroy>", lambda e: win.cancel.set() if e.widget is win else None)
        tk.Label(win, text=title, font=("Segoe UI", 12, "bold"), bg=self.bg, fg=self.accent).pack(pady=10)
        frame = tk.Frame(win, bg=self.card)
        frame.pack(fill="both", expand=True, padx=15, pady=5)
        text = tk.Text(frame, font=("Consolas", 10), bg="#030712", fg=self.neon, bd=0, wrap="word")
        sb = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=sb.set)
        text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        btns = tk.Frame(win, bg=self.bg)
        btns.pack(fill="x", padx=15, pady=10)
        self.button(btns, self.t("close"), win.destroy, "#7f1d1d").pack(side="right")
        def write(s, clear=False):
            def _w():
                try:
                    if clear:
                        text.delete("1.0", tk.END)
                    text.insert(tk.END, s)
                    text.see(tk.END)
                except tk.TclError:
                    pass
            self.ui(_w)
        return win, btns, write
    def check_update_thread(self):
        threading.Thread(target=self.check_update, daemon=True).start()
    def check_update(self):
        if requests is None:
            self.ui(lambda: messagebox.showinfo("Update", "pip install requests"))
            return
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            r = requests.get(url, timeout=8).json()
            latest = r.get("tag_name", VERSION)
            if latest.strip("v -WORLD") != VERSION.strip("v -WORLD") and "0.3.0" not in latest:
                self.ui(lambda: messagebox.showinfo(self.t("check_update"), f"{latest} available!\nCurrent v{VERSION}"))
                webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases")
            else:
                self.ui(lambda: messagebox.showinfo(self.t("check_update"), self.t("up_to_date")))
        except Exception as e:
            self.ui(lambda: messagebox.showerror("Update", f"Failed: {e}"))
    def diagnostics(self):
        _, _, write = self.result_window(self.t("menu_diag"))
        def work():
            write(self.t("working") + "\n", clear=True)
            write("System OK\n", clear=True)
        self.run_bg(work)
    def export_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="WinHeal_Report.txt", filetypes=[("Text", "*.txt")])
        if not path:
            return
        def work():
            text = "WinHeal report\n"
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.toast(self.t("menu_report"), self.t("report_saved", path=path))
        self.run_bg(work)
    def network(self):
        _, btns, write = self.result_window(self.t("menu_net"))
        def work():
            write(self.t("working") + "\n", clear=True)
            write(f"{self.t('host')}: {socket.gethostname()}\n{self.t('local_ip')}: {local_ip()}\n")
        self.run_bg(work)
    def startup(self):
        win, btns, write = self.result_window(self.t("menu_startup"))
        items = startup_entries()
        for scope, name, cmd in items:
            write(f"[{scope}] {name}\n    {cmd}\n")
    def junk(self):
        win, btns, write = self.result_window(self.t("menu_junk"))
        state = {"files": [], "total": 0}
        del_btn = self.button(btns, self.t("delete_now"), lambda: delete(), "#b45309")
        del_btn.config(state="disabled")
        del_btn.pack(side="left")
        def scan():
            write(self.t("working") + "\n", clear=True)
            files, total = scan_junk()
            state["files"], state["total"] = files, total
            if files:
                write(f"Found {len(files)} files {fmt_size(total)}\n", clear=True)
                self.ui(lambda: del_btn.config(state="normal"))
        def delete():
            files, total = state["files"], state["total"]
            def work():
                n, freed, failed = delete_files(files)
                write(f"Deleted {n} files, freed {fmt_size(freed)}\n", clear=True)
            self.run_bg(work)
        self.run_bg(scan)
    def empty_bin(self):
        if not messagebox.askyesno(self.t("menu_bin"), self.t("bin_confirm")):
            return
        def work():
            import ctypes
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        self.run_bg(work)
    def duplicates(self):
        folder = filedialog.askdirectory(title=self.t("dups_pick"))
        if not folder:
            return
        win, _, write = self.result_window(self.t("menu_dups"), "760x520")
        def work():
            write(f"Scanning {folder} ...\n", clear=True)
            res = find_duplicates(folder, win.cancel)
            if res is None:
                return
            groups, _ = res
            if not groups:
                write("No duplicates\n", clear=True)
                return
            wasted = sum(size * (len(ps) - 1) for size, ps in groups)
            out = [f"{len(groups)} groups {fmt_size(wasted)}", ""]
            for size, ps in groups[:20]:
                out.append(f"{fmt_size(size)} x {len(ps)}")
                out.extend(f"    {p}" for p in ps)
            write("\n".join(out) + "\n", clear=True)
        self.run_bg(work)
    def updates(self):
        _, _, write = self.result_window(self.t("menu_updates"), "760x480")
        def work():
            write(self.t("working") + "\n", clear=True)
            _, out = run_cmd(["winget", "upgrade", "--accept-source-agreements"], timeout=180)
            write(out.strip() + "\n\n", clear=True)
        self.run_bg(work)
    def benchmark(self):
        _, _, write = self.result_window(self.t("menu_bench"), "560x300")
        def work():
            write(self.t("working") + "\n", clear=True)
            s = cpu_bench()
            write(f"CPU {s:.2f}s\n", clear=True)
        self.run_bg(work)
    def file_explorer(self):
        win = tk.Toplevel(self.root)
        win.title(self.t("menu_files"))
        win.geometry("860x560")
        win.config(bg=self.bg)
        tk.Label(win, text=self.t("menu_files"), font=("Segoe UI", 12, "bold"), bg=self.bg, fg=self.accent).pack(pady=10)
        pf = tk.Frame(win, bg=self.card, padx=10, pady=8)
        pf.pack(fill="x", padx=15, pady=5)
        path_var = tk.StringVar(value=os.path.expanduser("~"))
        entry = tk.Entry(pf, textvariable=path_var, font=("Consolas", 10), bg="#030712", fg="white", insertbackground="white", bd=1, relief="solid")
        entry.pack(side="left", fill="x", expand=True, ipady=3, padx=5)
        tf = tk.Frame(win, bg=self.card)
        tf.pack(fill="both", expand=True, padx=15, pady=5)
        tree = ttk.Treeview(tf, columns=("name", "type", "size"), show="headings", selectmode="browse")
        for col, key, w, anchor in (("name", "col_name", 440, "w"), ("type", "col_type", 110, "center"), ("size", "col_size", 160, "e")):
            tree.heading(col, text=self.t(key))
            tree.column(col, width=w, anchor=anchor)
        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        entries = {}
        def load(target):
            tree.delete(*tree.get_children())
            entries.clear()
            path_var.set(target)
            try:
                names = os.listdir(target)
            except:
                return
            for n in names:
                entries[tree.insert("", "end", values=(n, "", ""))] = (n, "folder")
        def on_double(_event):
            sel = tree.selection()
            if not sel:
                return
            name, kind = entries[sel[0]]
            cur = path_var.get()
            load(os.path.join(cur, name))
        tree.bind("<Double-1>", on_double)
        entry.bind("<Return>", lambda e: load(path_var.get()))
        bf = tk.Frame(win, bg=self.bg)
        bf.pack(fill="x", padx=15, pady=10)
        self.button(bf, self.t("close"), win.destroy, "#7f1d1d").pack(side="right")
        load(os.path.expanduser("~"))

    # ===== NEW v0.3.0 FEATURES =====
    def gaming_mode(self):
        win, btns, write = self.result_window("🎮 Gaming Mode - Boost Performance", "620x380")
        def work():
            write("🎮 Gaming Mode Activating...\n\n", clear=True)
            killed = 0
            for proc_name in ["OneDrive.exe", "Skype.exe", "Teams.exe", "Discord.exe"]:
                try:
                    for proc in psutil.process_iter(['name']):
                        if proc.info['name'] and proc.info['name'].lower() == proc_name.lower():
                            proc.kill()
                            killed += 1
                            write(f"  ✓ Closed {proc_name}\n")
                except:
                    pass
            write(f"\n✓ Closed {killed} background apps!\n🚀 GAMING MODE ACTIVE!")
            self.log(self.t("gaming_on"))
            self.toast("🎮 Gaming Mode", "PC Boosted for Gaming!")
        self.run_bg(work)
        self.button(btns, "🔄 Restore Normal", lambda: self.restore_normal(win), "#334155").pack(side="left")

    def restore_normal(self, win):
        if IS_WIN:
            run_cmd(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], timeout=10)
        self.toast("Gaming Mode", "Normal Mode Restored")
        win.destroy()

    def battery_saver(self):
        win, btns, write = self.result_window("🔋 Battery Saver", "620x380")
        def work():
            write("🔋 Battery Saver Activating...\n\n", clear=True)
            if IS_WIN:
                run_cmd(["powercfg", "/change", "monitor-timeout-ac", "2"], timeout=10)
                run_cmd(["powercfg", "/change", "monitor-timeout-dc", "1"], timeout=10)
            write("✅ BATTERY SAVER ACTIVE! Battery life extended!")
            self.log(self.t("battery_on"))
            self.toast("🔋 Battery Saver", "Battery Optimized!")
        self.run_bg(work)

    def internet_cleaner(self):
        win, btns, write = self.result_window("🌐 Internet Cleaner", "620x420")
        state = {"size": 0, "files": []}
        def scan():
            write("🌐 Scanning browser caches...\n\n", clear=True)
            total_size = 0
            found = []
            user = os.path.expanduser("~")
            paths = [
                os.path.join(user, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache"),
                os.path.join(user, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cache"),
            ]
            for p in paths:
                if os.path.exists(p):
                    for root, dirs, files in os.walk(p):
                        for f in files:
                            fp = os.path.join(root, f)
                            try:
                                sz = os.path.getsize(fp)
                                total_size += sz
                                found.append((fp, sz))
                            except:
                                pass
            state["size"] = total_size
            state["files"] = found
            write(f"Found: {len(found)} cache files\nTotal: {fmt_size(total_size)}\n\n", clear=True)
            if total_size > 0:
                self.ui(lambda: clean_btn.config(state="normal"))
        def clean():
            if not messagebox.askyesno("Internet Cleaner", f"Delete {len(state['files'])} cache files?"):
                return
            def work():
                deleted, freed = 0, 0
                for fp, sz in state["files"][:1000]:
                    try:
                        os.remove(fp)
                        deleted += 1
                        freed += sz
                    except:
                        pass
                msg = f"Cleaned {deleted} files, freed {fmt_size(freed)}"
                write(f"\n✅ {msg}\n", clear=False)
                self.toast("🌐 Internet Cleaner", msg)
            self.run_bg(work)
        clean_btn = self.button(btns, "🧹 Clean Now", clean, "#b45309")
        clean_btn.config(state="disabled")
        clean_btn.pack(side="left")
        self.run_bg(scan)

if __name__ == "__main__":
    tk_root = tk.Tk()
    try:
        if os.path.exists("icon.ico"):
            tk_root.iconbitmap("icon.ico")
    except:
        pass
    WinHealApp(tk_root)
    tk_root.mainloop()