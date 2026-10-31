import customtkinter as ctk
import os, shutil, psutil, threading, json, requests, ctypes, winreg
from pathlib import Path
import winshell
from tkinter import messagebox, filedialog

TOTAL_FILE = "total_cleaned.json"
APP_VERSION = "v0.8.0 GLOBAL"
GITHUB_REPO = "soyenhasan/WinHeal-AI"

LANGUAGES = {
    "English": {"title":"WinHeal","subtitle":"v0.8.0 GLOBAL - 10 Languages","total":"Total Cleaned","clean_temp":"🧹 Clean Temp Files","clean_recycle":"🗑️ Clean Recycle Bin - REAL","clean_browser":"🌐 Clean Browser Cache - REAL","startup":"🚀 1. Startup Manager - Make PC Fast","ram_boost":"⚡ 2. RAM Booster - REAL Clean","large_file":"📁 3. Large File Finder (>500MB)","check_update":"🔄 Check for Update","ready":"Ready to heal...","new_features":"--- NEW v0.8.0 GLOBAL FEATURES ---","lang_label":"🌐 Language:"},
    "বাংলা": {"title":"উইনহিল","subtitle":"v0.8.0 গ্লোবাল - ১০ ভাষা","total":"মোট পরিষ্কার","clean_temp":"🧹 টেম্প ফাইল পরিষ্কার","clean_recycle":"🗑️ রিসাইকেল বিন খালি করুন","clean_browser":"🌐 ব্রাউজার ক্যাশ পরিষ্কার","startup":"🚀 ১. স্টার্টআপ ম্যানেজার","ram_boost":"⚡ ২. র‍্যাম বুস্টার - আসল","large_file":"📁 ৩. বড় ফাইল খুঁজুন","check_update":"🔄 আপডেট চেক","ready":"হিল করার জন্য প্রস্তুত...","new_features":"--- নতুন v0.8.0 গ্লোবাল ফিচার ---","lang_label":"🌐 ভাষা:"},
    "हिन्दी": {"title":"विनहील","subtitle":"v0.8.0 ग्लोबल - 10 भाषाएँ","total":"कुल साफ","clean_temp":"🧹 टेम्प फाइलें साफ करें","clean_recycle":"🗑️ रीसायकल बिन खाली करें","clean_browser":"🌐 ब्राउज़र कैश साफ करें","startup":"🚀 1. स्टार्टअप मैनेजर","ram_boost":"⚡ 2. रैम बूस्टर - असली","large_file":"📁 3. बड़ी फाइल खोजें","check_update":"🔄 अपडेट चेक","ready":"तैयार...","new_features":"--- नया v0.8.0 ग्लोबल ---","lang_label":"🌐 भाषा:"},
    "اردو": {"title":"ون ہیل","subtitle":"v0.8.0 گلوبل - 10 زبانیں","total":"کل صاف","clean_temp":"🧹 ٹیمپ صاف کریں","clean_recycle":"🗑️ ری سائیکل بن خالی","clean_browser":"🌐 براؤزر کیش صاف","startup":"🚀 1. اسٹارٹ اپ مینیجر","ram_boost":"⚡ 2. ریم بوسٹر","large_file":"📁 3. بڑی فائل تلاش","check_update":"🔄 اپ ڈیٹ چیک","ready":"تیار...","new_features":"--- نیا v0.8.0 ---","lang_label":"🌐 زبان:"},
    "العربية": {"title":"وين هيل","subtitle":"v0.8.0 عالمي - 10 لغات","total":"إجمالي التنظيف","clean_temp":"🧹 تنظيف الملفات المؤقتة","clean_recycle":"🗑️ إفراغ سلة المهملات","clean_browser":"🌐 تنظيف ذاكرة المتصفح","startup":"🚀 1. مدير بدء التشغيل","ram_boost":"⚡ 2. معزز الرام","large_file":"📁 3. البحث عن الملفات الكبيرة","check_update":"🔄 تحقق من التحديث","ready":"جاهز...","new_features":"--- ميزات v0.8.0 العالمية ---","lang_label":"🌐 اللغة:"},
    "Español": {"title":"WinHeal","subtitle":"v0.8.0 GLOBAL - 10 Idiomas","total":"Total Limpiado","clean_temp":"🧹 Limpiar Archivos Temp","clean_recycle":"🗑️ Vaciar Papelera - REAL","clean_browser":"🌐 Limpiar Caché Navegador","startup":"🚀 1. Gestor de Inicio","ram_boost":"⚡ 2. Potenciador RAM","large_file":"📁 3. Buscador Archivos Grandes","check_update":"🔄 Buscar Actualización","ready":"Listo...","new_features":"--- NUEVO v0.8.0 GLOBAL ---","lang_label":"🌐 Idioma:"},
    "Français": {"title":"WinHeal","subtitle":"v0.8.0 GLOBAL - 10 Langues","total":"Total Nettoyé","clean_temp":"🧹 Nettoyer Fichiers Temp","clean_recycle":"🗑️ Vider Corbeille","clean_browser":"🌐 Nettoyer Cache","startup":"🚀 1. Gestionnaire Démarrage","ram_boost":"⚡ 2. Booster RAM","large_file":"📁 3. Gros Fichiers","check_update":"🔄 Vérifier Mise à Jour","ready":"Prêt...","new_features":"--- NOUVEAU v0.8.0 GLOBAL ---","lang_label":"🌐 Langue:"},
    "Deutsch": {"title":"WinHeal","subtitle":"v0.8.0 GLOBAL - 10 Sprachen","total":"Bereinigt","clean_temp":"🧹 Temp-Dateien Bereinigen","clean_recycle":"🗑️ Papierkorb Leeren","clean_browser":"🌐 Browser-Cache Bereinigen","startup":"🚀 1. Startup Manager","ram_boost":"⚡ 2. RAM Booster","large_file":"📁 3. Große Dateien Finder","check_update":"🔄 Auf Update Prüfen","ready":"Bereit...","new_features":"--- NEU v0.8.0 GLOBAL ---","lang_label":"🌐 Sprache:"},
    "中文": {"title":"WinHeal","subtitle":"v0.8.0 全球版 - 10种语言","total":"总共清理","clean_temp":"🧹 清理临时文件","clean_recycle":"🗑️ 清空回收站","clean_browser":"🌐 清理浏览器缓存","startup":"🚀 1. 启动管理器","ram_boost":"⚡ 2. 内存加速器","large_file":"📁 3. 大文件查找器","check_update":"🔄 检查更新","ready":"准备...","new_features":"--- 新功能 v0.8.0 ---","lang_label":"🌐 语言:"},
    "日本語": {"title":"WinHeal","subtitle":"v0.8.0 グローバル - 10言語","total":"合計クリーン","clean_temp":"🧹 一時ファイルをクリーン","clean_recycle":"🗑️ ごみ箱を空に","clean_browser":"🌐 ブラウザキャッシュ","startup":"🚀 1. スタートアップ管理","ram_boost":"⚡ 2. RAMブースター","large_file":"📁 3. 大きなファイル","check_update":"🔄 アップデート確認","ready":"準備完了...","new_features":"--- 新機能 v0.8.0 ---","lang_label":"🌐 言語:"},
}

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
app.geometry("580x880")
app.title(f"WinHeal {APP_VERSION}")
try:
    if os.path.exists("icon.ico"): app.iconbitmap("icon.ico")
