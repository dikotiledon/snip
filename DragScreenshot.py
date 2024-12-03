import platform
import tkinter as tk
from PIL import ImageGrab

using_debug_mode = None

class DragScreenshotPanel:  
    def __init__(self, root: tk.Tk, master: tk.Toplevel | tk.Tk, callback = None, cancel_callback = None):
        self.root = root
        self.master = master
        self.callback = callback
        self.cancel_callback = cancel_callback
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.canvas = tk.Canvas(master, cursor="cross", background="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)  
        self.canvas.config(bg=master["bg"])
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='white', width=2)  

    def on_mouse_drag(self, event):  
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        self.canvas.delete(self.rect)
        dy = abs(y2-y1)
        dx = abs(x2-x1)
        if dy*dx != 0:
            self.master.withdraw()
            img = ImageGrab.grab()
            self.master.deiconify()
            self.master.focus_force()
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            x1 = x1 / screen_width * img.width
            x2 = x2 / screen_width * img.width
            y1 = y1 / screen_height * img.height
            y2 = y2 / screen_height * img.height
            img = img.crop(box=(x1, y1, x2, y2))
            if using_debug_mode: print("Screenshot taken!")
            self.root.after(1, self.callback(img))
        else:
            if using_debug_mode: print("Screenshot canceled!")
            self.root.after(1, self.cancel_callback())
        
        self.master.destroy()
        


def set_bg_transparent(toplevel:tk.Toplevel, invisible_color_Windows_OS_Only= '#100101'):
    if platform.system() == "Windows":
        toplevel.attributes("-transparentcolor", invisible_color_Windows_OS_Only)
        toplevel.config(bg=invisible_color_Windows_OS_Only)
    elif platform.system() == "Darwin":
        toplevel.attributes("-transparent", True)
        toplevel.config(bg="systemTransparent")
    else:
        if using_debug_mode: print(f"Total transparency is not supported on this OS. platform.system() -> '{platform.system()}'")
        window_alpha_channel = 0.3
        toplevel.attributes('-alpha', window_alpha_channel)
        toplevel.lift()
        toplevel.attributes("-topmost", True)
        toplevel.attributes("-transparent", True)


def drag_screen_shot(root:tk.Tk, callback = None, cancel_callback = None, debug_logging = False):
    global using_debug_mode

    using_debug_mode = debug_logging

    top = tk.Toplevel(root)
    top.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    top.overrideredirect(True)
    top.lift()
    top.attributes("-topmost", True)

    set_bg_transparent(top)
    DragScreenshotPanel(root, top, callback, cancel_callback)