"""WinHeal - Windows system care tool.

Every feature in this file does real work. Nothing is simulated.
Languages: English (en) and Bangla (bn). Add more in STRINGS.
"""
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
from collections import defaultdict

import psutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    import winreg
except ImportError:  # not Windows
    winreg = None

VERSION = "0.1.0"
IS_WIN = os.name == "nt"
NO_WINDOW = 0x08000000 if IS_WIN else 0
LOG_DIR = os.path.join(os.path.expanduser("~"), "WinHealLogs")
HIST = 30  # points on the live graph

# --------------------------------------------------------------------------
# Languages. Missing Bangla keys fall back to English.
# --------------------------------------------------------------------------
STRINGS = {
    "en": {
        "app_title": "WinHeal - System Care Tool",
        "menu_diag": "System Diagnostics",
        "menu_files": "File & Drive Explorer",
        "menu_net": "Network Troubleshooter",
        "menu_startup": "Startup Programs",
        "menu_dups": "Duplicate File Finder",
        "menu_updates": "Software Updates",
        "menu_junk": "Junk File Cleaner",
        "menu_bin": "Empty Recycle Bin",
        "menu_bench": "Quick Benchmark",
        "menu_report": "Export System Report",
        "theme": "THEME", "language": "LANGUAGE", "custom": "Custom", "quit": "Quit",
        "dashboard": "SYSTEM DASHBOARD",
        "status_ok": "● System load: normal",
        "status_warn": "● System load: high",
        "cpu": "CPU", "ram": "MEMORY", "disk": "DISK", "battery": "BATTERY",
        "no_battery": "No battery", "charging": "Plugged in", "on_battery": "On battery",
        "graph_title": "Live CPU & memory", "log_title": "Activity log",
        "close": "Close", "working": "Working...", "error": "Error",
        "windows_only": "This feature works on Windows only.",
        "threads": "threads", "free": "free", "started": "WinHeal started.",
        "issue_cpu": "CPU usage is very high. Close heavy programs.",
        "issue_ram": "Memory usage is very high. Close unused programs or restart.",
        "issue_disk": "Disk is almost full. Use the Junk Cleaner or Duplicate Finder.",
        "issue_battery": "Battery is low and not charging.",
        "issue_uptime": "The PC has not restarted for {d} days. A restart can help.",
        "no_issues": "No problems found. Your system looks healthy.",
        "found_issues": "Possible problems:",
        "top_procs": "Top memory users:",
        "uptime": "Uptime",
        "host": "Computer name", "local_ip": "Local IP", "sent": "Data sent",
        "received": "Data received", "ping_test": "Internet ping (8.8.8.8)",
        "dns_test": "DNS lookup (example.com)", "ok": "OK", "failed": "FAILED",
        "net_ok": "Result: connection looks healthy.",
        "net_dns": "Result: internet reachable but DNS fails. Try 'Flush DNS cache' or change DNS server.",
        "net_down": "Result: no internet. Check Wi-Fi/cable, router, and restart the router.",
        "flush_dns": "Flush DNS cache", "dns_flushed": "DNS cache flushed.",
        "startup_none": "No startup entries found.",
        "startup_note": "WinHeal only lists these. To disable one, use Task Manager > Startup apps.",
        "open_startup": "Open Startup settings",
        "junk_found": "Found {n} temp files older than 24 hours, total {size}.",
        "junk_none": "No old temp files to clean.",
        "delete_now": "Delete these files",
        "confirm_delete": "Delete {n} files ({size})?\nOnly temp files older than 24 hours are removed.",
        "junk_done": "Deleted {n} files, freed {size}. {f} files were in use/protected and skipped.",
        "bin_confirm": "Permanently empty the Recycle Bin? This cannot be undone.",
        "bin_done": "Recycle Bin emptied.",
        "dups_pick": "Choose a folder to scan for duplicates",
        "dups_scanning": "Scanning {folder} ...",
        "dups_none": "No duplicate files found (files under 1 KB are ignored).",
        "dups_summary": "{g} groups of identical files. Recoverable space: {size}.",
        "dups_note": "WinHeal deletes nothing. Review the list and remove copies yourself.",
        "wg_missing": "winget was not found. Install 'App Installer' from the Microsoft Store.",
        "wg_hint": "To update everything, run in a terminal: winget upgrade --all",
        "bench_cpu": "CPU test time: {s:.2f} s (lower is faster)",
        "bench_disk": "Disk write speed: {mb:.0f} MB/s",
        "bench_note": "Simple indicative tests. Not comparable with professional benchmarks.",
        "report_saved": "Report saved: {path}",
        "parent_dir": "[..] Parent folder", "col_name": "Name", "col_type": "Type",
        "col_size": "Size", "folder": "Folder", "file": "File", "home": "Home",
        "browse": "Browse...", "copy_ask": "Copy '{name}' to another folder?",
        "copy_done": "Copied to: {dest}", "path": "Path",
    },
    "bn": {
        "app_title": "WinHeal - সিস্টেম কেয়ার টুল",
        "menu_diag": "সিস্টেম ডায়াগনস্টিক",
        "menu_files": "ফাইল ও ড্রাইভ এক্সপ্লোরার",
        "menu_net": "নেটওয়ার্ক সমস্যা সমাধান",
        "menu_startup": "স্টার্টআপ প্রোগ্রাম",
        "menu_dups": "ডুপ্লিকেট ফাইল খোঁজা",
        "menu_updates": "সফটওয়্যার আপডেট",
        "menu_junk": "জাঙ্ক ফাইল ক্লিনার",
        "menu_bin": "রিসাইকেল বিন খালি করা",
        "menu_bench": "দ্রুত বেঞ্চমার্ক",
        "menu_report": "সিস্টেম রিপোর্ট সেভ",
        "theme": "থিম", "language": "ভাষা", "custom": "কাস্টম", "quit": "বন্ধ করুন",
        "dashboard": "সিস্টেম ড্যাশবোর্ড",
        "status_ok": "● সিস্টেম লোড: স্বাভাবিক",
        "status_warn": "● সিস্টেম লোড: বেশি",
        "cpu": "CPU", "ram": "মেমোরি", "disk": "ডিস্ক", "battery": "ব্যাটারি",
        "no_battery": "ব্যাটারি নেই", "charging": "চার্জে আছে", "on_battery": "ব্যাটারিতে চলছে",
        "graph_title": "লাইভ CPU ও মেমোরি", "log_title": "কাজের লগ",
        "close": "বন্ধ", "working": "কাজ চলছে...", "error": "ত্রুটি",
        "windows_only": "এই ফিচার শুধু Windows-এ চলে।",
        "threads": "থ্রেড", "free": "খালি", "started": "WinHeal চালু হয়েছে।",
        "issue_cpu": "CPU ব্যবহার খুব বেশি। ভারী প্রোগ্রাম বন্ধ করুন।",
        "issue_ram": "মেমোরি ব্যবহার খুব বেশি। অপ্রয়োজনীয় প্রোগ্রাম বন্ধ করুন বা রিস্টার্ট দিন।",
        "issue_disk": "ডিস্ক প্রায় ভরে গেছে। জাঙ্ক ক্লিনার বা ডুপ্লিকেট ফাইন্ডার ব্যবহার করুন।",
        "issue_battery": "ব্যাটারি কম এবং চার্জ হচ্ছে না।",
        "issue_uptime": "কম্পিউটার {d} দিন ধরে রিস্টার্ট হয়নি। রিস্টার্ট দিলে উপকার হতে পারে।",
        "no_issues": "কোনো সমস্যা পাওয়া যায়নি। সিস্টেম ভালো আছে।",
        "found_issues": "সম্ভাব্য সমস্যা:",
        "top_procs": "সবচেয়ে বেশি মেমোরি ব্যবহার করছে:",
        "uptime": "চালু আছে",
        "host": "কম্পিউটারের নাম", "local_ip": "লোকাল IP", "sent": "পাঠানো ডেটা",
        "received": "পাওয়া ডেটা", "ping_test": "ইন্টারনেট পিং (8.8.8.8)",
        "dns_test": "DNS লুকআপ (example.com)", "ok": "ঠিক আছে", "failed": "ব্যর্থ",
        "net_ok": "ফলাফল: সংযোগ ঠিক আছে।",
        "net_dns": "ফলাফল: ইন্টারনেট আছে কিন্তু DNS কাজ করছে না। 'DNS ক্যাশ পরিষ্কার' চাপুন বা DNS সার্ভার বদলান।",
        "net_down": "ফলাফল: ইন্টারনেট নেই। ওয়াই-ফাই/ক্যাবল ও রাউটার দেখুন, রাউটার রিস্টার্ট দিন।",
        "flush_dns": "DNS ক্যাশ পরিষ্কার", "dns_flushed": "DNS ক্যাশ পরিষ্কার হয়েছে।",
        "startup_none": "কোনো স্টার্টআপ এন্ট্রি পাওয়া যায়নি।",
        "startup_note": "WinHeal শুধু তালিকা দেখায়। বন্ধ করতে Task Manager > Startup apps ব্যবহার করুন।",
        "open_startup": "স্টার্টআপ সেটিংস খুলুন",
        "junk_found": "২৪ ঘণ্টার পুরনো {n}টি টেম্প ফাইল পাওয়া গেছে, মোট {size}।",
        "junk_none": "পরিষ্কার করার মতো পুরনো টেম্প ফাইল নেই।",
        "delete_now": "ফাইলগুলো মুছুন",
        "confirm_delete": "{n}টি ফাইল ({size}) মুছবেন?\nশুধু ২৪ ঘণ্টার পুরনো টেম্প ফাইল মোছা হবে।",
        "junk_done": "{n}টি ফাইল মুছে {size} জায়গা খালি হয়েছে। {f}টি ফাইল ব্যবহারে ছিল বলে বাদ গেছে।",
        "bin_confirm": "রিসাইকেল বিন স্থায়ীভাবে খালি করবেন? এটা ফেরানো যাবে না।",
        "bin_done": "রিসাইকেল বিন খালি হয়েছে।",
        "dups_pick": "ডুপ্লিকেট খোঁজার জন্য ফোল্ডার বেছে নিন",
        "dups_scanning": "{folder} স্ক্যান হচ্ছে ...",
        "dups_none": "কোনো ডুপ্লিকেট ফাইল পাওয়া যায়নি (১ KB-এর ছোট ফাইল বাদ)।",
        "dups_summary": "{g} গ্রুপ একই ফাইল। বাঁচানো যাবে: {size}।",
        "dups_note": "WinHeal কিছুই মোছে না। তালিকা দেখে নিজে কপি মুছুন।",
        "wg_missing": "winget পাওয়া যায়নি। Microsoft Store থেকে 'App Installer' ইনস্টল করুন।",
        "wg_hint": "সব আপডেট করতে টার্মিনালে চালান: winget upgrade --all",
        "bench_cpu": "CPU টেস্টের সময়: {s:.2f} সেকেন্ড (কম মানে দ্রুত)",
        "bench_disk": "ডিস্ক লেখার গতি: {mb:.0f} MB/s",
        "bench_note": "এটা সহজ আনুমানিক টেস্ট, পেশাদার বেঞ্চমার্কের সঙ্গে তুলনীয় নয়।",
        "report_saved": "রিপোর্ট সেভ হয়েছে: {path}",
        "parent_dir": "[..] উপরের ফোল্ডার", "col_name": "নাম", "col_type": "ধরন",
        "col_size": "সাইজ", "folder": "ফোল্ডার", "file": "ফাইল", "home": "হোম",
        "browse": "বেছে নিন...", "copy_ask": "'{name}' অন্য ফোল্ডারে কপি করবেন?",
        "copy_done": "কপি হয়েছে: {dest}", "path": "পাথ",
    },
}


