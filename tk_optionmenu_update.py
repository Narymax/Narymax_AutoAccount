import tkinter as tk

def update_label_app(selected_value):
    label_app.config(text="选择配置账本: " + selected_value)

# Create the main window
window = tk.Tk()

# Create a dropdown list
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
selected_value = tk.StringVar(window)
selected_value.set(options[0])
dropdown_menu = tk.OptionMenu(window, selected_value, *options, command=update_label_app)
dropdown_menu.pack()

# Create a label
label_app = tk.Label(window, text="Selected value: " + selected_value.get())
label_app.pack()
# 后面把小明改成默认从class中读的值
label_user = tk.Label(window, text="用户: " + "小明")
label_user.pack()

button_load_html = tk.Button(window, text="生成分类模板", command=None)
button_load_html.pack()

button_user_config = tk.Button(window, text="修改用户config", command=None)
button_user_config.pack()

button_keywords_aclasify = tk.Button(window, text="导入关键字分类模板", command=None)
button_keywords_aclasify.pack()

button_paylist_convert = tk.Button(window, text="自动账单转换", command=None)
button_paylist_convert.pack()



# Start the main event loop
window.mainloop()