import tkinter as tk
import pyautogui
import cv2
import datetime
import os
from PIL import Image, ImageTk
import numpy as np
import threading
import time

class Application:
    def __init__(self, master):
        self.master = master
        self.snip_surface = None
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.rect = None
        self.tracking_image = None
        self.tracking_active = False
        
        # Setup main window
        self.master.geometry('400x200+200+200')
        self.master.title('Screen Tracker')
        
        # Create frames and buttons
        self.menu_frame = tk.Frame(master)
        self.menu_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.snip_button = tk.Button(
            self.menu_frame, 
            text="Select Region", 
            command=self.create_screen_canvas, 
            bg="green", 
            fg="white"
        )
        self.snip_button.pack(pady=10)
        
        self.track_button = tk.Button(
            self.menu_frame, 
            text="Start Tracking", 
            command=self.toggle_tracking, 
            bg="blue", 
            fg="white", 
            state=tk.DISABLED
        )
        self.track_button.pack(pady=10)
        
        # Text area to display coordinates
        self.coord_text = tk.Text(
            self.menu_frame, 
            height=10, 
            width=50
        )
        self.coord_text.pack(pady=10)
        
        # Prepare full-screen overlay
        self.master_screen = tk.Toplevel(master)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "maroon3")
        
        self.picture_frame = tk.Frame(self.master_screen, background="maroon3")
        self.picture_frame.pack(fill=tk.BOTH, expand=True)

    def create_screen_canvas(self):
        # Reset previous tracking
        self.tracking_image = None
        self.track_button.config(state=tk.DISABLED)
        
        # Show full-screen overlay for snipping
        self.master_screen.deiconify()
        self.master.withdraw()
        
        self.snip_surface = tk.Canvas(
            self.picture_frame, 
            cursor="cross", 
            bg="grey11"
        )
        self.snip_surface.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.snip_surface.bind("<ButtonPress-1>", self.on_button_press)
        self.snip_surface.bind("<B1-Motion>", self.on_snip_drag)
        self.snip_surface.bind("<ButtonRelease-1>", self.on_button_release)
        
        # Set screen overlay properties
        self.master_screen.attributes('-fullscreen', True)
        self.master_screen.attributes('-alpha', 0.3)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)

    def on_button_press(self, event):
        # Save initial mouse position
        self.start_x = self.snip_surface.canvasx(event.x)
        self.start_y = self.snip_surface.canvasy(event.y)
        
        # Create rectangle for selection visualization
        self.rect = self.snip_surface.create_rectangle(
            0, 0, 1, 1, 
            outline='red', 
            width=3, 
            fill="maroon3"
        )

    def on_snip_drag(self, event):
        # Update current mouse position and rectangle
        self.current_x, self.current_y = (event.x, event.y)
        self.snip_surface.coords(
            self.rect, 
            self.start_x, 
            self.start_y, 
            self.current_x, 
            self.current_y
        )

    def on_button_release(self, event):
        # Ensure coordinates are integers and calculate region
        start_x = int(min(self.start_x, self.current_x))
        start_y = int(min(self.start_y, self.current_y))
        width = int(abs(self.current_x - self.start_x))
        height = int(abs(self.current_y - self.start_y))
        
        # Ensure minimum region size
        width = max(width, 1)
        height = max(height, 1)
        
        # Take screenshot and save
        screenshot = pyautogui.screenshot(region=(start_x, start_y, width, height))
        filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_snip.png")
        
        # Ensure snips directory exists
        if not os.path.exists("snips"):
            os.makedirs("snips")
        
        filepath = os.path.join("snips", filename)
        screenshot.save(filepath)
        
        # Save screenshot image for tracking
        self.tracking_image = cv2.imread(filepath)
        
        # Exit screenshot mode and re-enable tracking
        self.exit_screenshot_mode()
        self.track_button.config(state=tk.NORMAL)

    def exit_screenshot_mode(self):
        # Clean up screen overlay
        self.snip_surface.destroy()
        self.master_screen.withdraw()
        self.master.deiconify()

    def toggle_tracking(self):
        if not self.tracking_active and self.tracking_image is not None:
            # Start tracking
            self.tracking_active = True
            self.track_button.config(text="Stop Tracking", bg="red")
            self.tracking_thread = threading.Thread(target=self.track_movement)
            self.tracking_thread.start()
        else:
            # Stop tracking
            self.tracking_active = False
            self.track_button.config(text="Start Tracking", bg="blue")

    def track_movement(self):
        while self.tracking_active:
            try:
                # Find image on screen
                location = pyautogui.locateCenterOnScreen(
                    self.tracking_image, 
                    confidence=0.9
                )
                
                if location:
                    x, y = location
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Update text area with coordinates
                    self.coord_text.insert(tk.END, f"{timestamp}: X={x}, Y={y}\n")
                    self.coord_text.see(tk.END)
                
                time.sleep(1)  # Check every second
            
            except pyautogui.ImageNotFoundException:
                # Image not found
                self.coord_text.insert(tk.END, "Image not found on screen\n")
                self.coord_text.see(tk.END)
                time.sleep(1)
            except Exception as e:
                # Handle other potential errors
                self.coord_text.insert(tk.END, f"Error: {str(e)}\n")
                self.coord_text.see(tk.END)
                break

def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()

if __name__ == '__main__':
    main()