except: pass

current_lang_var = ctk.StringVar(value="English")

title = ctk.CTkLabel(app, text="WinHeal", font=ctk.CTkFont(size=55, weight="bold"), text_color="#00D1FF")
title.pack(pady=(5,2))

lang_frame = ctk.CTkFrame(app, fg_color="transparent")
lang_frame.pack(pady=2, padx=10, anchor="center")
lang_label_widget = ctk.CTkLabel(lang_frame, text="🌐 Language:", font=ctk.CTkFont(size=12, weight="bold"))
lang_label_widget.pack(side="left", padx=5)

subtitle = ctk.CTkLabel(app, text=f"{APP_VERSION} - 1,2,3 NEW ADDED", font=ctk.CTkFont(size=13), text_color="#00FF88")
subtitle.pack()

total_mb = get_total()
total_label = ctk.CTkLabel(app, text=f"🏆 Total Cleaned: {total_mb:.1f} MB | Made in Bangladesh 🇧🇩", font=ctk.CTkFont(size=13, weight="bold"), fg_color="#1F6AA5", corner_radius=20, width=500, height=32)
total_label.pack(pady=8)

count, temp_mb, browser_mb, ram = get_stats()
stats_label = ctk.CTkLabel(app, text=f"Temp: {count} files ({temp_mb:.1f} MB) | Browser: {browser_mb:.1f} MB | RAM: {ram}%", font=ctk.CTkFont(size=12))
stats_label.pack(pady=3)

