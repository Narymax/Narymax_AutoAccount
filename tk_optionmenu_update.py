import tkinter as tk

def update_label(selected_value):
    label.config(text="Selected value: " + selected_value)

# Create the main window
window = tk.Tk()

# Create a dropdown list
options = ["aaa", "bbb", "ccc"]
selected_value = tk.StringVar(window)
selected_value.set(options[0])
dropdown_menu = tk.OptionMenu(window, selected_value, *options, command=update_label)
dropdown_menu.pack()

# Create a label
label = tk.Label(window, text="Selected value: " + selected_value.get())
label.pack()

# Start the main event loop
window.mainloop()