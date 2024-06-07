# 常用util
import os
import tkinter as tk
from tkinter import filedialog
import sys
import os.path as op
import numpy as np
import pandas as pd
from datetime import datetime

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
            # 仅用于打开支付宝账单，打开微信、京东账单会报错
            df = pd.read_csv(csv_file_path, names=names, skiprows=0, encoding='gbk')
        except Exception as ex:
            # engine='python' 可以打开，但是中文是乱码 encoding='utf-8' 可以打开，中文正常
            df = pd.read_csv(csv_file_path, names=names, skiprows=0, engine='python', encoding='utf-8')
        return 'read_csv_ok', df


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

#  正则提取包含手机的mask
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


def auto_calssify_by_keyword(df,first_classify_col='分类',second_classify_col='子分类', match_list_rule=[], trade_type = '交易类型',redfund_income_classify = True):
    df[first_classify_col] = df[first_classify_col].astype(str)
    df[second_classify_col] = df[second_classify_col].astype(str)
    if match_list_rule is None:
        print('没有找到匹配模板')
        return df
    else:
        outcome_autoclass_total_num = 0
        income_autoclass_total_num = 0
        for list_vob in match_list_rule:

            # 使用列表推导式删除空字符串
            list = [str(item) for item in list_vob if item != '' or item != np.nan]
            first_class = list[1]
            second_class =list[2]

            if len(list) <= 3:
                continue
            else:
                # 支出自动分类
                result = (df['备注'].str.contains(list2orString(list[3:]))) & (df[trade_type].str.contains('支'))
                df.loc[result, first_classify_col] = first_class
                df.loc[result, second_classify_col] = second_class
                modified_outcome_rows = df.loc[result]
                if not modified_outcome_rows.empty:
                    df.loc[result, first_classify_col] = first_class
                    df.loc[result, second_classify_col] = second_class
                    outcome_autoclass_total_num += len(modified_outcome_rows)
                    print("Modified outcome rows:")
                    print(modified_outcome_rows)
        print(f"Total modified outcome rows: {outcome_autoclass_total_num}")
        print("\n \n ")

        # 收入退款分类
        if redfund_income_classify:
            result = df[trade_type].str.contains('收') & df['备注'].str.contains('退款')
            df.loc[result, first_classify_col] = "退款"
            df.loc[result, second_classify_col] = "退款"
            modified_income_rows = df.loc[result]
            if not modified_income_rows.empty:
                df.loc[result, first_classify_col] = "退款"
                df.loc[result, second_classify_col] = "退款"
                income_autoclass_total_num += len(modified_income_rows)
                print("Modified income rows:")
                print(modified_income_rows)

        print(f"Total modified income rows: {income_autoclass_total_num}")
        print("\n \n ")
        return df


def add_count_prefix_character(df, account_name='', account_name2 ='',prefix_character=''):

    if prefix_character != '':
        if account_name != '':
            # df[account_name] = prefix_character + df[account_name]
            # 检查并添加前缀到 account_name 列
            df[account_name] = df[account_name].apply(lambda x: prefix_character + x if x != '' else x)
        if account_name2 != '':
            df[account_name2] = df[account_name2].apply(lambda x: prefix_character + x if x != '' else x)

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

# 使用正则表达式从'账户'列提取"&YYY"格式的字符串
# 将提取出的字符串加到'备注'列的对应行后面
# 从'账户'列删除"&YYY"格式的字符串
def cut_df_Acol_tails_to_Bcol(df,Acol_name='账户',Bcol_name='备注', sep='&'):
    df['extracted'] = df[Acol_name].str.extract(r'(&\w+)$')
    df[Bcol_name] = df[Bcol_name].str.cat(df['extracted'].fillna(''), sep='')
    df[Acol_name] = df[Acol_name].str.replace(r'&\w+$', '')
    df.drop('extracted', axis=1, inplace=True)
    return df

def match_phone_number():
    # 匹配手机号
    # 创建示例数据
    data = {'ID': [1, 2, 3, 4, 5],
            'column_name': ['abc123456789def', '12345678900', 'xyz456789', '123456789012', '15995705685']}
    df = pd.DataFrame(data)

    # 使用正则表达式筛选出含有连续11位数字的行
    pattern = r'^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}$'  # 匹配连续11位数字
    mask = df['column_name'].str.contains(pattern, regex=True)
    filtered_rows = df[mask]

    # 输出结果
    print(filtered_rows)


def delete_much_than_9_nums():
    # 创建示例数据
    data = {'ID': [1, 2, 3, 4],
            'column_name': ['abc123456789def', '12345678900', 'xyz456789', '123456789012']}
    df = pd.DataFrame(data)

    # 删除连续出现9位及以上数字的行
    pattern = r'\d{9,}'  # 匹配连续出现9位及以上数字
    df['column_name'] = df['column_name'].str.replace(pattern, '')  # 将匹配到的数字替换为空字符串
    filtered_rows = df[df['column_name'].str.len() > 0]  # 筛选出替换后不为空的行

    # 输出结果
    print(filtered_rows)


#  提取包含手机的mask
def extract_phone(df, column_name):
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


# 屏蔽交易号 （默认不屏蔽手机号）
# 交易号判定，连续数字大于9个,(含有手机号的需要超过11个)
def redacte_key_number(df, colum_name, dedacte_phone_number=False, redacte_trade_number=True, redacte_show_char=''):
    # 含有手机号码的匹配行
    mask = extract_phone(df, colum_name)
    df[mask] = replace_continue_number(df[mask], colum_name, num=12, replace_char=redacte_show_char)

    # 不含有手机号码的行
    df[~mask] = replace_continue_number(df[~mask], colum_name, replace_char=redacte_show_char)
    return df


def write_dst_template_file(df, src_name, dst_app_name):
    # 变成指定app 模板
    if dst_app_name == '随手记':
        # 一步完成列名修改、增加新列和重新排序
        df = (
            df.rename(columns={"一级分类名称": "分类", "二级分类名称": "子分类", "账户": "账户1", "*账户": "账户2",
                               "支付渠道": "商家"})
            .reindex(columns=['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目',
                              '备注'])
        )
        print("完成 " + dst_app_name + "账单适配")

    file_name = datetime.now().strftime('%Y-%m-%d %H_%M_%S ') + dst_app_name + '导入' + src_name +'.xls'
    with pd.ExcelWriter(op.join(str(get_current_path()), file_name)) as writer:
        # 不保存序号
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    print("导出文件完成: " + op.join(str(get_current_path()), file_name))

    print("")
    return

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

if __name__ == '__main__':


        data = {'ID': [1, 2, 3, 4,5,6,7],
                'column_name': ['abc123456789def', '12345678900', 'xyz456789', '123456789012','15995705685#154546464875643434','er15995700000sd','01234567']}
        df = pd.DataFrame(data)
        df = redacte_key_number(df,'column_name',redacte_show_char="****")
        print(df)
        print("test")
