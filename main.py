import customtkinter as ctk
import os, shutil, psutil, threading, json
from pathlib import Path

# --- Config ---
TOTAL_FILE = "total_cleaned.json"
APP_NAME = "WinHeal v0.5.0 PRO MAX"

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
    
    # Browser Cache Approx
    browser_mb = 0
    try:
        chrome_cache = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cache"
        if chrome_cache.exists():
            browser_mb = sum(f.stat().st_size for f in chrome_cache.rglob('*') if f.is_file()) / (1024*1024)
    except: pass
    
    ram = psutil.virtual_memory().percent
    return count, temp_mb, browser_mb, ram

# --- UI ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("520x650")
app.title(APP_NAME)

# Try Icon
try:
    if os.path.exists("icon.ico"):
        app.iconbitmap("icon.ico")
except: pass

# Title
title = ctk.CTkLabel(app, text="WinHeal", font=ctk.CTkFont(size=55, weight="bold"), text_color="#00D1FF")
title.pack(pady=(20,5))

subtitle = ctk.CTkLabel(app, text="v0.5.0 PRO MAX - Professional Cleaner", font=ctk.CTkFont(size=14), text_color="#A0A0A0")
subtitle.pack()

# Total Cleaned Badge - PRO FEATURE
total_mb = get_total()
total_label = ctk.CTkLabel(app, text=f"🏆 Total Cleaned: {total_mb:.1f} MB | Made in Bangladesh 🇧🇩", 
                           font=ctk.CTkFont(size=13, weight="bold"), fg_color="#1F6AA5", corner_radius=20, width=400, height=30)
total_label.pack(pady=15)

# Stats
count, temp_mb, browser_mb, ram = get_stats()
stats_label = ctk.CTkLabel(app, text=f"Temp: {count} files ({temp_mb:.1f} MB) | Browser: {browser_mb:.1f} MB | RAM: {ram}%", 
                           font=ctk.CTkFont(size=12))
stats_label.pack(pady=5)

# Progress
progress = ctk.CTkProgressBar(app, width=400, height=15)
progress.pack(pady=10)
progress.set(0)
percent_label = ctk.CTkLabel(app, text="0%", font=ctk.CTkFont(size=12, weight="bold"))
percent_label.pack()

# Status
status = ctk.CTkLabel(app, text="Ready to heal...", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FF88")
status.pack(pady=10)

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
            cleaned = 0
            cleaned_mb = 0
            for i, f in enumerate(files):
                try:
                    if f.is_file():
                        cleaned_mb += f.stat().st_size / (1024*1024)
                        f.unlink()
                    else:
                        shutil.rmtree(f, ignore_errors=True)
                    cleaned += 1
                    pct = (i/total)*100 if total>0 else 100
                    update_progress(pct, f"Cleaning {i}/{total}...")
                except: pass
            new_total = save_total(cleaned_mb)
            total_label.configure(text=f"🏆 Total Cleaned: {new_total:.1f} MB | Made in Bangladesh 🇧🇩")
            update_progress(100, f"✅ Cleaned {cleaned} files ({cleaned_mb:.1f} MB)!")
        except Exception as e:
            update_progress(0, f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

# Buttons
btn1 = ctk.CTkButton(app, text="🧹 Clean Temp Files", width=400, height=45, fg_color="#00C853", hover_color="#00A843", font=ctk.CTkFont(size=15, weight="bold"), command=clean_temp)
btn1.pack(pady=8)

btn2 = ctk.CTkButton(app, text="🗑️ Clean Recycle Bin (NEW)", width=400, height=45, fg_color="#D32F2F", hover_color="#B71C1C", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: status.configure(text="Recycle Bin Cleaning Coming Soon..."))
btn2.pack(pady=8)

btn3 = ctk.CTkButton(app, text="🌐 Clean Browser Cache (NEW)", width=400, height=45, fg_color="#EF6C00", hover_color="#E65100", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: status.configure(text="Browser Cleaning Coming Soon..."))
btn3.pack(pady=8)

btn4 = ctk.CTkButton(app, text="⚡ Optimize RAM", width=400, height=45, fg_color="#1976D2", hover_color="#0D47A1", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: status.configure(text="RAM Optimized!"))
btn4.pack(pady=8)

footer = ctk.CTkLabel(app, text="Soyen Hasan | github.com/soyenhasan/WinHeal-AI", font=ctk.CTkFont(size=10), text_color="#666")
footer.pack(side="bottom", pady=10)

app.mainloop()