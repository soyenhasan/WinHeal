import customtkinter as ctk
import os, shutil, psutil, threading, json, requests, ctypes, winreg
from pathlib import Path
import winshell
from tkinter import messagebox, filedialog

TOTAL_FILE = "total_cleaned.json"
APP_VERSION = "v0.7.0 LEGEND"
GITHUB_REPO = "soyenhasan/WinHeal-AI"

def get_total():
    if os.path.exists(TOTAL_FILE):
        try:
            with open(TOTAL_FILE, 'r') as f:
                return json.load(f).get('total_mb', 0)
        except: return 0
    return 0

def save_total(mb):
    total = get_total() + mb
    with open(TOTAL_FILE, 'w') as f:
        json.dump({'total_mb': total}, f)
    return total

def get_stats():
    temp_path = Path(os.getenv('TEMP'))
    count = len(list(temp_path.glob('*'))) if temp_path.exists() else 0
    temp_mb = sum(f.stat().st_size for f in temp_path.glob('*') if f.is_file()) / (1024*1024) if temp_path.exists() else 0
    browser_mb = 0
    try:
        chrome_cache = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cache"
        if chrome_cache.exists():
            browser_mb = sum(f.stat().st_size for f in chrome_cache.rglob('*') if f.is_file()) / (1024*1024)
    except: pass
    ram = psutil.virtual_memory().percent
    return count, temp_mb, browser_mb, ram

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.geometry("560x820")
app.title(f"WinHeal {APP_VERSION}")
try:
    if os.path.exists("icon.ico"): app.iconbitmap("icon.ico")
except: pass

title = ctk.CTkLabel(app, text="WinHeal", font=ctk.CTkFont(size=55, weight="bold"), text_color="#00D1FF")
title.pack(pady=(15,2))
subtitle = ctk.CTkLabel(app, text=f"{APP_VERSION} - 1,2,3 NEW ADDED", font=ctk.CTkFont(size=13), text_color="#00FF88")
subtitle.pack()