# --------------------------------------------------------------------------
# Plain helpers (no UI, easy to test)
# --------------------------------------------------------------------------
def fmt_size(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
        n /= 1024


def run_cmd(cmd, timeout=60):
    """Run a command, return (returncode, combined output)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, creationflags=NO_WINDOW)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return -1, str(e)


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # UDP connect sends no packet
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
    except (AttributeError, NotImplementedError):
        return None


def junk_dirs():
    cands = [os.environ.get("TEMP"), os.environ.get("TMP")]
    root = os.environ.get("SystemRoot")
    if root:
        cands.append(os.path.join(root, "Temp"))
    out, seen = [], set()
    for c in cands:
        if c and os.path.isdir(c) and os.path.normcase(c) not in seen:
            seen.add(os.path.normcase(c))
            out.append(c)
    return out


def scan_junk(dirs=None, min_age_hours=24):
    """Return ([(path, size)], total_size) for temp files older than min_age_hours."""
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
    """Delete files. Returns (deleted_count, freed_bytes, failed_count)."""
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
    """Group identical files (same size, then same SHA-256). Files < 1 KB ignored.
    Returns (groups, files_seen) or None if cancelled. groups = [(size, [paths])]."""
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
    """Read-only list of (scope, name, command) from the Windows Run keys."""
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


# --------------------------------------------------------------------------
# Application
# --------------------------------------------------------------------------
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

    # ----- language / thread helpers ---------------------------------------
    def t(self, key, **kw):
        s = STRINGS.get(self.lang, {}).get(key) or STRINGS["en"].get(key, key)
        return s.format(**kw) if kw else s

    def ui(self, fn):
        """Run fn on the UI thread (safe to call from any thread)."""
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
            except Exception as e:  # report instead of dying silently
                self.log(f"ERROR: {e}")
        threading.Thread(target=runner, daemon=True).start()

    # ----- logging / toast ---------------------------------------------------
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
        except (tk.TclError, AttributeError):
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
        tk.Label(inner, text=message, font=("Segoe UI", 9), bg=self.card, fg="#cbd5e1",
                 wraplength=300, justify="left").pack(anchor="w", pady=3)
        w.after(3500, w.destroy)

    # ----- UI building ---------------------------------------------------------
    def button(self, parent, text, cmd, bg="#0369a1", fg="white"):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, font=("Segoe UI", 9, "bold"),
                         relief="flat", padx=12, pady=5, cursor="hand2")

    def build_ui(self):
        if self.main is not None:
            self.main.destroy()
        self.root.title(self.t("app_title"))
        self.root.config(bg=self.bg)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("cyber.Horizontal.TProgressbar", troughcolor="#0f172a", background=self.neon,
                        darkcolor=self.neon, lightcolor=self.neon, bordercolor=self.bg)

        self.main = tk.Frame(self.root, bg=self.bg)
        self.main.pack(fill="both", expand=True)

        # Sidebar
        side = tk.Frame(self.main, bg=self.card, width=260)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="⚡ WINHEAL", font=("Segoe UI", 14, "bold"), bg=self.card,
                 fg=self.accent).pack(anchor="w", padx=15, pady=(15, 0))
        tk.Label(side, text=f"v{VERSION}", font=("Segoe UI", 8), bg=self.card,
                 fg="#64748b").pack(anchor="w", padx=15, pady=(0, 10))

        menu = [
            ("menu_diag", self.diagnostics), ("menu_files", self.file_explorer),
            ("menu_net", self.network), ("menu_startup", self.startup),
            ("menu_dups", self.duplicates), ("menu_updates", self.updates),
            ("menu_junk", self.junk), ("menu_bin", self.empty_bin),
            ("menu_bench", self.benchmark), ("menu_report", self.export_report),
        ]
        for key, cmd in menu:
            tk.Button(side, text=self.t(key), command=cmd, bg=self.card, fg="#cbd5e1",
                      activebackground="#1e293b", activeforeground=self.accent,
                      font=("Segoe UI", 10), anchor="w", padx=15, pady=5, relief="flat",
                      cursor="hand2").pack(fill="x", pady=1)

        for label_key, items in (
            ("theme", [("Cyan", ("#38bdf8", "#10b981"), "#0369a1"), ("Green", ("#10b981", "#38bdf8"), "#064e3b"),
                       ("Purple", ("#c084fc", "#f43f5e"), "#581c87")]),
        ):
            box = tk.Frame(side, bg=self.card)
            box.pack(fill="x", padx=15, pady=(12, 0))
            tk.Label(box, text=self.t(label_key), font=("Segoe UI", 8, "bold"), bg=self.card,
                     fg="#64748b").pack(anchor="w")
            row = tk.Frame(box, bg=self.card)
            row.pack(fill="x", pady=2)
            for name, colors, bgc in items:
                tk.Button(row, text=name, command=lambda c=colors: self.set_theme(*c), bg=bgc, fg="white",
                          font=("Segoe UI", 8), relief="flat", width=6).pack(side="left", padx=1)
            tk.Button(row, text=self.t("custom"), command=self.pick_custom_theme, bg="#334155", fg="white",
                      font=("Segoe UI", 8), relief="flat", width=7).pack(side="left", padx=1)

        lbox = tk.Frame(side, bg=self.card)
        lbox.pack(fill="x", padx=15, pady=(12, 0))
        tk.Label(lbox, text=self.t("language"), font=("Segoe UI", 8, "bold"), bg=self.card,
                 fg="#64748b").pack(anchor="w")
        lrow = tk.Frame(lbox, bg=self.card)
        lrow.pack(fill="x", pady=2)
        tk.Button(lrow, text="English", command=lambda: self.set_lang("en"), bg="#334155", fg="white",
                  font=("Segoe UI", 9), relief="flat", width=9).pack(side="left", padx=1)
        tk.Button(lrow, text="বাংলা", command=lambda: self.set_lang("bn"), bg="#334155", fg="white",
                  font=("Segoe UI", 9), relief="flat", width=9).pack(side="left", padx=1)

        tk.Button(side, text=self.t("quit"), command=self.root.destroy, bg="#180707", fg="#f87171",
                  font=("Segoe UI", 9, "bold"), pady=5, relief="flat",
                  cursor="hand2").pack(side="bottom", fill="x", padx=15, pady=10)

        # Content
        content = tk.Frame(self.main, bg=self.bg)
        content.pack(side="right", fill="both", expand=True, padx=20, pady=15)
        top = tk.Frame(content, bg=self.bg)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text=self.t("dashboard"), font=("Segoe UI", 12, "bold"), bg=self.bg,
                 fg=self.accent).pack(side="left")
        self.status_badge = tk.Label(top, text=self.t("status_ok"), font=("Segoe UI", 9, "bold"),
                                     bg="#064e3b", fg="#34d399", padx=10, pady=4)
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
        tk.Label(gframe, text=self.t("graph_title"), font=("Segoe UI", 10, "bold"), bg=self.card,
                 fg="#cbd5e1").pack(anchor="w", pady=(0, 4))
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
        tk.Label(lframe, text=self.t("log_title"), font=("Segoe UI", 10, "bold"), bg=self.card,
                 fg="#cbd5e1").pack(anchor="w", pady=(0, 4))
        self.log_box = tk.Text(lframe, height=7, width=35, font=("Consolas", 9), bg="#030712",
                               fg=self.neon, bd=0, highlightthickness=0)
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

    # ----- live metrics ----------------------------------------------------------
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
            self.status_badge.config(text=self.t("status_warn" if high else "status_ok"),
                                     bg="#7f1d1d" if high else "#064e3b",
                                     fg="#fecaca" if high else "#34d399")
        except (tk.TclError, psutil.Error, OSError):
            pass
        self.root.after(2000, self.update_metrics)

    # ----- reusable result window ---------------------------------------------------
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

    # ----- features ---------------------------------------------------------------------
    def summary_text(self):
        """Real system summary, used by Diagnostics and the exported report."""
        cpu = psutil.cpu_percent(interval=1)
        vm = psutil.virtual_memory()
        du = psutil.disk_usage(self.root_drive)
        bat = get_battery()
        uptime_days = (time.time() - psutil.boot_time()) / 86400
        lines = [
            f"{datetime.datetime.now():%Y-%m-%d %H:%M}",
            f"{self.t('cpu')}: {cpu:.0f}%  ({psutil.cpu_count()} {self.t('threads')})",
            f"{self.t('ram')}: {vm.percent:.0f}%  ({fmt_size(vm.used)} / {fmt_size(vm.total)})",
            f"{self.t('disk')} {self.root_drive}: {du.percent:.0f}%  ({fmt_size(du.free)} {self.t('free')})",
            f"{self.t('uptime')}: {uptime_days:.1f} d",
        ]
        if bat is not None:
            lines.append(f"{self.t('battery')}: {bat.percent:.0f}% "
                         f"({self.t('charging') if bat.power_plugged else self.t('on_battery')})")
        issues = []
        if cpu >= 85:
            issues.append(self.t("issue_cpu"))
        if vm.percent >= 85:
            issues.append(self.t("issue_ram"))
        if du.percent >= 90:
            issues.append(self.t("issue_disk"))
        if bat is not None and not bat.power_plugged and bat.percent <= 20:
            issues.append(self.t("issue_battery"))
        if uptime_days >= 7:
            issues.append(self.t("issue_uptime", d=int(uptime_days)))
        lines.append("")
        if issues:
            lines.append(self.t("found_issues"))
            lines.extend(f"  - {i}" for i in issues)
        else:
            lines.append(self.t("no_issues"))
        procs = []
        for p in psutil.process_iter(["name", "memory_info"]):
            try:
                mi = p.info["memory_info"]
                if mi:
                    procs.append((mi.rss, p.info["name"] or "?"))
            except psutil.Error:
                pass
        procs.sort(reverse=True)
        lines += ["", self.t("top_procs")]
        lines.extend(f"  {fmt_size(r):>10}  {n}" for r, n in procs[:8])
        return "\n".join(lines)

    def diagnostics(self):
        _, _, write = self.result_window(self.t("menu_diag"))

        def work():
            write(self.t("working") + "\n", clear=True)
            write(self.summary_text() + "\n", clear=True)
            self.log(self.t("menu_diag"))
        self.run_bg(work)

    def export_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="WinHeal_Report.txt",
                                            filetypes=[("Text", "*.txt")])
        if not path:
            return

        def work():
            text = "WinHeal report\n" + "=" * 30 + "\n" + self.summary_text() + "\n"
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.toast(self.t("menu_report"), self.t("report_saved", path=path))
            self.log(self.t("report_saved", path=path))
        self.run_bg(work)

    def network(self):
        _, btns, write = self.result_window(self.t("menu_net"))

        def work():
            write(self.t("working") + "\n", clear=True)
            io = psutil.net_io_counters()
            write(f"{self.t('host')}: {socket.gethostname()}\n"
                  f"{self.t('local_ip')}: {local_ip()}\n"
                  f"{self.t('sent')}: {fmt_size(io.bytes_sent)}\n"
                  f"{self.t('received')}: {fmt_size(io.bytes_recv)}\n\n", clear=True)
            p = ping_ok()
            write(f"{self.t('ping_test')}: {self.t('ok') if p else self.t('failed')}\n")
            d = dns_ok()
            write(f"{self.t('dns_test')}: {self.t('ok') if d else self.t('failed')}\n\n")
            write(self.t("net_ok") if (p and d) else self.t("net_dns") if (p and not d) else self.t("net_down"))
            self.log(f"{self.t('menu_net')}: ping={p}, dns={d}")
        self.run_bg(work)

        if IS_WIN:
            def flush():
                def w():
                    rc, _ = run_cmd(["ipconfig", "/flushdns"], timeout=20)
                    self.toast(self.t("flush_dns"), self.t("dns_flushed") if rc == 0 else self.t("failed"))
                    self.log(self.t("flush_dns"))
                self.run_bg(w)
            self.button(btns, self.t("flush_dns"), flush).pack(side="left")

    def startup(self):
        win, btns, write = self.result_window(self.t("menu_startup"))
        if not IS_WIN:
            write(self.t("windows_only"))
            return
        items = startup_entries()
        if not items:
            write(self.t("startup_none") + "\n\n")
        for scope, name, cmd in items:
            write(f"[{scope}] {name}\n    {cmd}\n")
        write("\n" + self.t("startup_note"))

        def open_settings():
            try:
                os.startfile("ms-settings:startupapps")
            except OSError:
                run_cmd(["taskmgr"])
        self.button(btns, self.t("open_startup"), open_settings).pack(side="left")

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
                write(self.t("junk_found", n=len(files), size=fmt_size(total)) + "\n", clear=True)
                self.ui(lambda: del_btn.config(state="normal"))
            else:
                write(self.t("junk_none") + "\n", clear=True)

        def delete():
            files, total = state["files"], state["total"]
            if not messagebox.askyesno(self.t("menu_junk"),
                                       self.t("confirm_delete", n=len(files), size=fmt_size(total))):
                return
            del_btn.config(state="disabled")

            def work():
                n, freed, failed = delete_files(files)
                msg = self.t("junk_done", n=n, size=fmt_size(freed), f=failed)
                write(msg + "\n", clear=True)
                self.toast(self.t("menu_junk"), msg)
                self.log(msg)
            self.run_bg(work)
        self.run_bg(scan)

    def empty_bin(self):
        if not IS_WIN:
            messagebox.showinfo(self.t("menu_bin"), self.t("windows_only"))
            return
        if not messagebox.askyesno(self.t("menu_bin"), self.t("bin_confirm")):
            return

        def work():
            import ctypes
            # 7 = no confirmation, no progress UI, no sound (we already asked)
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
            self.toast(self.t("menu_bin"), self.t("bin_done"))
            self.log(self.t("bin_done"))
        self.run_bg(work)

    def duplicates(self):
        folder = filedialog.askdirectory(title=self.t("dups_pick"))
        if not folder:
            return
        win, _, write = self.result_window(self.t("menu_dups"), "760x520")

        def work():
            write(self.t("dups_scanning", folder=folder) + "\n", clear=True)
            res = find_duplicates(folder, win.cancel)
            if res is None:
                return
            groups, _ = res
            if not groups:
                write(self.t("dups_none") + "\n", clear=True)
                return
            wasted = sum(size * (len(ps) - 1) for size, ps in groups)
            out = [self.t("dups_summary", g=len(groups), size=fmt_size(wasted)), self.t("dups_note"), ""]
            for size, ps in groups[:50]:
                out.append(f"{fmt_size(size)} x {len(ps)}")
                out.extend(f"    {p}" for p in ps)
            if len(groups) > 50:
                out.append(f"... +{len(groups) - 50}")
            write("\n".join(out) + "\n", clear=True)
            self.log(self.t("dups_summary", g=len(groups), size=fmt_size(wasted)))
        self.run_bg(work)

    def updates(self):
        _, _, write = self.result_window(self.t("menu_updates"), "760x480")

        def work():
            if not IS_WIN or not shutil.which("winget"):
                write(self.t("wg_missing") if IS_WIN else self.t("windows_only"), clear=True)
                return
            write(self.t("working") + "\n", clear=True)
            _, out = run_cmd(["winget", "upgrade", "--accept-source-agreements"], timeout=180)
            write(out.strip() + "\n\n" + self.t("wg_hint"), clear=True)
            self.log(self.t("menu_updates"))
        self.run_bg(work)

    def benchmark(self):
        _, _, write = self.result_window(self.t("menu_bench"), "560x300")

        def work():
            write(self.t("working") + "\n", clear=True)
            s = cpu_bench()
            write(self.t("bench_cpu", s=s) + "\n", clear=True)
            try:
                mb = disk_write_bench()
                write(self.t("bench_disk", mb=mb) + "\n")
            except OSError as e:
                write(f"{self.t('error')}: {e}\n")
            write("\n" + self.t("bench_note"))
            self.log(self.t("menu_bench"))
        self.run_bg(work)

    def file_explorer(self):
        win = tk.Toplevel(self.root)
        win.title(self.t("menu_files"))
        win.geometry("860x560")
        win.config(bg=self.bg)
        tk.Label(win, text=self.t("menu_files"), font=("Segoe UI", 12, "bold"), bg=self.bg,
                 fg=self.accent).pack(pady=10)

        pf = tk.Frame(win, bg=self.card, padx=10, pady=8)
        pf.pack(fill="x", padx=15, pady=5)
        tk.Label(pf, text=self.t("path") + ":", font=("Segoe UI", 9, "bold"), bg=self.card,
                 fg="#94a3b8").pack(side="left", padx=(0, 5))
        path_var = tk.StringVar(value=os.path.expanduser("~"))
        entry = tk.Entry(pf, textvariable=path_var, font=("Consolas", 10), bg="#030712", fg="white",
                         insertbackground="white", bd=1, relief="solid")
        entry.pack(side="left", fill="x", expand=True, ipady=3, padx=5)

        tf = tk.Frame(win, bg=self.card)
        tf.pack(fill="both", expand=True, padx=15, pady=5)
        tree = ttk.Treeview(tf, columns=("name", "type", "size"), show="headings", selectmode="browse")
        for col, key, w, anchor in (("name", "col_name", 440, "w"), ("type", "col_type", 110, "center"),
                                    ("size", "col_size", 160, "e")):
            tree.heading(col, text=self.t(key))
            tree.column(col, width=w, anchor=anchor)
        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        entries = {}  # iid -> (name, kind); avoids Treeview turning "2024" into an int

        def load(target):
            if not os.path.isdir(target):
                messagebox.showerror(self.t("error"), target)
                return
            try:
                names = os.listdir(target)
            except OSError as e:
                messagebox.showerror(self.t("error"), str(e))
                return
            tree.delete(*tree.get_children())
            entries.clear()
            path_var.set(target)
            parent = os.path.dirname(target)
            if parent and parent != target:
                entries[tree.insert("", "end", values=(self.t("parent_dir"), "", ""))] = ("..", "parent")
            folders = sorted((n for n in names if os.path.isdir(os.path.join(target, n))), key=str.lower)
            files = sorted((n for n in names if not os.path.isdir(os.path.join(target, n))), key=str.lower)
            for n in folders:
                entries[tree.insert("", "end", values=(n, self.t("folder"), ""))] = (n, "folder")
            for n in files:
                try:
                    size = fmt_size(os.path.getsize(os.path.join(target, n)))
                except OSError:
                    size = "?"
                entries[tree.insert("", "end", values=(n, self.t("file"), size))] = (n, "file")

        def on_double(_event):
            sel = tree.selection()
            if not sel:
                return
            name, kind = entries[sel[0]]
            cur = path_var.get()
            if kind == "parent":
                load(os.path.dirname(cur))
            elif kind == "folder":
                load(os.path.join(cur, name))
            elif messagebox.askyesno(self.t("menu_files"), self.t("copy_ask", name=name)):
                dest = filedialog.askdirectory()
                if dest:
                    try:
                        shutil.copy(os.path.join(cur, name), dest)
                        messagebox.showinfo(self.t("menu_files"), self.t("copy_done", dest=dest))
                        self.log(f"{name} -> {dest}")
                    except OSError as e:
                        messagebox.showerror(self.t("error"), str(e))

        tree.bind("<Double-1>", on_double)
        entry.bind("<Return>", lambda e: load(path_var.get()))

        def browse():
            d = filedialog.askdirectory()
            if d:
                load(d)

        bf = tk.Frame(win, bg=self.bg)
        bf.pack(fill="x", padx=15, pady=10)
        self.button(bf, "🏠 " + self.t("home"), lambda: load(os.path.expanduser("~"))).pack(side="left")
        self.button(bf, self.t("browse"), browse, "#064e3b", "#34d399").pack(side="left", padx=10)
        self.button(bf, self.t("close"), win.destroy, "#7f1d1d").pack(side="right")
        load(os.path.expanduser("~"))


if __name__ == "__main__":
    tk_root = tk.Tk()
    WinHealApp(tk_root)
    tk_root.mainloop()
