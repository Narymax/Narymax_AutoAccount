# 常用util
import os
import tkinter as tk
from tkinter import filedialog
import sys
import pandas as pd


#  兼容打包后程序的路径读取
def get_current_path():
    if getattr(sys,'frozen',False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path

# 读取微信、支付宝账单到pandas DataFrame
def read_paylist_file():
    # 打印路径
    current_path = get_current_path()
    print(current_path)
    curpath = current_path
    print(curpath)
    # 读取帐单 文件
    csv_file_path = select_file_from_tk('.csv', show_title='请选择账单文件(支付宝、微信都可以)')
    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    if csv_file_path == '':
        return 'no_file',None
    else:
        csv_file_path = os.path.abspath(csv_file_path)
        try:
            # 仅用于打开支付宝账单，打开微信账单会报错
            df = pd.read_csv(csv_file_path, names=names, skiprows=0, encoding='gbk')
        except Exception as ex:
            # engine='python' 可以打开，但是中文是乱码 encoding='utf-8' 可以打开，中文正常
            df = pd.read_csv(csv_file_path, names=names, skiprows=0, engine='python', encoding='utf-8')
        return 'read_csv_ok',df


# 通过tkinter选择文件，返回文件路径
# file_extension = ".txt"
def select_file_from_tk(file_extension = '',show_title = '请选择文件'):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    # file_path = filedialog.askopenfilename()  # 打开文件选择对话框
    curpath = os.path.dirname(os.path.realpath(__file__))
    curpath = get_current_path()

    try:
        if file_extension != '':
            file_path = filedialog.askopenfilename(initialdir=curpath,title=show_title, filetypes=[(file_extension, "*"+file_extension)])
        else:
            file_path = filedialog.askopenfilename(initialdir=curpath,title=show_title)  # 打开文件选择对话框
        # file_path = filedialog.askopenfilename(filetypes=[("csv格式", "*.csv")])  # 打开指定格式
    except Exception as e:
        print("Error selecting file:", e)
        file_path = None

    root.quit()
    return file_path


# 屏蔽交易号 （默认不屏蔽手机号）
# 交易号判定，连续数字大于9个,(含有手机号的需要超过11个)
def redacte_key_number(df,colum_name,dedacte_phone_number=False,redacte_trade_number=True,redacte_show_char=''):
        # 含有手机号码的匹配行
        mask = extract_phone(df,colum_name)
        df[mask] = replace_continue_number(df[mask],colum_name,num=12,replace_char=redacte_show_char)

        # 不含有手机号码的行
        df[~mask] = replace_continue_number(df[~mask],colum_name,replace_char=redacte_show_char)
        return df

#  提取包含手机的mask
def extract_phone(df,column_name):

        pattern_middle = r'\D1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}\D'  # 匹配中间连续11位数字  aa1731234567bb
        mask_middle = df[column_name].str.contains(pattern_middle, regex=True)
        pattern_begin = r'^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}\D'  # 匹配从头开始连续11位数字 1731234567aa
        mask_begin = df[column_name].str.contains(pattern_begin, regex=True)
        pattern_end = r'\D1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}$'  # 匹配连续11位数字然后结束  aabb1731234567
        mask_end = df[column_name].str.contains(pattern_end, regex=True)
        mask = mask_middle | mask_begin | mask_end
        print("phone number extracted\n")
        print(df[mask])
        return mask


def replace_continue_number(df, colum_name, num=9, replace_char=''):
    pattern = r'(\d{{{0},}})'.format(num)  # 匹配连续出现num位及以上数字
    # 提取连续出现num位及以上数字的行
    matches = df[colum_name].str.extractall(pattern)
    print(matches)  # 打印匹配的结果

    df[colum_name] = df[colum_name].str.replace(pattern, replace_char)
    print("消除连续出现", num, "位及以上的数字，并且替换成\" ", replace_char, "\"\n")
    return df


def auto_calssify_by_keyword(df,first_classify_col='分类',second_classify_col='子分类', match_list_rule=[]):
    df[first_classify_col] = df[first_classify_col].astype(str)
    df[second_classify_col] = df[second_classify_col].astype(str)
    if match_list_rule is None:
        print('没有找到匹配模板')
        return df
    else:
        for match in match_list_rule:
            # 一个match 是一个规则 list
            # print(match)
            # print(type(match))
            # 分类
            first_class = match[0]
            # 子分类
            second_class = match[1]
            # 从第三个开始是【备注+关键词】
            for m in match[2:]:
                if len(m) == 1:
                    continue
                else:
                    # 找匹配
                    result = df[m[0]].str.contains(list2orString(m[1:]))
                    df.loc[result, first_classify_col] = first_class
                    df.loc[result, second_classify_col] = second_class

        return df

# ['He' ,'ui' ,'kk'] -> 'He|ui|kk'
def list2orString(list):
    dstString = ''
    for str in list:
        dstString = dstString + '|' + str
    dstString = dstString[1:]
    return dstString


def check_first_column_contains_string(df, specified_string):
    if df.iloc[:, 0].str.contains(specified_string).any():
        return True
    else:
        return False

def load_html_to_classify_rule_list(info_data,selected_value):
    if selected_value == "随手记":
        print("随手记")




def print_dog_head():
    print("\n\
                           ::\n\
                          :;J7, :,                        ::;7:\n\
                          ,ivYi, ,                       ;LLLFS:\n\
                          :iv7Yi                       :7ri;j5PL\n\
                         ,:ivYLvr                    ,ivrrirrY2X,\n\
                         :;r@Wwz.7r:                :ivu@kexianli.\n\
                        :iL7::,:::iiirii:ii;::::,,irvF7rvvLujL7ur\n\
                       ri::,:,::i:iiiiiii:i:irrv177JX7rYXqZEkvv17\n\
                    ;i:, , ::::iirrririi:i:::iiir2XXvii;L8OGJr71i\n\
                  :,, ,,:   ,::ir@mingyi.irii:i:::j1jri7ZBOS7ivv,\n\
                     ,::,    ::rv77iiiriii:iii:i::,rvLq@huhao.Li\n\
                 ,,      ,, ,:ir7ir::,:::i;ir:::i:i::rSGGYri712:\n\
               :::  ,v7r:: ::rrv77:, ,, ,:i7rrii:::::, ir7ri7Lri\n\
              ,     2OBBOi,iiir;r::        ,irriiii::,, ,iv7Luur:\n\
            ,,     i78MBBi,:,:::,:,  :7FSL: ,iriii:::i::,,:rLqXv::\n\
            :      iuMMP: :,:::,:ii;2GY7OBB0viiii:i:iii:i:::iJqL;::\n\
           ,     ::::i   ,,,,, ::LuBBu BBBBBErii:i:i:i:i:i:i:r77ii\n\
          ,       :       , ,,:::rruBZ1MBBqi, :,,,:::,::::::iiriri:\n\
         ,               ,,,,::::i:  @arqiao.       ,:,, ,:::ii;i7:\n\
        :,       rjujLYLi   ,,:::::,:::::::::,,   ,:i,:,,,,,::i:iii\n\
        ::      BBBBBBBBB0,    ,,::: , ,:::::: ,      ,,,, ,,:::::::\n\
        i,  ,  ,8BMMBBBBBBi     ,,:,,     ,,, , ,   , , , :,::ii::i::\n\
        :      iZMOMOMBBM2::::::::::,,,,     ,,,,,,:,,,::::i:irr:i:::,\n\
        i   ,,:;u0MBMOG1L:::i::::::  ,,,::,   ,,, ::::::i:i:iirii:i:i:\n\
        :    ,iuUuuXUkFu7i:iii:i:::, :,:,: ::::::::i:i:::::iirr7iiri::\n\
        :     :rk@Yizero.i:::::, ,:ii:::::::i:::::i::,::::iirrriiiri::,\n\
         :      5BMBBBBBBSr:,::rv2kuii:::iii::,:i:,, , ,,:,:i@petermu.,\n\
              , :r50EZ8MBBBBGOBBBZP7::::i::,:::::,: :,:,::i;rrririiii::\n\
                  :jujYY7LS0ujJL7r::,::i::,::::::::::::::iirirrrrrrr:ii:\n\
               ,:  :@kevensun.:,:,,,::::i:i:::::,,::::::iir;ii;7v77;ii;i,\n\
               ,,,     ,,:,::::::i:iiiii:i::::,, ::::iiiir@xingjief.r;7:i,\n\
            , , ,,,:,,::::::::iiiiiiiiii:,:,:::::::::iiir;ri7vL77rrirri::\n\
             :,, , ::::::::i:::i:::i:i::,,,,,:,::i:i:::iir;@Secbone.ii:::")
