import pyautogui
import cv2
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Test")
        self.geometry("400x600")

        self.expression = ""
        self.input_text = tk.StringVar()
        self.my_label = ""

        self.create_widgets()
        self.input_image()
        
    def input_image(self):
        link = askopenfilename()
        my_img = ImageTk.PhotoImage(Image.open(link))
        self.my_label.configure(image=my_img)
        self.my_label.image = my_img
        
    def create_widgets(self):

        input_frame = tk.Frame(self, height=100, bd=0, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        input_frame.pack(side=tk.TOP)

        input_field = tk.Entry(input_frame, font=('arial', 18, 'bold'), textvariable=self.input_text, width=50, bg="#eee", bd=0, justify=tk.RIGHT)
        input_field.grid(row=0, column=0)
        input_field.pack(ipady=10)
        
        btns_frame = tk.Frame(self, bg="grey")
        btns_frame.pack()
        
        button_quit = tk.Button(btns_frame, text='Exit Program', command=btns_frame.quit)
        button_quit.pack()
        
        my_label = tk.Label()
        my_label.pack()
        
        inputImgBtn = tk.Button(btns_frame, text='Image Upload', command=self.input_image(), bg='pink', fg='white')
        inputImgBtn.pack()


        # btns_frame = tk.Frame(self, bg="grey")
        # btns_frame.pack()

        # buttons = [
        #     '7', '8', '9', 'C',
        #     '4', '5', '6', '/',
        #     '1', '2', '3', '*',
        #     '0', '.', '=', '+',
        #     '-', '(', ')'
        # ]

        # row = 0
        # col = 0

        # for button in buttons:
        #     action = lambda x=button: self.on_button_click(x)
        #     tk.Button(btns_frame, text=button, width=10, height=3, bd=0, bg="#fff", cursor="hand2", command=action).grid(row=row, column=col, padx=1, pady=1)
        #     col += 1
        #     if col > 3:
        #         col = 0
        #         row += 1

    # def on_button_click(self, char):
    #     if char == 'C':
    #         self.expression = ""
    #     elif char == '=':
    #         try:
    #             self.expression = str(eval(self.expression))
    #         except:
    #             messagebox.showerror("Error", "Invalid Input")
    #             self.expression = ""
    #     else:
    #         self.expression += str(char)
    #     self.input_text.set(self.expression)1

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
# def detect_resolution():
#     x, y = pyautogui.size()
#     return x,y
#     # positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
#     # print(positionStr, end='')
#     # print('\b' * len(positionStr), end='', flush=True)

# def locateOnScreen():
#     location = pyautogui.locateCenterOnScreen('test1.png', confidence=0.9)
#     print(location)
    
# locateOnScreen()