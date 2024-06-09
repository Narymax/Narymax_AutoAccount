import tkinter as tk
import os
from tkinter import messagebox
from info_class import InfoClass
from util import print_dog_head
from util import read_paylist_file
from util import check_first_column_contains_string
from util import get_current_path
from wechat_paybill_convert import wechat_paybill_conv_dev
from ali_paybill_convert import ali_paybill_conv_dev
from jindong_bill_convert import jindong_bill_conv
import sys
import warnings

def init_df_columns(df, skiprows=0, use_column_name = True):
    df = df.iloc[skiprows+1:]
    first_row = df.iloc[0]
    # 将第一行转换成字符串
    new_column_names = [str(item) if item != "" else df.columns[idx] for idx, item in enumerate(first_row)]
    # 设置新的列名
    df.columns = new_column_names
    print("导入原始账单")
    print(new_column_names)
    # 删除第一行，因为它已经被用作列名
    df = df.drop(df.index[0])
    # 重置索引
    df.reset_index(drop=True, inplace=True)

    return df

def update_label_app(selected_value):
    label_app.config(text="选择配置账本: " + selected_value)
    if (selected_value == "随手记") | (selected_value == "钱迹") | (selected_value == "有鱼记账")|(selected_value == "挖财记账") :
        for button in button_list:
            button.config(state=tk.NORMAL)
    else:
        for button in button_list:
            button.config(state=tk.DISABLED)


def load_config(info_data):
    load_result = info_data.load_config_file_from_tk_window()
    label_user.config(text=info_data.user)

    if load_result == "load .xls":
        button_config_load.config(text="加载配置文件完成！继续点击覆盖当前配置文件！")
    elif load_result == "user abort select":
        pass

    window.mainloop()


def create_config(info_data):
    account_app_name = selected_value.get()
    if account_app_name == "随手记":
        # 获得随手记 二级自定义分类
        result = tk.messagebox.askyesno("是否有html文件", "针对< "+account_app_name+" >是否有本地网页配置文件？")
        if result:
            # load_html_to_classify_rule_list(info_data,selected_value.get())
            info_data.get_classify_name_from_html(account_app_name)
            print("有html文件")
        else:
            print("没有html文件")
    elif account_app_name == "钱迹":
        # 如何获得钱迹 自定义分类？？？ 暂时没想到办法
        pass

    info_data.create_csv_config_file()
    button_config_create.config(text="创建配置文件完成！继续点击创建配置文件！")

    window.mainloop()

def paylist_convert(info_data):
    file_type = ''
    flag, df = read_paylist_file()
    # 获取当前下拉选择记账app 名称
    dst_app = selected_value.get()
    if flag == 'no_file':
        print("读取支付单文件失败")
        window.mainloop()
        return
    else:
        if df.at[0, 'A'].find('微信') != -1:
            file_type = '微信'
            df.fillna('', inplace=True)
            # wechat_paybill_conv(df, info_data)
            df = init_df_columns(df, 15, True)
            wechat_paybill_conv_dev(df, info_data,dst_app)
        elif check_first_column_contains_string(df,"支付宝"):
            file_type = '支付宝'
            df.fillna('', inplace=True)
            # ali_paybill_conv(df,info_data)
            df = init_df_columns(df, 21, True)
            ali_paybill_conv_dev(df, info_data,dst_app)
        elif check_first_column_contains_string(df,"京东账号"):
            file_type = '京东'
            df.fillna('', inplace=True)

            df = init_df_columns(df, 18, True)
            jindong_bill_conv(df,info_data,dst_app)
        else:
            print("目前尚不支持的支付单格式")

        button_paylist_convert.config(text="转换" + file_type + "账单完成！继续点击转换！")
        window.mainloop()
        return

if __name__ == "__main__":

    auto_account_version = 'V1.3'

    print("富强、民主、文明、和谐、自由、平等、公正、法治、爱国、敬业、诚信、友善")
    print_dog_head()

    print("欢迎使用自动记账工具" + auto_account_version + "\n")
    print("目前支持随手记 读取 微信、支付宝、京东 账单\n \n \n \n")
    print("教程：https://gitee.com/Naymax/Narymax_AutoAccount/blob/main/README.md")

    if getattr(sys,'frozen',False):
        # 程序在打包状态下运行，不打印警告
        warnings.filterwarnings("ignore")
    else:
        pass


    # Create the main window
    window = tk.Tk()
    window.title("Narymax AutoAccount "+auto_account_version)
    window.geometry("350x180")
    options = [ "随手记",
                "钱迹",
                "挖财记账",
                "有鱼记账",
                "百事AA记账",
        "Timi时光记账",
        "口袋记账",
        "可萌记账",
        "松鼠记账",
        "洋葱记账",
        "薄荷记账",
        "记账·海豚记账本",
        "鲨鱼记账"
    ]

    # Create a dropdown list
    selected_value = tk.StringVar(window)
    selected_value.set(options[0])
    dropdown_menu = tk.OptionMenu(window, selected_value, *options, command=update_label_app)
    dropdown_menu.pack()

    # Create a label
    label_app = tk.Label(window, text="Selected value: " + selected_value.get())
    label_app.pack()

    current_path = get_current_path()
    config_file_name = current_path + "/config/config.xls"

    if not os.path.exists(config_file_name):
        print(f"Path '{config_file_name}'默认配置文件不存在.")
        info_data = InfoClass('快乐小猴')
    else:
        print(f"Path '{config_file_name}' 默认配置文件already exists，使用config.xls信息初始化.")
        info_data = InfoClass('')
        info_data.load_config_file(config_file_name)

    button_config_load = tk.Button(window, text="加载config文件", command=lambda: load_config(info_data))
    button_config_load.pack()

    button_config_create = tk.Button(window, text="创建config文件", command=lambda: create_config(info_data))
    button_config_create.pack()

    button_paylist_convert = tk.Button(window, text="微信、支付宝、京东 账单一键转换", command=lambda: paylist_convert(info_data))
    button_paylist_convert.pack()

    button_list = [button_paylist_convert,button_config_load,button_config_create]


    # 后面把小明改成默认从class中读的值
    label_user = tk.Label(window, text="用户: " + info_data.user)
    label_user.pack()


    # Start the main event loop
    window.mainloop()