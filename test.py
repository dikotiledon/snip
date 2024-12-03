import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Test")
        self.geometry("400x600")

        self.image_path = None  # Store the path of the selected image
        self.my_label = tk.Label()
        self.my_label.pack()

        self.create_widgets()

    def create_widgets(self):
        input_frame = tk.Frame(self, height=100, bd=0, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        input_frame.pack(side=tk.TOP)

        input_field = tk.Entry(input_frame, font=('arial', 18, 'bold'), text="", width=50, bg="#eee", bd=0, justify=tk.RIGHT)
        input_field.grid(row=0, column=0)
        input_field.pack(ipady=10)

        btns_frame = tk.Frame(self, bg="grey")
        btns_frame.pack()

        button_quit = tk.Button(btns_frame, text='Exit Program', command=self.quit)
        button_quit.pack()

        inputImgBtn = tk.Button(btns_frame, text='Image Upload', command=self.input_image, bg='pink', fg='white')
        inputImgBtn.pack()

    def input_image(self):
        self.image_path = askopenfilename()  # Get the file path of the selected image

        if self.image_path:
            try:
                my_img = ImageTk.PhotoImage(Image.open(self.image_path))
                self.my_label.configure(image=my_img)
                self.my_label.image = my_img
            except FileNotFoundError:
                messagebox.showerror("Error", "Invalid image file selected.")

if __name__ == "__main__":
    app = App()
    app.mainloop()