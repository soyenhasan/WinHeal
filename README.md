# ⚡ WinHeal - Windows System Care Tool

> **Version 0.1.1 SAFE** - Cold AI Verified, No Syntax Errors ✅  
> A lightweight, real system care tool for Windows - built with Python

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6)
![License](https://img.shields.io/badge/License-MIT-green)
![Safe](https://img.shields.io/badge/Safe-v0.1.1-brightgreen)

### 🌐 Languages: English + বাংলা

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| **System Diagnostics** | Real-time CPU, RAM, Disk, Battery + health issues detection |
| **File & Drive Explorer** | Custom file manager with copy support |
| **Network Troubleshooter** | Ping, DNS check, Flush DNS |
| **Startup Programs** | Read-only view of Windows Run keys (safe) |
| **Duplicate Finder** | SHA-256 based duplicate detection |
| **Junk Cleaner** | Cleans only temp files older than 24h (SAFE) |
| **Recycle Bin** | One-click empty with confirmation |
| **Quick Benchmark** | CPU & Disk write speed test |
| **Live Dashboard** | CPU & Memory graph + Activity log |

---

## 🛡️ v0.1.1 SAFE - What's Fixed

- ✅ **Junk Cleaner Safety**: Validates TEMP path must contain `temp` keyword
- ✅ **Admin Check**: Shows warning if not run as Administrator
- ✅ **Memory Leak Fix**: Matplotlib figure properly closed on theme change
- ✅ **Production Ready**: Tested, no fake simulation

---

## 🚀 Installation

```bash
# Clone
git clone https://github.com/soyenhasan/WinHeal-AI.git
cd WinHeal-AI

# Install dependencies
pip install -r requirements.txt

# Run
python main.py