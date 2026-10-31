# WinHeal v0.1.0 - First Version from Zero
# Made by soyenhasan

import tkinter as tk
import os

def clean_temp():
    try:
        temp_path = os.environ.get('TEMP')
        count = 0
        for file in os.listdir(temp_path):
            try:
                full_path = os.path.join(temp_path, file)
                if os.path.isfile(full_path):
                    os.remove(full_path)
                    count += 1
            except:
                pass
        status_label.config(text=f"✅ {count} files cleaned!")
    except Exception as e:
        status_label.config(text=f"❌ Error: {e}")

root = tk.Tk()
root.title("WinHeal v0.1.0")
root.geometry("400x300")
root.configure(bg="#1e293b")

tk.Label(root, text="WinHeal", font=("Arial", 30, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=20)
tk.Label(root, text="v0.1.0 - First Version", bg="#1e293b", fg="white").pack()
tk.Label(root, text="The Journey Begins", bg="#1e293b", fg="gray").pack(pady=5)

tk.Button(root, text="🧹 Clean Temp Files", bg="#16a34a", fg="white", font=("Arial", 12), padx=20, pady=10, command=clean_temp).pack(pady=20)

status_label = tk.Label(root, text="Ready to clean...", bg="#1e293b", fg="white")
status_label.pack(pady=10)

tk.Label(root, text="Made in Bangladesh", bg="#1e293b", fg="gray", font=("Arial", 8)).pack(side="bottom", pady=10)

root.mainloop()