total_mb = get_total()
total_label = ctk.CTkLabel(app, text=f"🏆 Total Cleaned: {total_mb:.1f} MB | Made in Bangladesh 🇧🇩", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#1F6AA5", corner_radius=20, width=480, height=32)
total_label.pack(pady=12)

count, temp_mb, browser_mb, ram = get_stats()
stats_label = ctk.CTkLabel(app, text=f"Temp: {count} files ({temp_mb:.1f} MB) | Browser: {browser_mb:.1f} MB | RAM: {ram}%", font=ctk.CTkFont(size=12))
stats_label.pack(pady=5)

progress = ctk.CTkProgressBar(app, width=480, height=15)
progress.pack(pady=10)
progress.set(0)
percent_label = ctk.CTkLabel(app, text="0%", font=ctk.CTkFont(size=12, weight="bold"))
percent_label.pack()
status = ctk.CTkLabel(app, text="Ready to heal...", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FF88")
status.pack(pady=8)

def update_progress(val, text):
    progress.set(val/100)
    percent_label.configure(text=f"{int(val)}%")
    status.configure(text=text)

def clean_temp():
    def task():
        try:
            temp_path = Path(os.getenv('TEMP'))
            files = list(temp_path.glob('*'))
            total = len(files)
            cleaned_mb = 0
            for i, f in enumerate(files):
                try:
                    if f.is_file():
                        cleaned_mb += f.stat().st_size / (1024*1024)
                        f.unlink()
                    else: shutil.rmtree(f, ignore_errors=True)
                    update_progress((i/total)*100 if total>0 else 100, f"Cleaning {i}/{total}...")
                except: pass
            new_total = save_total(cleaned_mb)
            total_label.configure(text=f"🏆 Total Cleaned: {new_total:.1f} MB | Made in Bangladesh 🇧🇩")
            update_progress(100, f"✅ Cleaned Temp ({cleaned_mb:.1f} MB)!")
        except Exception as e: update_progress(0, f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

def clean_recycle():
    def task():
        try:
            update_progress(30, "Emptying Recycle Bin...")
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            new_total = save_total(5)
            total_label.configure(text=f"🏆 Total Cleaned: {new_total:.1f} MB | Made in Bangladesh 🇧🇩")
            update_progress(100, "✅ Recycle Bin Emptied!")
        except Exception as e: update_progress(0, f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

def clean_browser():
    def task():
        try:
            paths = [Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cache", Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Cache"]
            update_progress(20, "Scanning Browser Cache...")
            total_size = 0
            for p in paths:
                if p.exists():
                    for f in p.rglob('*'):
                        try:
                            if f.is_file():
                                total_size += f.stat().st_size / (1024*1024)
                                f.unlink()
                        except: pass
            new_total = save_total(total_size)
            total_label.configure(text=f"🏆 Total Cleaned: {new_total:.1f} MB | Made in Bangladesh 🇧🇩")
            update_progress(100, f"✅ Browser Cleaned ({total_size:.1f} MB)!")
        except Exception as e: update_progress(0, f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

# --- NEW 1,2,3 ---
def show_startup_manager():
    win = ctk.CTkToplevel(app)
    win.geometry("650x450")
    win.title("🚀 Startup Manager")
    ctk.CTkLabel(win, text="Startup Apps - Disable to Make PC Faster", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
    scroll = ctk.CTkScrollableFrame(win, width=600, height=350)
    scroll.pack(pady=10, padx=10, fill="both", expand=True)
    try:
        apps = []
        for hkey, path in [(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"), (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")]:
            try:
                key = winreg.OpenKey(hkey, path)
                for i in range(winreg.QueryInfoKey(key)[1]):
                    name, val, _ = winreg.EnumValue(key, i)
                    apps.append((name, val, hkey, path))
            except: pass
        for name, val, hkey, path in apps:
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=4, padx=5)
            ctk.CTkLabel(row, text=name[:30], width=200, anchor="w").pack(side="left", padx=10)
            ctk.CTkButton(row, text="Disable", fg_color="#D32F2F", width=80, command=lambda n=name, hk=hkey, p=path: disable_startup(n, hk, p, win)).pack(side="right", padx=10)
    except Exception as e: ctk.CTkLabel(scroll, text=f"Error: {e}").pack()

def disable_startup(name, hkey, path, parent_win):
    try:
        key = winreg.OpenKey(hkey, path, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        messagebox.showinfo("WinHeal", f"✅ {name} Disabled!")
        parent_win.destroy()
        show_startup_manager()
    except Exception as e: messagebox.showerror("Error", f"Failed: {e}")

def real_ram_booster():
    def task():
        try:
            update_progress(10, "⚡ REAL RAM Cleaning...")
            cleaned_count = 0
            for proc in psutil.process_iter(['pid']):
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.info['pid'])
                    if handle:
                        ctypes.windll.psapi.EmptyWorkingSet(handle)
                        ctypes.windll.kernel32.CloseHandle(handle)
                        cleaned_count += 1
                except: pass
            mem = psutil.virtual_memory()
            update_progress(100, f"✅ RAM Boosted! Available: {mem.available // (1024*1024)} MB")
        except Exception as e: update_progress(0, f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

def find_large_files():
    def task():
        try:
            folder = filedialog.askdirectory(title="Select Folder")
            if not folder: return
            update_progress(10, f"Scanning {folder} for >500MB...")
            large = []
            for root, dirs, files in os.walk(folder):
                if "Windows" in root: continue
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        size = os.path.getsize(fp)
                        if size > 500*1024*1024:
                            large.append((fp, size // (1024*1024)))
                    except: pass
            win = ctk.CTkToplevel(app)
            win.geometry("750x500")
            textbox = ctk.CTkTextbox(win, width=700, height=400)
            textbox.pack(pady=10, padx=10, fill="both", expand=True)
            text = "\n".join([f"{mb} MB - {path}" for path, mb in sorted(large, key=lambda x: x[1], reverse=True)]) if large else "✅ No Large Files!"
            textbox.insert("0.0", text)
            update_progress(100, f"✅ Found {len(large)} Large Files!")
        except Exception as e: update_progress(0, f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

def check_update():
    def task():
        try:
            update_progress(10, "Checking for Update...")
            r = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=5)
            if r.status_code == 200:
                latest = r.json().get('tag_name', 'v0.5.0')
                update_progress(100, f"🚀 Update: {latest}!" if latest != APP_VERSION else f"✅ Latest: {APP_VERSION}")
            else: update_progress(0, "No Internet")
        except: update_progress(0, "Update Failed - Offline")
    threading.Thread(target=task, daemon=True).start()

ctk.CTkButton(app, text="🧹 Clean Temp Files", width=480, height=45, fg_color="#00C853", command=clean_temp).pack(pady=6)
ctk.CTkButton(app, text="🗑️ Clean Recycle Bin - REAL", width=480, height=45, fg_color="#D32F2F", command=clean_recycle).pack(pady=6)
ctk.CTkButton(app, text="🌐 Clean Browser Cache - REAL", width=480, height=45, fg_color="#EF6C00", command=clean_browser).pack(pady=6)
ctk.CTkLabel(app, text="--- NEW v0.7.0 LEGEND FEATURES ---", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFD600").pack(pady=(12,4))
ctk.CTkButton(app, text="🚀 1. Startup Manager - Make PC Fast", width=480, height=45, fg_color="#7B1FA2", command=show_startup_manager).pack(pady=6)
ctk.CTkButton(app, text="⚡ 2. RAM Booster - REAL Clean", width=480, height=45, fg_color="#1976D2", command=real_ram_booster).pack(pady=6)
ctk.CTkButton(app, text="📁 3. Large File Finder (>500MB)", width=480, height=45, fg_color="#00796B", command=find_large_files).pack(pady=6)
ctk.CTkButton(app, text="🔄 Check for Update", width=480, height=28, fg_color="#333", command=check_update).pack(pady=10)
ctk.CTkLabel(app, text="Soyen Hasan | github.com/soyenhasan/WinHeal-AI | v0.7.0 LEGEND", font=ctk.CTkFont(size=10), text_color="#666").pack(side="bottom", pady=8)
app.mainloop()