progress = ctk.CTkProgressBar(app, width=500, height=15)
progress.pack(pady=8)
progress.set(0)
percent_label = ctk.CTkLabel(app, text="0%", font=ctk.CTkFont(size=12, weight="bold"))
percent_label.pack()
status = ctk.CTkLabel(app, text="Ready to heal...", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FF88")
status.pack(pady=5)

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
            t = LANGUAGES[current_lang_var.get()]["total"]
            total_label.configure(text=f"🏆 {t}: {new_total:.1f} MB | Made in Bangladesh 🇧🇩")
            update_progress(100, f"✅ Cleaned Temp ({cleaned_mb:.1f} MB)!")
        except Exception as e: update_progress(0, f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

def clean_recycle():
    def task():
        try:
            update_progress(30, "Emptying Recycle Bin...")
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            new_total = save_total(5)
            t = LANGUAGES[current_lang_var.get()]["total"]
            total_label.configure(text=f"🏆 {t}: {new_total:.1f} MB | Made in Bangladesh 🇧🇩")
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
            t = LANGUAGES[current_lang_var.get()]["total"]
            total_label.configure(text=f"🏆 {t}: {new_total:.1f} MB | Made in Bangladesh 🇧🇩")
            update_progress(100, f"✅ Browser Cleaned ({total_size:.1f} MB)!")
        except Exception as e: update_progress(0, f"Error: {e}")
    threading.Thread(target=task, daemon=True).start()

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
            for proc in psutil.process_iter(['pid']):
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.info['pid'])
                    if handle:
                        ctypes.windll.psapi.EmptyWorkingSet(handle)
                        ctypes.windll.kernel32.CloseHandle(handle)
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

btn_temp = ctk.CTkButton(app, text="🧹 Clean Temp Files", width=500, height=45, fg_color="#00C853", command=clean_temp)
btn_temp.pack(pady=5)
btn_recycle = ctk.CTkButton(app, text="🗑️ Clean Recycle Bin - REAL", width=500, height=45, fg_color="#D32F2F", command=clean_recycle)
btn_recycle.pack(pady=5)
btn_browser = ctk.CTkButton(app, text="🌐 Clean Browser Cache - REAL", width=500, height=45, fg_color="#EF6C00", command=clean_browser)
btn_browser.pack(pady=5)

label_new = ctk.CTkLabel(app, text="--- NEW v0.8.0 GLOBAL FEATURES ---", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFD600")
label_new.pack(pady=(10,4))

btn_startup = ctk.CTkButton(app, text="🚀 1. Startup Manager - Make PC Fast", width=500, height=45, fg_color="#7B1FA2", command=show_startup_manager)
btn_startup.pack(pady=5)
btn_ram = ctk.CTkButton(app, text="⚡ 2. RAM Booster - REAL Clean", width=500, height=45, fg_color="#1976D2", command=real_ram_booster)
btn_ram.pack(pady=5)
btn_large = ctk.CTkButton(app, text="📁 3. Large File Finder (>500MB)", width=500, height=45, fg_color="#00796B", command=find_large_files)
btn_large.pack(pady=5)

btn_update = ctk.CTkButton(app, text="🔄 Check for Update", width=500, height=28, fg_color="#333", command=check_update)
btn_update.pack(pady=10)

footer = ctk.CTkLabel(app, text="Soyen Hasan | github.com/soyenhasan/WinHeal-AI | v0.8.0 GLOBAL", font=ctk.CTkFont(size=10), text_color="#666")
footer.pack(side="bottom", pady=8)

def change_language(choice):
    lang = LANGUAGES[choice]
    title.configure(text=lang["title"])
    subtitle.configure(text=lang["subtitle"])
    lang_label_widget.configure(text=lang["lang_label"])
    btn_temp.configure(text=lang["clean_temp"])
    btn_recycle.configure(text=lang["clean_recycle"])
    btn_browser.configure(text=lang["clean_browser"])
    btn_startup.configure(text=lang["startup"])
    btn_ram.configure(text=lang["ram_boost"])
    btn_large.configure(text=lang["large_file"])
    btn_update.configure(text=lang["check_update"])
    status.configure(text=lang["ready"])
    label_new.configure(text=lang["new_features"])
    total_mb = get_total()
    total_label.configure(text=f"🏆 {lang['total']}: {total_mb:.1f} MB | Made in Bangladesh 🇧🇩")
    app.title(f"WinHeal {APP_VERSION} - {choice}")

lang_menu = ctk.CTkOptionMenu(lang_frame, values=list(LANGUAGES.keys()), variable=current_lang_var, command=change_language, width=160, fg_color="#1F6AA5", button_color="#1F6AA5")
lang_menu.pack(side="left", padx=5)

app.mainloop()