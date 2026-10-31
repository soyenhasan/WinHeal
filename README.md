# WinHeal v0.3.0 ULTRA - Made by Soyen
# Features: Temp + RAM + Recycle Bin + Browser Cache

import tkinter as tk
from tkinter import ttk
import os
import shutil
import psutil
import threading
import subprocess

def get_temp_size():
    temp_path = os.getenv('TEMP')
    total = 0
    count = 0
    try:
        for dirpath, dirnames, filenames in os.walk(temp_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                    count += 1
                except: pass
    except: pass
    return count, total / (1024*1024)

def get_browser_cache_size():
    paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache")
    ]
    total = 0
    for p in paths:
        if os.path.exists(p):
            for dirpath, dirnames, filenames in os.walk(p):
                for f in filenames:
                    try: total += os.path.getsize(os.path.join(dirpath, f))
                    except: pass
    return total / (1024*1024)

def clean_temp_thread():
    def run():
        status_label.config(text="Cleaning Temp Files...")
        progress.start()
        temp_path = os.getenv('TEMP')
        cleaned = 0
        try:
            for file in os.listdir(temp_path):
                try:
                    path = os.path.join(temp_path, file)
                    if os.path.isfile(path): os.unlink(path)
                    else: shutil.rmtree(path)
                    cleaned += 1
                except: pass
        except: pass
        progress.stop()
        status_label.config(text=f"✅ {cleaned} Temp Files Cleaned!")
        refresh_stats()
    threading.Thread(target=run, daemon=True).start()

def clean_recycle_thread():
    def run():
        status_label.config(text="Emptying Recycle Bin...")
        progress.start()
        try:
            # PowerShell command to clear bin silently
            subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force"], capture_output=True)
            status_label.config(text="✅ Recycle Bin Emptied!")
        except Exception as e:
            status_label.config(text=f"Error: {e}")
        progress.stop()
        refresh_stats()
    threading.Thread(target=run, daemon=True).start()

def clean_browser_thread():
    def run():
        status_label.config(text="Cleaning Browser Cache...")
        progress.start()
        paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Code Cache")
        ]
        cleaned = 0
        for p in paths:
            if os.path.exists(p):
                try:
                    shutil.rmtree(p, ignore_errors=True)
                    os.makedirs(p, exist_ok=True)
                    cleaned += 1
                except: pass
        progress.stop()
        status_label.config(text=f"✅ Browser Cache Cleaned! ({cleaned} folders)")
        refresh_stats()
    threading.Thread(target=run, daemon=True).start()

def clean_ram():
    ram = psutil.virtual_memory()
    status_label.config(text=f"RAM: {ram.percent}% Used | Close Chrome for best speed!")

def refresh_stats():
    c, s = get_temp_size()
    b = get_browser_cache_size()
    ram = psutil.virtual_memory()
    stats_label.config(text=f"Temp: {c} files ({s:.1f} MB) | Browser: {b:.1f} MB | RAM: {ram.percent}%")

# --- UI v0.3.0 ---
root = tk.Tk()
root.title("WinHeal v0.3.0 ULTRA")
root.geometry("500x620")
root.configure(bg="#0f172a")

tk.Label(root, text="WinHeal", font=("Segoe UI Bold", 36), bg="#0f172a", fg="#38bdf8").pack(pady=(20,2))
tk.Label(root, text="v0.3.0 ULTRA - The Healing Continues", font=("Segoe UI", 11), bg="#0f172a", fg="#94a3b8").pack()

stats_label = tk.Label(root, text="Loading...", font=("Segoe UI", 10), bg="#0f172a", fg="white")
stats_label.pack(pady=15)

progress = ttk.Progressbar(root, mode='indeterminate', length=350)
progress.pack(pady=5)

btn_frame = tk.Frame(root, bg="#0f172a")
btn_frame.pack(pady=20)

def mk_btn(text, color, cmd):
    return tk.Button(btn_frame, text=text, command=cmd, bg=color, fg="white", font=("Segoe UI Bold", 11), width=28, bd=0, pady=10, cursor="hand2")

mk_btn("🧹 Clean Temp Files", "#22c55e", clean_temp_thread).pack(pady=6)
mk_btn("🗑️ Clean Recycle Bin (NEW)", "#ef4444", clean_recycle_thread).pack(pady=6)
mk_btn("🌐 Clean Browser Cache (NEW)", "#f59e0b", clean_browser_thread).pack(pady=6)
mk_btn("⚡ Optimize RAM", "#3b82f6", clean_ram).pack(pady=6)

status_label = tk.Label(root, text="Ready to heal...", font=("Segoe UI Bold", 11), bg="#0f172a", fg="#22c55e")
status_label.pack(pady=15)

tk.Label(root, text="Made in Bangladesh 🇧🇩 | Soyen Hasan | github.com/soyenhasan/WinHeal-AI", font=("Segoe UI", 8), bg="#0f172a", fg="#64748b").pack(side="bottom", pady=15)

refresh_stats()
root.mainloop()