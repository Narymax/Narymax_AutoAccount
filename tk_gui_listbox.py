import tkinter as tk

def button_click():
    selected_index = listbox.curselection()
    if selected_index:
        selected_value = options[selected_index[0]]
        label1.config(text="Selected value: " + selected_value)
        label2.config(text="Button clicked!")

# Create the main window
window = tk.Tk()

# Create a Listbox
options = [ "随手记",
    "Timi时光记账",
    "口袋记账",
    "可萌记账",
    "挖财记账",
    "有鱼记账",
    "松鼠记账",
    "洋葱记账",
    "百事AA记账",
    "薄荷记账",
    "记账·海豚记账本",
    "钱迹",
    "鲨鱼记账"
]
listbox = tk.Listbox(window, selectmode=tk.SINGLE)
for option in options:
    listbox.insert(tk.END, option)
listbox.pack()

# Set the default selection
listbox.selection_set(0)

# Create two labels
label1 = tk.Label(window, text="Label 1")
label1.pack()

label2 = tk.Label(window, text="Label 2")
label2.pack()

# Create a button
button = tk.Button(window, text="Click me", command=button_click)
button.pack()

# Start the main event loop
window.mainloop()