import tkinter as tk
from tkinter import filedialog

def open_file_and_display():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            text_label.config(text=content)
    else:
        text_label.config(text="No file selected")

root = tk.Tk()
root.title("File Content Display")

open_button = tk.Button(root, text="Open File", command=open_file_and_display)
open_button.pack(pady=10)

text_label = tk.Label(root, text="", wraplength=400, justify="left")
text_label.pack(pady=10)

root.mainloop()