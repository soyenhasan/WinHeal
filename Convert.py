from PIL import Image
img = Image.open("icon.png")
img.save("icon.ico", sizes=[(256,256)])
print("Icon Ready! icon.ico তৈরি হয়েছে!")