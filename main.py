"""WinHeal - Windows system care tool.

Every feature in this file does real work. Nothing is simulated.
Languages (10): English, Bangla, Arabic, Hindi, Spanish, Chinese, Portuguese,
French, German, Russian. Add more in STRINGS.
"""
import datetime
import hashlib
import json
import os
import queue
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
import webbrowser
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

VERSION = "0.3.0"
IS_WIN = os.name == "nt"
NO_WINDOW = 0x08000000 if IS_WIN else 0
LOG_DIR = os.path.join(os.path.expanduser("~"), "WinHealLogs")
HIST = 30  # points on the live graph
GITHUB_REPO = "soyenhasan/WinHeal-AI"
LARGE_MB = 500
STATS_FILE = os.path.join(LOG_DIR, "stats.json")
BACKUP_FILE = os.path.join(LOG_DIR, "startup_backup.json")
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
LANG_NAMES = [("en", "English"), ("bn", "বাংলা"), ("ar", "العربية"), ("hi", "हिन्दी"),
              ("es", "Español"), ("zh", "中文"), ("pt", "Português"), ("fr", "Français"),
              ("de", "Deutsch"), ("ru", "Русский")]

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
        "menu_browser": "Browser Cache Cleaner",
        "menu_large": "Large File Finder",
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
        "net_down": "Result: no internet. Check Wi-Fi/cable and router, then restart the router.",
        "flush_dns": "Flush DNS cache", "dns_flushed": "DNS cache flushed.",
        "startup_none": "No startup entries found.",
        "startup_note": "You can disable any entry here and restore it later.",
        "open_startup": "Open Startup settings",
        "startup_disable": "Disable", "startup_restore": "Restore",
        "startup_disabled_title": "Disabled by WinHeal (can be restored):",
        "startup_confirm": "Disable '{name}' at startup?\nYou can restore it later from this window.",
        "startup_disabled_ok": "'{name}' disabled.",
        "startup_restored_ok": "'{name}' restored.",
        "startup_admin": "Administrator rights are needed for this entry. Run WinHeal as Administrator.",
        "startup_failed": "Failed: {err}",
        "junk_found": "Found {n} temp files older than 24 hours, total {size}.",
        "junk_none": "No old temp files to clean.",
        "delete_now": "Delete these files",
        "confirm_delete": "Delete {n} files ({size})?\nThis cannot be undone.",
        "junk_done": "Deleted {n} files, freed {size}. {f} skipped (in use or protected).",
        "browser_found": "Found {size} of browser cache in {n} files (Chrome/Edge/Brave).",
        "browser_none": "No browser cache found.",
        "browser_note": "Close your browsers first for best results. Passwords and bookmarks are not touched.",
        "large_pick": "Choose a folder to scan",
        "large_scanning": "Scanning {folder} for files over 500 MB ...",
        "large_none": "No files over 500 MB found.",
        "large_found": "{n} large files found. WinHeal deletes nothing.",
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
        "total_cleaned": "Total cleaned: {size}",
        "check_update": "Check for update",
        "update_available": "Version {latest} is available (you have {current}). Open the download page?",
        "up_to_date": "You have the latest version ({current}).",
        "no_release": "No release has been published yet.",
        "update_failed": "Could not check for updates: {err}",
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
        "menu_browser": "ব্রাউজার ক্যাশ ক্লিনার",
        "menu_large": "বড় ফাইল খোঁজা",
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
        "startup_note": "এখানে যেকোনো এন্ট্রি বন্ধ করতে পারবেন এবং পরে ফিরিয়ে আনতে পারবেন।",
        "open_startup": "স্টার্টআপ সেটিংস খুলুন",
        "startup_disable": "বন্ধ করুন", "startup_restore": "ফিরিয়ে আনুন",
        "startup_disabled_title": "WinHeal বন্ধ করেছে (ফেরানো যাবে):",
        "startup_confirm": "স্টার্টআপে '{name}' বন্ধ করবেন?\nপরে এই উইন্ডো থেকে ফিরিয়ে আনতে পারবেন।",
        "startup_disabled_ok": "'{name}' বন্ধ হয়েছে।",
        "startup_restored_ok": "'{name}' ফিরিয়ে আনা হয়েছে।",
        "startup_admin": "এই এন্ট্রির জন্য অ্যাডমিনিস্ট্রেটর অনুমতি লাগবে। WinHeal-কে অ্যাডমিনিস্ট্রেটর হিসেবে চালান।",
        "startup_failed": "ব্যর্থ: {err}",
        "junk_found": "২৪ ঘণ্টার পুরনো {n}টি টেম্প ফাইল পাওয়া গেছে, মোট {size}।",
        "junk_none": "পরিষ্কার করার মতো পুরনো টেম্প ফাইল নেই।",
        "delete_now": "ফাইলগুলো মুছুন",
        "confirm_delete": "{n}টি ফাইল ({size}) মুছবেন?\nএটা ফেরানো যাবে না।",
        "junk_done": "{n}টি ফাইল মুছে {size} জায়গা খালি হয়েছে। {f}টি বাদ গেছে (ব্যবহারে ছিল বা সুরক্ষিত)।",
        "browser_found": "{n}টি ফাইলে {size} ব্রাউজার ক্যাশ পাওয়া গেছে (Chrome/Edge/Brave)।",
        "browser_none": "কোনো ব্রাউজার ক্যাশ পাওয়া যায়নি।",
        "browser_note": "ভালো ফলাফলের জন্য আগে ব্রাউজার বন্ধ করুন। পাসওয়ার্ড ও বুকমার্কে হাত দেওয়া হয় না।",
        "large_pick": "স্ক্যান করার জন্য ফোল্ডার বেছে নিন",
        "large_scanning": "{folder}-এ ৫০০ MB-এর বড় ফাইল খোঁজা হচ্ছে ...",
        "large_none": "৫০০ MB-এর বড় কোনো ফাইল পাওয়া যায়নি।",
        "large_found": "{n}টি বড় ফাইল পাওয়া গেছে। WinHeal কিছুই মোছে না।",
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
        "total_cleaned": "মোট পরিষ্কার: {size}",
        "check_update": "আপডেট চেক করুন",
        "update_available": "{latest} সংস্করণ পাওয়া যাচ্ছে (আপনার আছে {current})। ডাউনলোড পেজ খুলবেন?",
        "up_to_date": "আপনার কাছে সর্বশেষ সংস্করণ ({current}) আছে।",
        "no_release": "এখনো কোনো রিলিজ প্রকাশ হয়নি।",
        "update_failed": "আপডেট চেক করা যায়নি: {err}",
    },
    "ar": {
        "app_title": "WinHeal - أداة العناية بالنظام",
        "menu_diag": "تشخيص النظام",
        "menu_files": "مستكشف الملفات والأقراص",
        "menu_net": "استكشاف أخطاء الشبكة",
        "menu_startup": "برامج بدء التشغيل",
        "menu_dups": "البحث عن الملفات المكررة",
        "menu_updates": "تحديثات البرامج",
        "menu_junk": "منظف الملفات المؤقتة",
        "menu_browser": "منظف ذاكرة المتصفح",
        "menu_large": "البحث عن الملفات الكبيرة",
        "menu_bin": "إفراغ سلة المحذوفات",
        "menu_bench": "اختبار أداء سريع",
        "menu_report": "تصدير تقرير النظام",
        "theme": "السمة", "language": "اللغة", "custom": "مخصص", "quit": "خروج",
        "dashboard": "لوحة النظام",
        "status_ok": "● حمل النظام: طبيعي",
        "status_warn": "● حمل النظام: مرتفع",
        "cpu": "المعالج", "ram": "الذاكرة", "disk": "القرص", "battery": "البطارية",
        "no_battery": "لا توجد بطارية", "charging": "موصول بالكهرباء", "on_battery": "يعمل بالبطارية",
        "graph_title": "المعالج والذاكرة مباشرة", "log_title": "سجل النشاط",
        "close": "إغلاق", "working": "جارٍ العمل...", "error": "خطأ",
        "windows_only": "هذه الميزة تعمل على Windows فقط.",
        "threads": "خيوط", "free": "متاح", "started": "تم تشغيل WinHeal.",
        "issue_cpu": "استخدام المعالج مرتفع جدًا. أغلق البرامج الثقيلة.",
        "issue_ram": "استخدام الذاكرة مرتفع جدًا. أغلق البرامج غير المستخدمة أو أعد التشغيل.",
        "issue_disk": "القرص ممتلئ تقريبًا. استخدم منظف الملفات أو البحث عن المكررات.",
        "issue_battery": "البطارية منخفضة ولا تُشحن.",
        "issue_uptime": "لم يُعاد تشغيل الجهاز منذ {d} يومًا. قد تفيد إعادة التشغيل.",
        "no_issues": "لم يتم العثور على مشاكل. نظامك يبدو سليمًا.",
        "found_issues": "مشاكل محتملة:",
        "top_procs": "أكثر البرامج استهلاكًا للذاكرة:",
        "uptime": "مدة التشغيل",
        "host": "اسم الكمبيوتر", "local_ip": "عنوان IP المحلي", "sent": "البيانات المرسلة",
        "received": "البيانات المستلمة", "ping_test": "اختبار الإنترنت (8.8.8.8)",
        "dns_test": "فحص DNS (example.com)", "ok": "جيد", "failed": "فشل",
        "net_ok": "النتيجة: الاتصال سليم.",
        "net_dns": "النتيجة: الإنترنت متاح لكن DNS لا يعمل. جرّب مسح ذاكرة DNS أو غيّر خادم DNS.",
        "net_down": "النتيجة: لا يوجد إنترنت. افحص الواي فاي أو الكابل والراوتر، ثم أعد تشغيل الراوتر.",
        "flush_dns": "مسح ذاكرة DNS", "dns_flushed": "تم مسح ذاكرة DNS.",
        "startup_none": "لا توجد عناصر بدء تشغيل.",
        "startup_note": "يمكنك تعطيل أي عنصر هنا وإعادته لاحقًا.",
        "open_startup": "فتح إعدادات بدء التشغيل",
        "startup_disable": "تعطيل", "startup_restore": "استعادة",
        "startup_disabled_title": "معطّل بواسطة WinHeal (يمكن استعادته):",
        "startup_confirm": "تعطيل '{name}' عند بدء التشغيل؟\nيمكنك استعادته لاحقًا من هذه النافذة.",
        "startup_disabled_ok": "تم تعطيل '{name}'.",
        "startup_restored_ok": "تمت استعادة '{name}'.",
        "startup_admin": "هذا العنصر يحتاج صلاحيات المسؤول. شغّل WinHeal كمسؤول.",
        "startup_failed": "فشل: {err}",
        "junk_found": "تم العثور على {n} ملفًا مؤقتًا أقدم من 24 ساعة، بحجم {size}.",
        "junk_none": "لا توجد ملفات مؤقتة قديمة للتنظيف.",
        "delete_now": "حذف هذه الملفات",
        "confirm_delete": "حذف {n} ملفًا ({size})؟\nلا يمكن التراجع عن ذلك.",
        "junk_done": "تم حذف {n} ملفًا وتحرير {size}. تم تخطي {f} (قيد الاستخدام أو محمية).",
        "browser_found": "تم العثور على {size} من ذاكرة المتصفح في {n} ملفًا (Chrome/Edge/Brave).",
        "browser_none": "لم يتم العثور على ذاكرة متصفح.",
        "browser_note": "أغلق المتصفحات أولًا للحصول على أفضل نتيجة. لا يتم المساس بكلمات المرور والإشارات المرجعية.",
        "large_pick": "اختر مجلدًا للفحص",
        "large_scanning": "جارٍ فحص {folder} بحثًا عن ملفات أكبر من 500 ميجابايت ...",
        "large_none": "لا توجد ملفات أكبر من 500 ميجابايت.",
        "large_found": "تم العثور على {n} ملفًا كبيرًا. WinHeal لا يحذف شيئًا.",
        "bin_confirm": "إفراغ سلة المحذوفات نهائيًا؟ لا يمكن التراجع.",
        "bin_done": "تم إفراغ سلة المحذوفات.",
        "dups_pick": "اختر مجلدًا للبحث عن المكررات",
        "dups_scanning": "جارٍ فحص {folder} ...",
        "dups_none": "لا توجد ملفات مكررة (الملفات الأصغر من 1 كيلوبايت متجاهلة).",
        "dups_summary": "{g} مجموعة من الملفات المتطابقة. المساحة القابلة للتوفير: {size}.",
        "dups_note": "WinHeal لا يحذف شيئًا. راجع القائمة واحذف النسخ بنفسك.",
        "wg_missing": "لم يتم العثور على winget. ثبّت 'App Installer' من Microsoft Store.",
        "wg_hint": "لتحديث كل شيء، شغّل في الطرفية: winget upgrade --all",
        "bench_cpu": "زمن اختبار المعالج: {s:.2f} ثانية (الأقل أسرع)",
        "bench_disk": "سرعة الكتابة على القرص: {mb:.0f} ميجابايت/ث",
        "bench_note": "اختبارات بسيطة تقريبية، لا تُقارن بالاختبارات الاحترافية.",
        "report_saved": "تم حفظ التقرير: {path}",
        "parent_dir": "[..] المجلد الأعلى", "col_name": "الاسم", "col_type": "النوع",
        "col_size": "الحجم", "folder": "مجلد", "file": "ملف", "home": "الرئيسية",
        "browse": "استعراض...", "copy_ask": "نسخ '{name}' إلى مجلد آخر؟",
        "copy_done": "تم النسخ إلى: {dest}", "path": "المسار",
        "total_cleaned": "إجمالي ما تم تنظيفه: {size}",
        "check_update": "التحقق من التحديث",
        "update_available": "الإصدار {latest} متاح (لديك {current}). فتح صفحة التنزيل؟",
        "up_to_date": "لديك أحدث إصدار ({current}).",
        "no_release": "لم يتم نشر أي إصدار بعد.",
        "update_failed": "تعذر التحقق من التحديثات: {err}",
    },
    "hi": {
        "app_title": "WinHeal - सिस्टम केयर टूल",
        "menu_diag": "सिस्टम डायग्नोस्टिक्स",
        "menu_files": "फ़ाइल और ड्राइव एक्सप्लोरर",
        "menu_net": "नेटवर्क समस्या समाधान",
        "menu_startup": "स्टार्टअप प्रोग्राम",
        "menu_dups": "डुप्लिकेट फ़ाइल खोजक",
        "menu_updates": "सॉफ़्टवेयर अपडेट",
        "menu_junk": "जंक फ़ाइल क्लीनर",
        "menu_browser": "ब्राउज़र कैश क्लीनर",
        "menu_large": "बड़ी फ़ाइलें खोजें",
        "menu_bin": "रीसायकल बिन खाली करें",
        "menu_bench": "त्वरित बेंचमार्क",
        "menu_report": "सिस्टम रिपोर्ट निर्यात करें",
        "theme": "थीम", "language": "भाषा", "custom": "कस्टम", "quit": "बाहर निकलें",
        "dashboard": "सिस्टम डैशबोर्ड",
        "status_ok": "● सिस्टम लोड: सामान्य",
        "status_warn": "● सिस्टम लोड: अधिक",
        "cpu": "CPU", "ram": "मेमोरी", "disk": "डिस्क", "battery": "बैटरी",
        "no_battery": "बैटरी नहीं है", "charging": "चार्जर लगा है", "on_battery": "बैटरी पर चल रहा है",
        "graph_title": "लाइव CPU और मेमोरी", "log_title": "गतिविधि लॉग",
        "close": "बंद करें", "working": "काम चल रहा है...", "error": "त्रुटि",
        "windows_only": "यह सुविधा केवल Windows पर चलती है।",
        "threads": "थ्रेड", "free": "खाली", "started": "WinHeal शुरू हो गया।",
        "issue_cpu": "CPU उपयोग बहुत अधिक है। भारी प्रोग्राम बंद करें।",
        "issue_ram": "मेमोरी उपयोग बहुत अधिक है। अनावश्यक प्रोग्राम बंद करें या रीस्टार्ट करें।",
        "issue_disk": "डिस्क लगभग भर गई है। जंक क्लीनर या डुप्लिकेट खोजक का उपयोग करें।",
        "issue_battery": "बैटरी कम है और चार्ज नहीं हो रही।",
        "issue_uptime": "पीसी {d} दिनों से रीस्टार्ट नहीं हुआ। रीस्टार्ट करने से मदद मिल सकती है।",
        "no_issues": "कोई समस्या नहीं मिली। आपका सिस्टम ठीक दिखता है।",
        "found_issues": "संभावित समस्याएँ:",
        "top_procs": "सबसे अधिक मेमोरी उपयोग करने वाले:",
        "uptime": "चालू रहने का समय",
        "host": "कंप्यूटर का नाम", "local_ip": "लोकल IP", "sent": "भेजा गया डेटा",
        "received": "प्राप्त डेटा", "ping_test": "इंटरनेट पिंग (8.8.8.8)",
        "dns_test": "DNS जाँच (example.com)", "ok": "ठीक", "failed": "विफल",
        "net_ok": "परिणाम: कनेक्शन ठीक है।",
        "net_dns": "परिणाम: इंटरनेट है लेकिन DNS काम नहीं कर रहा। DNS कैश साफ़ करें या DNS सर्वर बदलें।",
        "net_down": "परिणाम: इंटरनेट नहीं है। वाई-फ़ाई/केबल और राउटर जाँचें, फिर राउटर रीस्टार्ट करें।",
        "flush_dns": "DNS कैश साफ़ करें", "dns_flushed": "DNS कैश साफ़ हो गया।",
        "startup_none": "कोई स्टार्टअप प्रविष्टि नहीं मिली।",
        "startup_note": "आप यहाँ किसी भी प्रविष्टि को बंद कर सकते हैं और बाद में वापस ला सकते हैं।",
        "open_startup": "स्टार्टअप सेटिंग्स खोलें",
        "startup_disable": "बंद करें", "startup_restore": "वापस लाएँ",
        "startup_disabled_title": "WinHeal द्वारा बंद (वापस लाया जा सकता है):",
        "startup_confirm": "स्टार्टअप पर '{name}' बंद करें?\nआप इसे बाद में इसी विंडो से वापस ला सकते हैं।",
        "startup_disabled_ok": "'{name}' बंद कर दिया गया।",
        "startup_restored_ok": "'{name}' वापस चालू किया गया।",
        "startup_admin": "इस प्रविष्टि के लिए एडमिनिस्ट्रेटर अधिकार चाहिए। WinHeal को एडमिनिस्ट्रेटर के रूप में चलाएँ।",
        "startup_failed": "विफल: {err}",
        "junk_found": "24 घंटे से पुरानी {n} अस्थायी फ़ाइलें मिलीं, कुल {size}।",
        "junk_none": "साफ़ करने के लिए कोई पुरानी अस्थायी फ़ाइल नहीं है।",
        "delete_now": "ये फ़ाइलें हटाएँ",
        "confirm_delete": "{n} फ़ाइलें ({size}) हटाएँ?\nइसे वापस नहीं किया जा सकता।",
        "junk_done": "{n} फ़ाइलें हटाईं, {size} जगह खाली हुई। {f} छोड़ी गईं (उपयोग में या सुरक्षित)।",
        "browser_found": "{n} फ़ाइलों में {size} ब्राउज़र कैश मिला (Chrome/Edge/Brave)।",
        "browser_none": "कोई ब्राउज़र कैश नहीं मिला।",
        "browser_note": "बेहतर परिणाम के लिए पहले ब्राउज़र बंद करें। पासवर्ड और बुकमार्क को नहीं छुआ जाता।",
        "large_pick": "स्कैन करने के लिए फ़ोल्डर चुनें",
        "large_scanning": "{folder} में 500 MB से बड़ी फ़ाइलें खोजी जा रही हैं ...",
        "large_none": "500 MB से बड़ी कोई फ़ाइल नहीं मिली।",
        "large_found": "{n} बड़ी फ़ाइलें मिलीं। WinHeal कुछ नहीं हटाता।",
        "bin_confirm": "रीसायकल बिन हमेशा के लिए खाली करें? इसे वापस नहीं किया जा सकता।",
        "bin_done": "रीसायकल बिन खाली हो गया।",
        "dups_pick": "डुप्लिकेट खोजने के लिए फ़ोल्डर चुनें",
        "dups_scanning": "{folder} स्कैन हो रहा है ...",
        "dups_none": "कोई डुप्लिकेट फ़ाइल नहीं मिली (1 KB से छोटी फ़ाइलें छोड़ी गईं)।",
        "dups_summary": "{g} समूह एक जैसी फ़ाइलों के। बचाई जा सकने वाली जगह: {size}।",
        "dups_note": "WinHeal कुछ नहीं हटाता। सूची देखकर प्रतियाँ खुद हटाएँ।",
        "wg_missing": "winget नहीं मिला। Microsoft Store से 'App Installer' इंस्टॉल करें।",
        "wg_hint": "सब कुछ अपडेट करने के लिए टर्मिनल में चलाएँ: winget upgrade --all",
        "bench_cpu": "CPU टेस्ट समय: {s:.2f} सेकंड (कम मतलब तेज़)",
        "bench_disk": "डिस्क लिखने की गति: {mb:.0f} MB/s",
        "bench_note": "ये सरल अनुमानित टेस्ट हैं, पेशेवर बेंचमार्क से तुलनीय नहीं।",
        "report_saved": "रिपोर्ट सहेजी गई: {path}",
        "parent_dir": "[..] ऊपरी फ़ोल्डर", "col_name": "नाम", "col_type": "प्रकार",
        "col_size": "आकार", "folder": "फ़ोल्डर", "file": "फ़ाइल", "home": "होम",
        "browse": "चुनें...", "copy_ask": "'{name}' को दूसरे फ़ोल्डर में कॉपी करें?",
        "copy_done": "यहाँ कॉपी किया गया: {dest}", "path": "पाथ",
        "total_cleaned": "कुल साफ़ किया गया: {size}",
        "check_update": "अपडेट जाँचें",
        "update_available": "संस्करण {latest} उपलब्ध है (आपके पास {current} है)। डाउनलोड पेज खोलें?",
        "up_to_date": "आपके पास नवीनतम संस्करण ({current}) है।",
        "no_release": "अभी तक कोई रिलीज़ प्रकाशित नहीं हुई है।",
        "update_failed": "अपडेट जाँचा नहीं जा सका: {err}",
    },
    "es": {
        "app_title": "WinHeal - Herramienta de mantenimiento",
        "menu_diag": "Diagnóstico del sistema",
        "menu_files": "Explorador de archivos y unidades",
        "menu_net": "Solucionador de red",
        "menu_startup": "Programas de inicio",
        "menu_dups": "Buscador de archivos duplicados",
        "menu_updates": "Actualizaciones de software",
        "menu_junk": "Limpiador de archivos basura",
        "menu_browser": "Limpiador de caché del navegador",
        "menu_large": "Buscador de archivos grandes",
        "menu_bin": "Vaciar la papelera",
        "menu_bench": "Prueba rápida de rendimiento",
        "menu_report": "Exportar informe del sistema",
        "theme": "TEMA", "language": "IDIOMA", "custom": "Personalizado", "quit": "Salir",
        "dashboard": "PANEL DEL SISTEMA",
        "status_ok": "● Carga del sistema: normal",
        "status_warn": "● Carga del sistema: alta",
        "cpu": "CPU", "ram": "MEMORIA", "disk": "DISCO", "battery": "BATERÍA",
        "no_battery": "Sin batería", "charging": "Conectado a la corriente", "on_battery": "Con batería",
        "graph_title": "CPU y memoria en vivo", "log_title": "Registro de actividad",
        "close": "Cerrar", "working": "Trabajando...", "error": "Error",
        "windows_only": "Esta función solo funciona en Windows.",
        "threads": "hilos", "free": "libre", "started": "WinHeal iniciado.",
        "issue_cpu": "El uso de CPU es muy alto. Cierra programas pesados.",
        "issue_ram": "El uso de memoria es muy alto. Cierra programas que no uses o reinicia.",
        "issue_disk": "El disco está casi lleno. Usa el limpiador de basura o el buscador de duplicados.",
        "issue_battery": "La batería está baja y no se está cargando.",
        "issue_uptime": "El PC no se reinicia desde hace {d} días. Reiniciar puede ayudar.",
        "no_issues": "No se encontraron problemas. Tu sistema se ve saludable.",
        "found_issues": "Posibles problemas:",
        "top_procs": "Mayor uso de memoria:",
        "uptime": "Tiempo encendido",
        "host": "Nombre del equipo", "local_ip": "IP local", "sent": "Datos enviados",
        "received": "Datos recibidos", "ping_test": "Ping a internet (8.8.8.8)",
        "dns_test": "Consulta DNS (example.com)", "ok": "OK", "failed": "FALLÓ",
        "net_ok": "Resultado: la conexión se ve saludable.",
        "net_dns": "Resultado: hay internet pero el DNS falla. Prueba 'Vaciar caché DNS' o cambia el servidor DNS.",
        "net_down": "Resultado: sin internet. Revisa el Wi-Fi o el cable y el router, y reinicia el router.",
        "flush_dns": "Vaciar caché DNS", "dns_flushed": "Caché DNS vaciada.",
        "startup_none": "No hay entradas de inicio.",
        "startup_note": "Puedes desactivar cualquier entrada aquí y restaurarla después.",
        "open_startup": "Abrir configuración de inicio",
        "startup_disable": "Desactivar", "startup_restore": "Restaurar",
        "startup_disabled_title": "Desactivadas por WinHeal (se pueden restaurar):",
        "startup_confirm": "¿Desactivar '{name}' al iniciar?\nPuedes restaurarla después desde esta ventana.",
        "startup_disabled_ok": "'{name}' desactivada.",
        "startup_restored_ok": "'{name}' restaurada.",
        "startup_admin": "Esta entrada requiere permisos de administrador. Ejecuta WinHeal como administrador.",
        "startup_failed": "Error: {err}",
        "junk_found": "Se encontraron {n} archivos temporales de más de 24 horas, en total {size}.",
        "junk_none": "No hay archivos temporales antiguos que limpiar.",
        "delete_now": "Eliminar estos archivos",
        "confirm_delete": "¿Eliminar {n} archivos ({size})?\nEsto no se puede deshacer.",
        "junk_done": "Se eliminaron {n} archivos y se liberaron {size}. Se omitieron {f} (en uso o protegidos).",
        "browser_found": "Se encontraron {size} de caché del navegador en {n} archivos (Chrome/Edge/Brave).",
        "browser_none": "No se encontró caché del navegador.",
        "browser_note": "Cierra los navegadores antes para mejores resultados. No se tocan contraseñas ni marcadores.",
        "large_pick": "Elige una carpeta para analizar",
        "large_scanning": "Buscando archivos de más de 500 MB en {folder} ...",
        "large_none": "No se encontraron archivos de más de 500 MB.",
        "large_found": "Se encontraron {n} archivos grandes. WinHeal no elimina nada.",
        "bin_confirm": "¿Vaciar la papelera de forma permanente? No se puede deshacer.",
        "bin_done": "Papelera vaciada.",
        "dups_pick": "Elige una carpeta para buscar duplicados",
        "dups_scanning": "Analizando {folder} ...",
        "dups_none": "No se encontraron duplicados (se ignoran archivos de menos de 1 KB).",
        "dups_summary": "{g} grupos de archivos idénticos. Espacio recuperable: {size}.",
        "dups_note": "WinHeal no elimina nada. Revisa la lista y borra las copias tú mismo.",
        "wg_missing": "No se encontró winget. Instala 'Instalador de aplicación' desde Microsoft Store.",
        "wg_hint": "Para actualizar todo, ejecuta en una terminal: winget upgrade --all",
        "bench_cpu": "Tiempo de prueba de CPU: {s:.2f} s (menos es más rápido)",
        "bench_disk": "Velocidad de escritura en disco: {mb:.0f} MB/s",
        "bench_note": "Pruebas simples y orientativas. No comparables con pruebas profesionales.",
        "report_saved": "Informe guardado: {path}",
        "parent_dir": "[..] Carpeta superior", "col_name": "Nombre", "col_type": "Tipo",
        "col_size": "Tamaño", "folder": "Carpeta", "file": "Archivo", "home": "Inicio",
        "browse": "Examinar...", "copy_ask": "¿Copiar '{name}' a otra carpeta?",
        "copy_done": "Copiado en: {dest}", "path": "Ruta",
        "total_cleaned": "Total limpiado: {size}",
        "check_update": "Buscar actualización",
        "update_available": "La versión {latest} está disponible (tienes {current}). ¿Abrir la página de descarga?",
        "up_to_date": "Tienes la última versión ({current}).",
        "no_release": "Aún no se ha publicado ninguna versión.",
        "update_failed": "No se pudo buscar actualizaciones: {err}",
    },
    "zh": {
        "app_title": "WinHeal - 系统维护工具",
        "menu_diag": "系统诊断",
        "menu_files": "文件与磁盘浏览器",
        "menu_net": "网络故障排查",
        "menu_startup": "启动程序",
        "menu_dups": "重复文件查找",
        "menu_updates": "软件更新",
        "menu_junk": "垃圾文件清理",
        "menu_browser": "浏览器缓存清理",
        "menu_large": "大文件查找",
        "menu_bin": "清空回收站",
        "menu_bench": "快速测试",
        "menu_report": "导出系统报告",
        "theme": "主题", "language": "语言", "custom": "自定义", "quit": "退出",
        "dashboard": "系统仪表板",
        "status_ok": "● 系统负载：正常",
        "status_warn": "● 系统负载：偏高",
        "cpu": "CPU", "ram": "内存", "disk": "磁盘", "battery": "电池",
        "no_battery": "无电池", "charging": "已接通电源", "on_battery": "使用电池",
        "graph_title": "实时 CPU 与内存", "log_title": "活动日志",
        "close": "关闭", "working": "处理中...", "error": "错误",
        "windows_only": "此功能仅支持 Windows。",
        "threads": "线程", "free": "可用", "started": "WinHeal 已启动。",
        "issue_cpu": "CPU 使用率过高，请关闭占用大的程序。",
        "issue_ram": "内存使用率过高，请关闭不用的程序或重启。",
        "issue_disk": "磁盘几乎已满，请使用垃圾清理或重复文件查找。",
        "issue_battery": "电量低且未在充电。",
        "issue_uptime": "电脑已 {d} 天未重启，重启可能有帮助。",
        "no_issues": "未发现问题，系统状态良好。",
        "found_issues": "可能的问题：",
        "top_procs": "内存占用最多的程序：",
        "uptime": "运行时间",
        "host": "计算机名", "local_ip": "本机 IP", "sent": "已发送数据",
        "received": "已接收数据", "ping_test": "互联网 Ping (8.8.8.8)",
        "dns_test": "DNS 解析 (example.com)", "ok": "正常", "failed": "失败",
        "net_ok": "结果：连接正常。",
        "net_dns": "结果：可上网但 DNS 解析失败。请尝试刷新 DNS 缓存或更换 DNS 服务器。",
        "net_down": "结果：无法上网。请检查 Wi-Fi/网线和路由器，并重启路由器。",
        "flush_dns": "刷新 DNS 缓存", "dns_flushed": "DNS 缓存已刷新。",
        "startup_none": "没有启动项。",
        "startup_note": "你可以在这里停用任意启动项，之后也能恢复。",
        "open_startup": "打开启动设置",
        "startup_disable": "停用", "startup_restore": "恢复",
        "startup_disabled_title": "已被 WinHeal 停用（可恢复）：",
        "startup_confirm": "开机时停用“{name}”？\n之后可以在此窗口恢复。",
        "startup_disabled_ok": "已停用“{name}”。",
        "startup_restored_ok": "已恢复“{name}”。",
        "startup_admin": "此项需要管理员权限，请以管理员身份运行 WinHeal。",
        "startup_failed": "失败：{err}",
        "junk_found": "发现 {n} 个超过 24 小时的临时文件，共 {size}。",
        "junk_none": "没有需要清理的旧临时文件。",
        "delete_now": "删除这些文件",
        "confirm_delete": "删除 {n} 个文件（{size}）？\n此操作无法撤销。",
        "junk_done": "已删除 {n} 个文件，释放 {size}。跳过 {f} 个（正在使用或受保护）。",
        "browser_found": "在 {n} 个文件中发现 {size} 浏览器缓存（Chrome/Edge/Brave）。",
        "browser_none": "未发现浏览器缓存。",
        "browser_note": "建议先关闭浏览器以获得最佳效果。不会触及密码和书签。",
        "large_pick": "选择要扫描的文件夹",
        "large_scanning": "正在 {folder} 中查找超过 500 MB 的文件 ...",
        "large_none": "未发现超过 500 MB 的文件。",
        "large_found": "发现 {n} 个大文件。WinHeal 不会删除任何内容。",
        "bin_confirm": "永久清空回收站？此操作无法撤销。",
        "bin_done": "回收站已清空。",
        "dups_pick": "选择要查找重复文件的文件夹",
        "dups_scanning": "正在扫描 {folder} ...",
        "dups_none": "未发现重复文件（忽略小于 1 KB 的文件）。",
        "dups_summary": "共 {g} 组相同文件，可回收空间：{size}。",
        "dups_note": "WinHeal 不会删除任何内容，请查看列表后自行删除副本。",
        "wg_missing": "未找到 winget。请从 Microsoft Store 安装“应用安装程序”。",
        "wg_hint": "更新全部软件，请在终端运行：winget upgrade --all",
        "bench_cpu": "CPU 测试用时：{s:.2f} 秒（越短越快）",
        "bench_disk": "磁盘写入速度：{mb:.0f} MB/s",
        "bench_note": "这是简单的参考测试，不能与专业基准测试相比。",
        "report_saved": "报告已保存：{path}",
        "parent_dir": "[..] 上级文件夹", "col_name": "名称", "col_type": "类型",
        "col_size": "大小", "folder": "文件夹", "file": "文件", "home": "主目录",
        "browse": "浏览...", "copy_ask": "将“{name}”复制到其他文件夹？",
        "copy_done": "已复制到：{dest}", "path": "路径",
        "total_cleaned": "累计清理：{size}",
        "check_update": "检查更新",
        "update_available": "有新版本 {latest}（当前 {current}）。是否打开下载页面？",
        "up_to_date": "已是最新版本（{current}）。",
        "no_release": "尚未发布任何版本。",
        "update_failed": "无法检查更新：{err}",
    },
    "pt": {
        "app_title": "WinHeal - Ferramenta de cuidados do sistema",
        "menu_diag": "Diagnóstico do sistema",
        "menu_files": "Explorador de arquivos e unidades",
        "menu_net": "Solução de problemas de rede",
        "menu_startup": "Programas de inicialização",
        "menu_dups": "Localizador de arquivos duplicados",
        "menu_updates": "Atualizações de software",
        "menu_junk": "Limpeza de arquivos inúteis",
        "menu_browser": "Limpeza de cache do navegador",
        "menu_large": "Localizador de arquivos grandes",
        "menu_bin": "Esvaziar a lixeira",
        "menu_bench": "Teste rápido de desempenho",
        "menu_report": "Exportar relatório do sistema",
        "theme": "TEMA", "language": "IDIOMA", "custom": "Personalizar", "quit": "Sair",
        "dashboard": "PAINEL DO SISTEMA",
        "status_ok": "● Carga do sistema: normal",
        "status_warn": "● Carga do sistema: alta",
        "cpu": "CPU", "ram": "MEMÓRIA", "disk": "DISCO", "battery": "BATERIA",
        "no_battery": "Sem bateria", "charging": "Na tomada", "on_battery": "Na bateria",
        "graph_title": "CPU e memória ao vivo", "log_title": "Registro de atividades",
        "close": "Fechar", "working": "Trabalhando...", "error": "Erro",
        "windows_only": "Este recurso funciona apenas no Windows.",
        "threads": "threads", "free": "livre", "started": "WinHeal iniciado.",
        "issue_cpu": "O uso da CPU está muito alto. Feche programas pesados.",
        "issue_ram": "O uso de memória está muito alto. Feche programas não usados ou reinicie.",
        "issue_disk": "O disco está quase cheio. Use a limpeza de arquivos inúteis ou o localizador de duplicados.",
        "issue_battery": "A bateria está fraca e não está carregando.",
        "issue_uptime": "O PC não é reiniciado há {d} dias. Reiniciar pode ajudar.",
        "no_issues": "Nenhum problema encontrado. Seu sistema parece saudável.",
        "found_issues": "Possíveis problemas:",
        "top_procs": "Maior uso de memória:",
        "uptime": "Tempo ligado",
        "host": "Nome do computador", "local_ip": "IP local", "sent": "Dados enviados",
        "received": "Dados recebidos", "ping_test": "Ping na internet (8.8.8.8)",
        "dns_test": "Consulta DNS (example.com)", "ok": "OK", "failed": "FALHOU",
        "net_ok": "Resultado: a conexão parece saudável.",
        "net_dns": "Resultado: há internet, mas o DNS falha. Tente 'Limpar cache DNS' ou troque o servidor DNS.",
        "net_down": "Resultado: sem internet. Verifique o Wi-Fi ou cabo e o roteador, e reinicie o roteador.",
        "flush_dns": "Limpar cache DNS", "dns_flushed": "Cache DNS limpo.",
        "startup_none": "Nenhum item de inicialização.",
        "startup_note": "Você pode desativar qualquer item aqui e restaurá-lo depois.",
        "open_startup": "Abrir configurações de inicialização",
        "startup_disable": "Desativar", "startup_restore": "Restaurar",
        "startup_disabled_title": "Desativados pelo WinHeal (podem ser restaurados):",
        "startup_confirm": "Desativar '{name}' na inicialização?\nVocê pode restaurar depois nesta janela.",
        "startup_disabled_ok": "'{name}' desativado.",
        "startup_restored_ok": "'{name}' restaurado.",
        "startup_admin": "Este item exige direitos de administrador. Execute o WinHeal como administrador.",
        "startup_failed": "Falha: {err}",
        "junk_found": "Encontrados {n} arquivos temporários com mais de 24 horas, total de {size}.",
        "junk_none": "Não há arquivos temporários antigos para limpar.",
        "delete_now": "Excluir estes arquivos",
        "confirm_delete": "Excluir {n} arquivos ({size})?\nIsso não pode ser desfeito.",
        "junk_done": "Excluídos {n} arquivos, liberados {size}. {f} ignorados (em uso ou protegidos).",
        "browser_found": "Encontrados {size} de cache do navegador em {n} arquivos (Chrome/Edge/Brave).",
        "browser_none": "Nenhum cache de navegador encontrado.",
        "browser_note": "Feche os navegadores antes para melhor resultado. Senhas e favoritos não são afetados.",
        "large_pick": "Escolha uma pasta para verificar",
        "large_scanning": "Procurando arquivos acima de 500 MB em {folder} ...",
        "large_none": "Nenhum arquivo acima de 500 MB encontrado.",
        "large_found": "{n} arquivos grandes encontrados. O WinHeal não exclui nada.",
        "bin_confirm": "Esvaziar a lixeira permanentemente? Isso não pode ser desfeito.",
        "bin_done": "Lixeira esvaziada.",
        "dups_pick": "Escolha uma pasta para procurar duplicados",
        "dups_scanning": "Verificando {folder} ...",
        "dups_none": "Nenhum duplicado encontrado (arquivos menores que 1 KB são ignorados).",
        "dups_summary": "{g} grupos de arquivos idênticos. Espaço recuperável: {size}.",
        "dups_note": "O WinHeal não exclui nada. Revise a lista e remova as cópias você mesmo.",
        "wg_missing": "winget não encontrado. Instale o 'Instalador de Aplicativo' na Microsoft Store.",
        "wg_hint": "Para atualizar tudo, execute no terminal: winget upgrade --all",
        "bench_cpu": "Tempo do teste de CPU: {s:.2f} s (menor é mais rápido)",
        "bench_disk": "Velocidade de gravação em disco: {mb:.0f} MB/s",
        "bench_note": "Testes simples e aproximados. Não comparáveis a benchmarks profissionais.",
        "report_saved": "Relatório salvo: {path}",
        "parent_dir": "[..] Pasta superior", "col_name": "Nome", "col_type": "Tipo",
        "col_size": "Tamanho", "folder": "Pasta", "file": "Arquivo", "home": "Início",
        "browse": "Procurar...", "copy_ask": "Copiar '{name}' para outra pasta?",
        "copy_done": "Copiado para: {dest}", "path": "Caminho",
        "total_cleaned": "Total limpo: {size}",
        "check_update": "Verificar atualização",
        "update_available": "A versão {latest} está disponível (você tem {current}). Abrir a página de download?",
        "up_to_date": "Você tem a versão mais recente ({current}).",
        "no_release": "Nenhuma versão foi publicada ainda.",
        "update_failed": "Não foi possível verificar atualizações: {err}",
    },
    "fr": {
        "app_title": "WinHeal - Outil d'entretien du système",
        "menu_diag": "Diagnostic du système",
        "menu_files": "Explorateur de fichiers et lecteurs",
        "menu_net": "Dépannage réseau",
        "menu_startup": "Programmes au démarrage",
        "menu_dups": "Recherche de doublons",
        "menu_updates": "Mises à jour logicielles",
        "menu_junk": "Nettoyage des fichiers inutiles",
        "menu_browser": "Nettoyage du cache du navigateur",
        "menu_large": "Recherche de gros fichiers",
        "menu_bin": "Vider la corbeille",
        "menu_bench": "Test de performance rapide",
        "menu_report": "Exporter le rapport système",
        "theme": "THÈME", "language": "LANGUE", "custom": "Personnalisé", "quit": "Quitter",
        "dashboard": "TABLEAU DE BORD",
        "status_ok": "● Charge système : normale",
        "status_warn": "● Charge système : élevée",
        "cpu": "CPU", "ram": "MÉMOIRE", "disk": "DISQUE", "battery": "BATTERIE",
        "no_battery": "Pas de batterie", "charging": "Branché", "on_battery": "Sur batterie",
        "graph_title": "CPU et mémoire en direct", "log_title": "Journal d'activité",
        "close": "Fermer", "working": "En cours...", "error": "Erreur",
        "windows_only": "Cette fonction ne marche que sous Windows.",
        "threads": "threads", "free": "libre", "started": "WinHeal démarré.",
        "issue_cpu": "L'utilisation du CPU est très élevée. Fermez les programmes lourds.",
        "issue_ram": "L'utilisation de la mémoire est très élevée. Fermez les programmes inutiles ou redémarrez.",
        "issue_disk": "Le disque est presque plein. Utilisez le nettoyage ou la recherche de doublons.",
        "issue_battery": "La batterie est faible et ne charge pas.",
        "issue_uptime": "Le PC n'a pas redémarré depuis {d} jours. Un redémarrage peut aider.",
        "no_issues": "Aucun problème trouvé. Votre système semble en bonne santé.",
        "found_issues": "Problèmes possibles :",
        "top_procs": "Plus gros consommateurs de mémoire :",
        "uptime": "Temps de fonctionnement",
        "host": "Nom de l'ordinateur", "local_ip": "IP locale", "sent": "Données envoyées",
        "received": "Données reçues", "ping_test": "Ping internet (8.8.8.8)",
        "dns_test": "Résolution DNS (example.com)", "ok": "OK", "failed": "ÉCHEC",
        "net_ok": "Résultat : la connexion semble saine.",
        "net_dns": "Résultat : internet fonctionne mais le DNS échoue. Essayez « Vider le cache DNS » ou changez de serveur DNS.",
        "net_down": "Résultat : pas d'internet. Vérifiez le Wi-Fi ou le câble et la box, puis redémarrez la box.",
        "flush_dns": "Vider le cache DNS", "dns_flushed": "Cache DNS vidé.",
        "startup_none": "Aucune entrée de démarrage.",
        "startup_note": "Vous pouvez désactiver une entrée ici et la restaurer plus tard.",
        "open_startup": "Ouvrir les paramètres de démarrage",
        "startup_disable": "Désactiver", "startup_restore": "Restaurer",
        "startup_disabled_title": "Désactivées par WinHeal (restaurables) :",
        "startup_confirm": "Désactiver « {name} » au démarrage ?\nVous pourrez la restaurer plus tard depuis cette fenêtre.",
        "startup_disabled_ok": "« {name} » désactivée.",
        "startup_restored_ok": "« {name} » restaurée.",
        "startup_admin": "Cette entrée nécessite les droits administrateur. Lancez WinHeal en administrateur.",
        "startup_failed": "Échec : {err}",
        "junk_found": "{n} fichiers temporaires de plus de 24 heures trouvés, total {size}.",
        "junk_none": "Aucun ancien fichier temporaire à nettoyer.",
        "delete_now": "Supprimer ces fichiers",
        "confirm_delete": "Supprimer {n} fichiers ({size}) ?\nCette action est irréversible.",
        "junk_done": "{n} fichiers supprimés, {size} libérés. {f} ignorés (en cours d'utilisation ou protégés).",
        "browser_found": "{size} de cache de navigateur trouvés dans {n} fichiers (Chrome/Edge/Brave).",
        "browser_none": "Aucun cache de navigateur trouvé.",
        "browser_note": "Fermez d'abord vos navigateurs pour un meilleur résultat. Mots de passe et favoris ne sont pas touchés.",
        "large_pick": "Choisissez un dossier à analyser",
        "large_scanning": "Recherche de fichiers de plus de 500 Mo dans {folder} ...",
        "large_none": "Aucun fichier de plus de 500 Mo trouvé.",
        "large_found": "{n} gros fichiers trouvés. WinHeal ne supprime rien.",
        "bin_confirm": "Vider définitivement la corbeille ? Irréversible.",
        "bin_done": "Corbeille vidée.",
        "dups_pick": "Choisissez un dossier où chercher des doublons",
        "dups_scanning": "Analyse de {folder} ...",
        "dups_none": "Aucun doublon trouvé (fichiers de moins de 1 Ko ignorés).",
        "dups_summary": "{g} groupes de fichiers identiques. Espace récupérable : {size}.",
        "dups_note": "WinHeal ne supprime rien. Vérifiez la liste et supprimez les copies vous-même.",
        "wg_missing": "winget introuvable. Installez « Programme d'installation d'application » depuis le Microsoft Store.",
        "wg_hint": "Pour tout mettre à jour, lancez dans un terminal : winget upgrade --all",
        "bench_cpu": "Durée du test CPU : {s:.2f} s (moins = plus rapide)",
        "bench_disk": "Vitesse d'écriture disque : {mb:.0f} Mo/s",
        "bench_note": "Tests simples et indicatifs. Non comparables à des benchmarks professionnels.",
        "report_saved": "Rapport enregistré : {path}",
        "parent_dir": "[..] Dossier parent", "col_name": "Nom", "col_type": "Type",
        "col_size": "Taille", "folder": "Dossier", "file": "Fichier", "home": "Accueil",
        "browse": "Parcourir...", "copy_ask": "Copier « {name} » vers un autre dossier ?",
        "copy_done": "Copié vers : {dest}", "path": "Chemin",
        "total_cleaned": "Total nettoyé : {size}",
        "check_update": "Vérifier les mises à jour",
        "update_available": "La version {latest} est disponible (vous avez {current}). Ouvrir la page de téléchargement ?",
        "up_to_date": "Vous avez la dernière version ({current}).",
        "no_release": "Aucune version n'a encore été publiée.",
        "update_failed": "Impossible de vérifier les mises à jour : {err}",
    },
    "de": {
        "app_title": "WinHeal - Systempflege-Tool",
        "menu_diag": "Systemdiagnose",
        "menu_files": "Datei- und Laufwerks-Explorer",
        "menu_net": "Netzwerk-Fehlerbehebung",
        "menu_startup": "Autostart-Programme",
        "menu_dups": "Duplikate finden",
        "menu_updates": "Software-Updates",
        "menu_junk": "Datenmüll bereinigen",
        "menu_browser": "Browser-Cache bereinigen",
        "menu_large": "Große Dateien finden",
        "menu_bin": "Papierkorb leeren",
        "menu_bench": "Schneller Benchmark",
        "menu_report": "Systembericht exportieren",
        "theme": "DESIGN", "language": "SPRACHE", "custom": "Eigene", "quit": "Beenden",
        "dashboard": "SYSTEMÜBERSICHT",
        "status_ok": "● Systemlast: normal",
        "status_warn": "● Systemlast: hoch",
        "cpu": "CPU", "ram": "SPEICHER", "disk": "DATENTRÄGER", "battery": "AKKU",
        "no_battery": "Kein Akku", "charging": "Am Netz", "on_battery": "Akkubetrieb",
        "graph_title": "CPU und Speicher live", "log_title": "Aktivitätsprotokoll",
        "close": "Schließen", "working": "Arbeite...", "error": "Fehler",
        "windows_only": "Diese Funktion gibt es nur unter Windows.",
        "threads": "Threads", "free": "frei", "started": "WinHeal gestartet.",
        "issue_cpu": "Die CPU-Auslastung ist sehr hoch. Schließen Sie rechenintensive Programme.",
        "issue_ram": "Die Speicherauslastung ist sehr hoch. Schließen Sie unnötige Programme oder starten Sie neu.",
        "issue_disk": "Der Datenträger ist fast voll. Nutzen Sie die Bereinigung oder die Duplikatsuche.",
        "issue_battery": "Der Akku ist schwach und lädt nicht.",
        "issue_uptime": "Der PC wurde seit {d} Tagen nicht neu gestartet. Ein Neustart kann helfen.",
        "no_issues": "Keine Probleme gefunden. Ihr System sieht gesund aus.",
        "found_issues": "Mögliche Probleme:",
        "top_procs": "Größte Speichernutzer:",
        "uptime": "Laufzeit",
        "host": "Computername", "local_ip": "Lokale IP", "sent": "Gesendete Daten",
        "received": "Empfangene Daten", "ping_test": "Internet-Ping (8.8.8.8)",
        "dns_test": "DNS-Abfrage (example.com)", "ok": "OK", "failed": "FEHLGESCHLAGEN",
        "net_ok": "Ergebnis: Die Verbindung sieht gesund aus.",
        "net_dns": "Ergebnis: Internet erreichbar, aber DNS schlägt fehl. Versuchen Sie 'DNS-Cache leeren' oder wechseln Sie den DNS-Server.",
        "net_down": "Ergebnis: Kein Internet. Prüfen Sie WLAN/Kabel und Router und starten Sie den Router neu.",
        "flush_dns": "DNS-Cache leeren", "dns_flushed": "DNS-Cache geleert.",
        "startup_none": "Keine Autostart-Einträge.",
        "startup_note": "Sie können hier jeden Eintrag deaktivieren und später wiederherstellen.",
        "open_startup": "Autostart-Einstellungen öffnen",
        "startup_disable": "Deaktivieren", "startup_restore": "Wiederherstellen",
        "startup_disabled_title": "Von WinHeal deaktiviert (wiederherstellbar):",
        "startup_confirm": "'{name}' beim Start deaktivieren?\nSie können es später in diesem Fenster wiederherstellen.",
        "startup_disabled_ok": "'{name}' deaktiviert.",
        "startup_restored_ok": "'{name}' wiederhergestellt.",
        "startup_admin": "Dieser Eintrag erfordert Administratorrechte. Starten Sie WinHeal als Administrator.",
        "startup_failed": "Fehlgeschlagen: {err}",
        "junk_found": "{n} temporäre Dateien älter als 24 Stunden gefunden, insgesamt {size}.",
        "junk_none": "Keine alten temporären Dateien zum Bereinigen.",
        "delete_now": "Diese Dateien löschen",
        "confirm_delete": "{n} Dateien ({size}) löschen?\nDies kann nicht rückgängig gemacht werden.",
        "junk_done": "{n} Dateien gelöscht, {size} freigegeben. {f} übersprungen (in Benutzung oder geschützt).",
        "browser_found": "{size} Browser-Cache in {n} Dateien gefunden (Chrome/Edge/Brave).",
        "browser_none": "Kein Browser-Cache gefunden.",
        "browser_note": "Schließen Sie zuerst die Browser für das beste Ergebnis. Passwörter und Lesezeichen bleiben unberührt.",
        "large_pick": "Ordner zum Durchsuchen wählen",
        "large_scanning": "Suche nach Dateien über 500 MB in {folder} ...",
        "large_none": "Keine Dateien über 500 MB gefunden.",
        "large_found": "{n} große Dateien gefunden. WinHeal löscht nichts.",
        "bin_confirm": "Papierkorb endgültig leeren? Dies kann nicht rückgängig gemacht werden.",
        "bin_done": "Papierkorb geleert.",
        "dups_pick": "Ordner für die Duplikatsuche wählen",
        "dups_scanning": "Durchsuche {folder} ...",
        "dups_none": "Keine Duplikate gefunden (Dateien unter 1 KB werden ignoriert).",
        "dups_summary": "{g} Gruppen identischer Dateien. Einsparbarer Platz: {size}.",
        "dups_note": "WinHeal löscht nichts. Prüfen Sie die Liste und entfernen Sie Kopien selbst.",
        "wg_missing": "winget nicht gefunden. Installieren Sie den 'App-Installer' aus dem Microsoft Store.",
        "wg_hint": "Um alles zu aktualisieren, im Terminal ausführen: winget upgrade --all",
        "bench_cpu": "CPU-Testzeit: {s:.2f} s (weniger ist schneller)",
        "bench_disk": "Schreibgeschwindigkeit: {mb:.0f} MB/s",
        "bench_note": "Einfache Richtwerte. Nicht mit professionellen Benchmarks vergleichbar.",
        "report_saved": "Bericht gespeichert: {path}",
        "parent_dir": "[..] Übergeordneter Ordner", "col_name": "Name", "col_type": "Typ",
        "col_size": "Größe", "folder": "Ordner", "file": "Datei", "home": "Start",
        "browse": "Durchsuchen...", "copy_ask": "'{name}' in einen anderen Ordner kopieren?",
        "copy_done": "Kopiert nach: {dest}", "path": "Pfad",
        "total_cleaned": "Insgesamt bereinigt: {size}",
        "check_update": "Nach Update suchen",
        "update_available": "Version {latest} ist verfügbar (Sie haben {current}). Download-Seite öffnen?",
        "up_to_date": "Sie haben die neueste Version ({current}).",
        "no_release": "Es wurde noch keine Version veröffentlicht.",
        "update_failed": "Update-Prüfung nicht möglich: {err}",
    },
    "ru": {
        "app_title": "WinHeal - Инструмент обслуживания системы",
        "menu_diag": "Диагностика системы",
        "menu_files": "Проводник файлов и дисков",
        "menu_net": "Диагностика сети",
        "menu_startup": "Программы автозагрузки",
        "menu_dups": "Поиск дубликатов",
        "menu_updates": "Обновления программ",
        "menu_junk": "Очистка мусорных файлов",
        "menu_browser": "Очистка кэша браузера",
        "menu_large": "Поиск больших файлов",
        "menu_bin": "Очистить корзину",
        "menu_bench": "Быстрый тест",
        "menu_report": "Экспорт отчёта о системе",
        "theme": "ТЕМА", "language": "ЯЗЫК", "custom": "Свой", "quit": "Выход",
        "dashboard": "ПАНЕЛЬ СИСТЕМЫ",
        "status_ok": "● Нагрузка системы: нормальная",
        "status_warn": "● Нагрузка системы: высокая",
        "cpu": "ЦП", "ram": "ПАМЯТЬ", "disk": "ДИСК", "battery": "БАТАРЕЯ",
        "no_battery": "Нет батареи", "charging": "Подключено к питанию", "on_battery": "Работа от батареи",
        "graph_title": "ЦП и память в реальном времени", "log_title": "Журнал действий",
        "close": "Закрыть", "working": "Выполняется...", "error": "Ошибка",
        "windows_only": "Эта функция работает только в Windows.",
        "threads": "потоков", "free": "свободно", "started": "WinHeal запущен.",
        "issue_cpu": "Очень высокая нагрузка на ЦП. Закройте тяжёлые программы.",
        "issue_ram": "Очень высокое использование памяти. Закройте ненужные программы или перезагрузите ПК.",
        "issue_disk": "Диск почти заполнен. Используйте очистку мусора или поиск дубликатов.",
        "issue_battery": "Низкий заряд батареи, зарядка не идёт.",
        "issue_uptime": "ПК не перезагружался {d} дн. Перезагрузка может помочь.",
        "no_issues": "Проблем не найдено. Система выглядит здоровой.",
        "found_issues": "Возможные проблемы:",
        "top_procs": "Больше всего памяти используют:",
        "uptime": "Время работы",
        "host": "Имя компьютера", "local_ip": "Локальный IP", "sent": "Отправлено данных",
        "received": "Получено данных", "ping_test": "Пинг интернета (8.8.8.8)",
        "dns_test": "DNS-запрос (example.com)", "ok": "ОК", "failed": "СБОЙ",
        "net_ok": "Результат: соединение в порядке.",
        "net_dns": "Результат: интернет доступен, но DNS не работает. Попробуйте «Сбросить кэш DNS» или смените DNS-сервер.",
        "net_down": "Результат: нет интернета. Проверьте Wi-Fi или кабель и роутер, перезагрузите роутер.",
        "flush_dns": "Сбросить кэш DNS", "dns_flushed": "Кэш DNS сброшен.",
        "startup_none": "Нет элементов автозагрузки.",
        "startup_note": "Здесь можно отключить любой элемент и позже вернуть его.",
        "open_startup": "Открыть настройки автозагрузки",
        "startup_disable": "Отключить", "startup_restore": "Вернуть",
        "startup_disabled_title": "Отключено WinHeal (можно вернуть):",
        "startup_confirm": "Отключить «{name}» при запуске?\nПозже его можно вернуть из этого окна.",
        "startup_disabled_ok": "«{name}» отключено.",
        "startup_restored_ok": "«{name}» возвращено.",
        "startup_admin": "Для этого элемента нужны права администратора. Запустите WinHeal от имени администратора.",
        "startup_failed": "Ошибка: {err}",
        "junk_found": "Найдено временных файлов старше 24 часов: {n}, всего {size}.",
        "junk_none": "Нет старых временных файлов для очистки.",
        "delete_now": "Удалить эти файлы",
        "confirm_delete": "Удалить файлов: {n} ({size})?\nЭто нельзя отменить.",
        "junk_done": "Удалено файлов: {n}, освобождено {size}. Пропущено: {f} (используются или защищены).",
        "browser_found": "Найдено {size} кэша браузеров в {n} файлах (Chrome/Edge/Brave).",
        "browser_none": "Кэш браузеров не найден.",
        "browser_note": "Для лучшего результата сначала закройте браузеры. Пароли и закладки не затрагиваются.",
        "large_pick": "Выберите папку для сканирования",
        "large_scanning": "Поиск файлов больше 500 МБ в {folder} ...",
        "large_none": "Файлов больше 500 МБ не найдено.",
        "large_found": "Найдено больших файлов: {n}. WinHeal ничего не удаляет.",
        "bin_confirm": "Очистить корзину без возможности восстановления?",
        "bin_done": "Корзина очищена.",
        "dups_pick": "Выберите папку для поиска дубликатов",
        "dups_scanning": "Сканирование {folder} ...",
        "dups_none": "Дубликатов не найдено (файлы меньше 1 КБ игнорируются).",
        "dups_summary": "Групп одинаковых файлов: {g}. Можно освободить: {size}.",
        "dups_note": "WinHeal ничего не удаляет. Просмотрите список и удалите копии сами.",
        "wg_missing": "winget не найден. Установите «Установщик приложения» из Microsoft Store.",
        "wg_hint": "Чтобы обновить всё, выполните в терминале: winget upgrade --all",
        "bench_cpu": "Время теста ЦП: {s:.2f} с (меньше — быстрее)",
        "bench_disk": "Скорость записи на диск: {mb:.0f} МБ/с",
        "bench_note": "Простые ориентировочные тесты, не сопоставимы с профессиональными бенчмарками.",
        "report_saved": "Отчёт сохранён: {path}",
        "parent_dir": "[..] Родительская папка", "col_name": "Имя", "col_type": "Тип",
        "col_size": "Размер", "folder": "Папка", "file": "Файл", "home": "Домой",
        "browse": "Обзор...", "copy_ask": "Копировать «{name}» в другую папку?",
        "copy_done": "Скопировано в: {dest}", "path": "Путь",
        "total_cleaned": "Всего очищено: {size}",
        "check_update": "Проверить обновления",
        "update_available": "Доступна версия {latest} (у вас {current}). Открыть страницу загрузки?",
        "up_to_date": "У вас последняя версия ({current}).",
        "no_release": "Релизов пока нет.",
        "update_failed": "Не удалось проверить обновления: {err}",
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


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_total_cleaned():
    d = load_json(STATS_FILE, {})
    try:
        return int(d.get("total_bytes", 0))
    except (TypeError, ValueError, AttributeError):
        return 0


def add_total_cleaned(nbytes):
    """Add the bytes that were REALLY deleted to the lifetime counter."""
    total = get_total_cleaned() + int(nbytes)
    try:
        save_json(STATS_FILE, {"total_bytes": total})
    except OSError:
        pass
    return total


def browser_cache_dirs():
    la = os.environ.get("LOCALAPPDATA")
    if not la:
        return []
    rel = [r"Google\Chrome\User Data\Default\Cache", r"Google\Chrome\User Data\Default\Code Cache",
           r"Microsoft\Edge\User Data\Default\Cache", r"Microsoft\Edge\User Data\Default\Code Cache",
           r"BraveSoftware\Brave-Browser\User Data\Default\Cache"]
    return [p for p in (os.path.join(la, r) for r in rel) if os.path.isdir(p)]


def scan_all_files(dirs):
    """Return ([(path, size)], total_size) for every regular file under dirs."""
    files, total = [], 0
    for d in dirs:
        for root, _, names in os.walk(d):
            for n in names:
                fp = os.path.join(root, n)
                try:
                    st = os.lstat(fp)
                except OSError:
                    continue
                files.append((fp, st.st_size))
                total += st.st_size
    return files, total


def find_large_files(folder, min_mb=LARGE_MB, cancel=None):
    """Return [(size, path)] of files >= min_mb, biggest first, or None if cancelled."""
    limit = min_mb * 1024 * 1024
    found = []
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
            if size >= limit:
                found.append((size, fp))
    found.sort(reverse=True)
    return found


def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v))[:3])


