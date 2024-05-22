import tkinter as tk
from info_class import InfoClass
from util import print_dog_head
from util import read_paylist_file
from util import check_first_column_contains_string
from wechat_paybill_convert import wechat_paybill_conv
from ali_paybill_convert import ali_paybill_conv

import warnings

def update_label_app(selected_value):
    label_app.config(text="选择配置账本: " + selected_value)
    if selected_value == "随手记":
        for button in button_list:
            button.config(state=tk.NORMAL)
    else:
        for button in button_list:
            button.config(state=tk.DISABLED)


def load_html_convert_to_yaml(info_data):
        flag = info_data.get_match_list_from_tk()
        # button_load_html.config(text="完成")
        if flag:
            button_load_html.config(text="上传本地网页，生成分类模板，完成！")
            info_data.create_auto_classify_template()
            print("导入html成功")
        window.mainloop()

def load_user_config(info_data):
    flag = info_data.get_user_info_from_tk()
    if flag:
        button_user_config.config(text="用户config文件更新，完成！")
        print("用户config文件修改，完成")
        label_user.config(text="用户: " + info_data.user)
    window.mainloop()

def load_keywords_clasif_yaml(info_data):
    flag = info_data.get_match_template_from_tk()
    if flag:
        button_keywords_aclasify.config(text="分类模板读取，完成！")
        print("关键字分类模板读取，完成")
    window.mainloop()

def paylist_convert(info_data):
    file_type = ''
    flag, df = read_paylist_file()
    if flag == 'no_file':
        print("读取支付单文件失败")
        window.mainloop()
        return
    else:
        if df.at[0, 'A'].find('微信') != -1:
            file_type = '微信'
            wechat_paybill_conv(df, info_data)
        elif check_first_column_contains_string(df,"支付宝"):
            file_type = '支付宝'
            ali_paybill_conv(df,info_data)
        else:
            print("目前尚不支持的支付单格式")

        button_paylist_convert.config(text="转换" + file_type + "账单完成！继续点击转换！")
        window.mainloop()

if __name__ == "__main__":

    warnings.filterwarnings("ignore")

    print("富强、民主、文明、和谐、自由、平等、公正、法治、爱国、敬业、诚信、友善")

    print_dog_head()

    print("欢迎使用自动记账工具V1.1\n")
    print("目前只支持随手记，读取微信支付宝账单\n \n \n \n")
    print("教程：https://gitee.com/Naymax/Narymax_AutoAccount/blob/main/README.md")


    # Create the main window
    window = tk.Tk()
    window.title("Narymax AutoAccount V1.1")
    window.geometry("400x260")

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

    info_data = InfoClass('小明')

    button_load_html = tk.Button(window, text="上传本地网页，生成分类模板", command=lambda: load_html_convert_to_yaml(info_data))
    button_load_html.pack()

    button_user_config = tk.Button(window, text="用户config文件修改", command=lambda: load_user_config(info_data))
    button_user_config.pack()

    button_keywords_aclasify = tk.Button(window, text="导入关键字分类模板", command=lambda: load_keywords_clasif_yaml(info_data))
    button_keywords_aclasify.pack()

    button_paylist_convert = tk.Button(window, text="微信、支付宝 账单一键转换", command=lambda: paylist_convert(info_data))
    button_paylist_convert.pack()

    button_list = [button_load_html,button_user_config,button_keywords_aclasify,button_paylist_convert]


    # 后面把小明改成默认从class中读的值
    label_user = tk.Label(window, text="用户: " + "小明")
    label_user.pack()

    # Start the main event loop
    window.mainloop()