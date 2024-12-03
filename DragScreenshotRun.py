import tkinter as tk
import DragScreenshot as dshot

root = tk.Tk()
root.withdraw()

def callback(img):
    img.save("a.png")

def cancel_callback():
    print("User clicked / dragged 0 pixels.")

dshot.drag_screen_shot(root, callback, cancel_callback)

root.mainloop()