def check_latest_release():
    """Return ("none", None) if no release exists, else ("ok", tag_name)."""
    req = urllib.request.Request(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                                 headers={"User-Agent": "WinHeal", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "none", None
        raise
    return "ok", str(data.get("tag_name", ""))


def _run_hive(scope):
    return winreg.HKEY_CURRENT_USER if scope == "User" else winreg.HKEY_LOCAL_MACHINE


def disabled_startup_entries():
    data = load_json(BACKUP_FILE, [])
    return data if isinstance(data, list) else []


def disable_startup(scope, name, value):
    """Remove a Run entry but save it first so it can be restored."""
    backup = disabled_startup_entries()
    backup = [b for b in backup if not (b.get("scope") == scope and b.get("name") == name)]
    backup.append({"scope": scope, "name": name, "value": value})
    save_json(BACKUP_FILE, backup)  # backup BEFORE deleting
    try:
        with winreg.OpenKey(_run_hive(scope), RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, name)
    except OSError:
        save_json(BACKUP_FILE, [b for b in backup if not (b["scope"] == scope and b["name"] == name)])
        raise


def restore_startup(scope, name, value):
    kind = winreg.REG_EXPAND_SZ if "%" in value else winreg.REG_SZ
    with winreg.OpenKey(_run_hive(scope), RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, name, 0, kind, value)
    rest = [b for b in disabled_startup_entries() if not (b.get("scope") == scope and b.get("name") == name)]
    save_json(BACKUP_FILE, rest)


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

        root.geometry("1200x820")
        root.minsize(1000, 740)
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
            ("menu_junk", self.junk), ("menu_browser", self.browser_cache),
            ("menu_large", self.large_files), ("menu_bin", self.empty_bin),
            ("menu_bench", self.benchmark), ("menu_report", self.export_report),
        ]
        for key, cmd in menu:
            tk.Button(side, text=self.t(key), command=cmd, bg=self.card, fg="#cbd5e1",
                      activebackground="#1e293b", activeforeground=self.accent,
                      font=("Segoe UI", 9), anchor="w", padx=15, pady=3, relief="flat",
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
        combo = ttk.Combobox(lbox, values=[n for _, n in LANG_NAMES], state="readonly", font=("Segoe UI", 10))
        combo.set(dict(LANG_NAMES)[self.lang])
        combo.pack(fill="x", pady=3)
        combo.bind("<<ComboboxSelected>>",
                   lambda e: self.set_lang(next(c for c, n in LANG_NAMES if n == combo.get())))

        tk.Button(side, text=self.t("quit"), command=self.root.destroy, bg="#180707", fg="#f87171",
                  font=("Segoe UI", 9, "bold"), pady=5, relief="flat",
                  cursor="hand2").pack(side="bottom", fill="x", padx=15, pady=10)
        tk.Button(side, text="🔄 " + self.t("check_update"), command=self.check_update, bg="#1e3a5f",
                  fg="#38bdf8", font=("Segoe UI", 9, "bold"), pady=5, relief="flat",
                  cursor="hand2").pack(side="bottom", fill="x", padx=15, pady=(0, 2))

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
        self.total_lbl = tk.Label(top, text="", font=("Segoe UI", 9), bg=self.bg, fg="#94a3b8")
        self.total_lbl.pack(side="right", padx=12)
        self.refresh_total()

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

    def refresh_total(self):
        try:
            self.total_lbl.config(text=self.t("total_cleaned", size=fmt_size(get_total_cleaned())))
        except (tk.TclError, AttributeError):
            pass

    def startup(self):
        win = tk.Toplevel(self.root)
        win.title(self.t("menu_startup"))
        win.geometry("780x580")
        win.config(bg=self.bg)
        tk.Label(win, text=self.t("menu_startup"), font=("Segoe UI", 12, "bold"), bg=self.bg,
                 fg=self.accent).pack(pady=10)
        if not IS_WIN:
            tk.Label(win, text=self.t("windows_only"), bg=self.bg, fg=self.neon).pack(pady=20)
            return
        tk.Label(win, text=self.t("startup_note"), font=("Segoe UI", 9), bg=self.bg, fg="#94a3b8",
                 wraplength=720, justify="left").pack(padx=15, anchor="w")
        holder = tk.Frame(win, bg=self.card)
        holder.pack(fill="both", expand=True, padx=15, pady=8)
        canvas = tk.Canvas(holder, bg=self.card, highlightthickness=0)
        sb = ttk.Scrollbar(holder, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.card)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def do_disable(scope, name, value):
            if not messagebox.askyesno(self.t("menu_startup"), self.t("startup_confirm", name=name)):
                return
            try:
                disable_startup(scope, name, value)
            except PermissionError:
                messagebox.showerror(self.t("error"), self.t("startup_admin"))
            except OSError as e:
                messagebox.showerror(self.t("error"), self.t("startup_failed", err=str(e)))
            else:
                self.log(self.t("startup_disabled_ok", name=name))
                refresh()

        def do_restore(scope, name, value):
            try:
                restore_startup(scope, name, value)
            except PermissionError:
                messagebox.showerror(self.t("error"), self.t("startup_admin"))
            except OSError as e:
                messagebox.showerror(self.t("error"), self.t("startup_failed", err=str(e)))
            else:
                self.log(self.t("startup_restored_ok", name=name))
                refresh()

        def row(scope, name, value, label, cmd, color):
            r = tk.Frame(inner, bg=self.card)
            r.pack(fill="x", padx=8, pady=3)
            tk.Label(r, text=f"[{scope}] {name}\n{value}", font=("Consolas", 9), bg=self.card, fg=self.neon,
                     justify="left", anchor="w", wraplength=560).pack(side="left", fill="x", expand=True)
            self.button(r, label, cmd, color).pack(side="right", padx=5)

        def refresh():
            for w in inner.winfo_children():
                w.destroy()
            items = startup_entries()
            if not items:
                tk.Label(inner, text=self.t("startup_none"), bg=self.card, fg="#94a3b8").pack(pady=8, padx=8)
            for scope, name, value in items:
                row(scope, name, value, self.t("startup_disable"),
                    lambda sc=scope, n=name, v=value: do_disable(sc, n, v), "#b91c1c")
            disabled = disabled_startup_entries()
            if disabled:
                tk.Label(inner, text=self.t("startup_disabled_title"), font=("Segoe UI", 9, "bold"),
                         bg=self.card, fg="#fbbf24").pack(anchor="w", padx=8, pady=(14, 4))
                for b in disabled:
                    row(b["scope"], b["name"], b["value"], self.t("startup_restore"),
                        lambda sc=b["scope"], n=b["name"], v=b["value"]: do_restore(sc, n, v), "#064e3b")

        refresh()
        bf = tk.Frame(win, bg=self.bg)
        bf.pack(fill="x", padx=15, pady=10)

        def open_settings():
            try:
                os.startfile("ms-settings:startupapps")
            except OSError:
                run_cmd(["taskmgr"])
        self.button(bf, self.t("open_startup"), open_settings).pack(side="left")
        self.button(bf, self.t("close"), win.destroy, "#7f1d1d").pack(side="right")

    def cleaner(self, menu_key, scan_fn, found_key, none_key, note_key=None):
        """Generic scan -> show size -> ask -> delete flow. Counts only bytes really deleted."""
        win, btns, write = self.result_window(self.t(menu_key))
        state = {"files": [], "total": 0}
        del_btn = self.button(btns, self.t("delete_now"), lambda: delete(), "#b45309")
        del_btn.config(state="disabled")
        del_btn.pack(side="left")

        def scan():
            write(self.t("working") + "\n", clear=True)
            files, total = scan_fn()
            state["files"], state["total"] = files, total
            if files:
                msg = self.t(found_key, n=len(files), size=fmt_size(total))
                if note_key:
                    msg += "\n\n" + self.t(note_key)
                write(msg + "\n", clear=True)
                self.ui(lambda: del_btn.config(state="normal"))
            else:
                write(self.t(none_key) + "\n", clear=True)

        def delete():
            files, total = state["files"], state["total"]
            if not messagebox.askyesno(self.t(menu_key), self.t("confirm_delete", n=len(files), size=fmt_size(total))):
                return
            del_btn.config(state="disabled")

            def work():
                n, freed, failed = delete_files(files)
                add_total_cleaned(freed)
                msg = self.t("junk_done", n=n, size=fmt_size(freed), f=failed)
                write(msg + "\n", clear=True)
                self.toast(self.t(menu_key), msg)
                self.log(msg)
                self.ui(self.refresh_total)
            self.run_bg(work)
        self.run_bg(scan)

    def junk(self):
        self.cleaner("menu_junk", scan_junk, "junk_found", "junk_none")

    def browser_cache(self):
        self.cleaner("menu_browser", lambda: scan_all_files(browser_cache_dirs()),
                     "browser_found", "browser_none", "browser_note")

    def large_files(self):
        folder = filedialog.askdirectory(title=self.t("large_pick"))
        if not folder:
            return
        win, _, write = self.result_window(self.t("menu_large"), "820x520")

        def work():
            write(self.t("large_scanning", folder=folder) + "\n", clear=True)
            res = find_large_files(folder, LARGE_MB, win.cancel)
            if res is None:
                return
            if not res:
                write(self.t("large_none") + "\n", clear=True)
                return
            lines = [self.t("large_found", n=len(res)), ""]
            lines += [f"{fmt_size(sz):>10}  {p}" for sz, p in res[:100]]
            write("\n".join(lines) + "\n", clear=True)
            self.log(self.t("large_found", n=len(res)))
        self.run_bg(work)

    def check_update(self):
        def work():
            try:
                status, tag = check_latest_release()
            except Exception as e:  # network errors, bad JSON, rate limit
                err = str(e)
                self.ui(lambda: messagebox.showerror(self.t("error"), self.t("update_failed", err=err)))
                return
            if status == "none" or not tag:
                self.ui(lambda: messagebox.showinfo(self.t("check_update"), self.t("no_release")))
            elif version_tuple(tag) > version_tuple(VERSION):
                def ask():
                    if messagebox.askyesno(self.t("check_update"),
                                           self.t("update_available", latest=tag, current=VERSION)):
                        webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
                self.ui(ask)
            else:
                self.ui(lambda: messagebox.showinfo(self.t("check_update"),
                                                    self.t("up_to_date", current=VERSION)))
        self.run_bg(work)

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