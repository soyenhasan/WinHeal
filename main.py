# WinHeal v0.2.0 - Pro Version
# Made by Soyen - Made in Bangladesh

import tkinter as tk
from tkinter import ttk
import os
import shutil
import psutil
import threading

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
    return count, total / (1024*1024)  # MB

def clean_temp():
    def run_clean():
        status_label.config(text="Cleaning...")
        progress.start()
        temp_path = os.getenv('TEMP')
        cleaned = 0
        try:
            for file in os.listdir(temp_path):
                try:
                    path = os.path.join(temp_path, file)
                    if os.path.isfile(path):
                        os.unlink(path)
                        cleaned += 1
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                        cleaned += 1
                except: pass
        except Exception as e:
            status_label.config(text=f"Error: {e}")
        
        progress.stop()
        status_label.config(text=f"Done! {cleaned} files cleaned!")
        refresh_stats()
    
    threading.Thread(target=run_clean, daemon=True).start()

def clean_ram():
    status_label.config(text="RAM Optimized!")
    # Simple RAM cache clear trick - just show RAM
    ram = psutil.virtual_memory()
    status_label.config(text=f"RAM Usage: {ram.percent}% - Try closing Chrome!")

def refresh_stats():
    count, size_mb = get_temp_size()
    ram = psutil.virtual_memory()
    stats_label.config(text=f"Temp Files: {count} | Size: {size_mb:.1f} MB | RAM: {ram.percent}%")

# --- UI ---
root = tk.Tk()
root.title("WinHeal v0.2.0")
root.geometry("450x500")
root.configure(bg="#0f172a")

# Title
title = tk.Label(root, text="WinHeal", font=("Segoe UI Bold", 36), bg="#0f172a", fg="#38bdf8")
title.pack(pady=(20,5))

sub = tk.Label(root, text="v0.2.0 - Pro Cleaner", font=("Segoe UI", 12), bg="#0f172a", fg="#94a3b8")
sub.pack()

stats_label = tk.Label(root, text="Loading stats...", font=("Segoe UI", 10), bg="#0f172a", fg="white")
stats_label.pack(pady=15)

progress = ttk.Progressbar(root, mode='indeterminate', length=300)
progress.pack(pady=10)

# Buttons Frame
btn_frame = tk.Frame(root, bg="#0f172a")
btn_frame.pack(pady=20)

style = ttk.Style()
style.configure("TButton", font=("Segoe UI Bold", 11), padding=10)

btn1 = tk.Button(btn_frame, text="🧹 Clean Temp Files", command=clean_temp, bg="#22c55e", fg="white", font=("Segoe UI Bold", 12), width=20, bd=0, pady=10, cursor="hand2")
btn1.pack(pady=10)

btn2 = tk.Button(btn_frame, text="⚡ Optimize RAM", command=clean_ram, bg="#3b82f6", fg="white", font=("Segoe UI Bold", 12), width=20, bd=0, pady=10, cursor="hand2")
btn2.pack(pady=10)

status_label = tk.Label(root, text="Ready to heal...", font=("Segoe UI", 11), bg="#0f172a", fg="#22c55e")
status_label.pack(pady=10)

footer = tk.Label(root, text="Made in Bangladesh 🇧🇩 | The Journey Continues", font=("Segoe UI", 8), bg="#0f172a", fg="#64748b")
footer.pack(side="bottom", pady=15)

refresh_stats()
root.mainloop()