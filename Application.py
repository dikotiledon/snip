import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import pystray
import pyautogui
import cv2
import datetime
import os
import numpy as np
import threading
import time
import pytesseract
from PIL import Image

# Ensure Tesseract OCR path is set correctly
# You may need to adjust this path based on your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class MultiTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Multi-Image Tracker with Snipping")
        self.master.geometry('600x800+100+100')
        self.master.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        
        # Snipping related attributes
        self.snip_surface = None
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.rect = None

        # Tracking images and their details
        self.tracking_images = []
        
        # UI Components
        self.setup_ui()



    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # Snip Button
        snip_btn = tk.Button(
            button_frame, 
            text="Snip Screen", 
            command=self.create_screen_canvas,
            bg="green",
            fg="white"
        )
        snip_btn.pack(side=tk.LEFT, padx=5)

        # Add Image Button
        add_image_btn = tk.Button(
            button_frame, 
            text="Add Image", 
            command=self.add_tracking_image,
            bg="blue",
            fg="white"
        )
        add_image_btn.pack(side=tk.LEFT, padx=5)

        # Start Tracking Button
        self.track_btn = tk.Button(
            button_frame, 
            text="Start Tracking", 
            command=self.toggle_tracking,
            bg="blue",
            fg="white",
            state=tk.DISABLED
        )
        self.track_btn.pack(side=tk.LEFT, padx=5)
        # Minimize to tray Button
        minimize_to_tray_btn = tk.Button(
            button_frame, 
            text="Minimize to tray", 
            command=self.minimize_to_tray,
            bg="green",
            fg="white"
        )
        minimize_to_tray_btn.pack(side=tk.RIGHT, padx=5)

        
        # Images Listbox
        self.images_listbox = tk.Listbox(main_frame, height=10)
        self.images_listbox.pack(fill=tk.X, pady=10)

        # Results Text Area
        self.results_text = tk.Text(main_frame, height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Tracking state
        self.tracking_active = False
        self.tracking_thread = None

        # Prepare full-screen overlay
        self.master_screen = tk.Toplevel(self.master)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "maroon3")
        
        self.picture_frame = tk.Frame(self.master_screen, background="maroon3")
        self.picture_frame.pack(fill=tk.BOTH, expand=True)

    def create_screen_canvas(self):
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
        
        # Process the snipped image
        self.process_snipped_image(filepath)
        
        # Exit screenshot mode
        self.exit_screenshot_mode()

    def process_snipped_image(self, filepath):
        try:
            # Read image with OpenCV
            cv_image = cv2.imread(filepath)
            
            # Perform OCR on the image
            pil_image = Image.open(filepath)
            # ocr_text = pytesseract.image_to_string(pil_image).strip()

            # Store image details
            self.tracking_images.append({
                'filepath': filepath,
                'cv_image': cv_image
                # ,'ocr_text': ocr_text]
            })

            # Update listbox
            self.images_listbox.insert(tk.END, os.path.basename(filepath))

            # Enable tracking button if images are added
            self.track_btn.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Could not process snipped image: {str(e)}")

    def add_tracking_image(self):
        # Open file dialog to select image
        filepath = filedialog.askopenfilename(
            title="Select Tracking Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if not filepath:
            return

        # Process selected image
        self.process_snipped_image(filepath)

    def exit_screenshot_mode(self):
        # Clean up screen overlay
        self.snip_surface.destroy()
        self.master_screen.withdraw()
        self.master.deiconify()

    def toggle_tracking(self):
        if not self.tracking_active and self.tracking_images:
            # Start tracking
            self.tracking_active = True
            self.track_btn.config(text="Stop Tracking", bg="red", fg="white")
            
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            
            # Start tracking thread
            self.tracking_thread = threading.Thread(target=self.track_multiple_images)
            self.tracking_thread.start()
        else:
            # Stop tracking
            self.tracking_active = False
            self.track_btn.config(text="Start Tracking", bg="blue", fg="white")

    def track_multiple_images(self):
        while self.tracking_active:
            try:
                # Track each image
                for image_data in self.tracking_images:
                    filepath = image_data['filepath']
                    # ocr_text = image_data['ocr_text']

                    # Try to locate the image on screen
                    try:
                        location = pyautogui.locateCenterOnScreen(
                            filepath, 
                            grayscale=True,
                            confidence=0.8
                        )
                        
                        if location:
                            x, y = location
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(x,y)
                            
                            # start_x = int(min(self.start_x, self.current_x))
                            # start_y = int(min(self.start_y, self.current_y))
                            # width = int(abs(self.current_x - self.start_x))
                            # height = int(abs(self.current_y - self.start_y))
                            
                            # screenshot = pyautogui.screenshot(region=(x - 10, y - 10, 20, 20))

                            # Perform OCR on the captured region
                            # ocr_text = pytesseract.image_to_string(screenshot)
                            # Construct result message
                            result_msg = (
                                f"{timestamp}: "
                                f"Image: {os.path.basename(filepath)} "
                                f"Location: X={x}, Y={y}\n"
                            )
                            
                            # Add OCR text if available
                            # if ocr_text:
                            #     result_msg += f"OCR Text: {ocr_text}\n"
                            
                            # Update results in main thread
                            self.update_results(result_msg)
                    
                    except pyautogui.ImageNotFoundException:
                        # Image not found, log silently
                        pass
                
                # Wait before next scan
                time.sleep(0.5)
            
            except Exception as e:
                print(e)
                # Log any unexpected errors
                error_msg = f"Tracking error: {str(e)}\n"
                self.update_results(error_msg)
                break

    def update_results(self, message):
        # Use after method to update UI from thread safely
        self.master.after(0, self._safe_text_update, message)

    def _safe_text_update(self, message):
        # Append message to results text
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)
    def minimize_to_tray(self):
        self.master.withdraw() 
        image = Image.open("app.ico")
        menu = (pystray.MenuItem('Quit',  self.quit_window), 
                pystray.MenuItem('Show',self.show_window))
        icon = pystray.Icon("name", image, "Application", menu)
        icon.run()
    def quit_window(self, icon):
        icon.stop()
        self.master.destroy()    
    def show_window(self, icon):
        icon.stop()
        self.master.after(0,self.master.deiconify)     
def main():
    root = tk.Tk()
    app = MultiTracker(root)
    root.mainloop()

if __name__ == '__main__':
    main()