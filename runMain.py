
import tkinter as tk
from tkinter import filedialog
from bs4 import BeautifulSoup
from collections import OrderedDict
import pandas as pd
import numpy as np
import yaml
import os
import os.path as op
import sys
from util import select_file_from_tk
from util import get_current_path

def select_directory():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    directory_path = filedialog.askdirectory()  # 打开目录选择对话框
    return directory_path



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def searchStrInStringSeries(list,string):
    for str in list:
        if str in string:
            return True
    return False



# ['He' ,'ui' ,'kk'] -> 'He|ui|kk'
def list2orString(list):
    dstString = ''
    for str in list:
        dstString = dstString + '|' + str
    dstString = dstString[1:]
    return dstString


def select_directory():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    directory_path = filedialog.askdirectory()  # 打开目录选择对话框
    return directory_path


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

def replace_continue_number(df,colum_name,num=9,replace_char=''):
        pattern = r'(\d{{{0},}})'.format(num)   # 匹配连续出现num位及以上数字
        # 提取连续出现num位及以上数字的行
        matches = df[colum_name].str.extractall(pattern)
        print(matches)  # 打印匹配的结果

        df[colum_name] = df[colum_name].str.replace(pattern, replace_char)
        print("消除连续出现",num,"位及以上的数字，并且替换成\" ",replace_char,"\"\n")
        return df

# 屏蔽交易号 （默认不屏蔽手机号）
# 交易号判定，连续数字大于9个,(含有手机号的需要超过11个)
def redacte_key_number(df,colum_name,dedacte_phone_number=False,redacte_trade_number=True,redacte_show_char=''):
        # 含有手机号码的匹配行
        mask = extract_phone(df,colum_name)
        df[mask] = replace_continue_number(df[mask],colum_name,num=12,replace_char=redacte_show_char)

        # 不含有手机号码的行
        df[~mask] = replace_continue_number(df[~mask],colum_name,replace_char=redacte_show_char)
        return df



def auto_classify(df,use_tamplate=True):
    df['分类'] = df['分类'].astype(str)
    df['子分类'] = df['子分类'].astype(str)
    # 使用yaml 导入match规则
    if use_tamplate:
        curpath = os.path.dirname(os.path.realpath(__file__))
        # yamlpath = os.path.join(curpath, "auto_classify_config_tample.yaml")
        yamlpath = os.path.join(get_current_path(), "auto_classify_config_tample.yaml")
        f = open(yamlpath, 'r', encoding='utf-8')
        cfg_str = f.read()
        match_list = yaml.load(cfg_str,Loader=yaml.SafeLoader)
    else:
        match_list = select_file_from_tk('.yaml',show_title='请选择自定义分类关键词文件')

    for match in match_list:
        # 一个match 是一个规则 list
        # print(match)
        # print(type(match))
        #分类
        first_class = match[0]
        #子分类
        second_class = match[1]
        #从第三个开始是【备注+关键词】
        for m in match[2:]:
            if len(m) == 1:
                continue
            else:
                # 找匹配
                result = df[m[0]].str.contains(list2orString(m[1:]))
                df.loc[result, '分类'] = first_class
                df.loc[result, '子分类'] = second_class

    return df

# Function to execute program1.py
def load_sui_html_category():
    html_file_path = select_file_from_tk('.html',
                           show_title='请选择随手记支出分类.html (https://www.sui.com/category/budgetCategory.do)')

    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    li_tags = soup.find_all('li', {'class': 'li-level1'})
    li_tags2 = soup.find_all('li', {'class': 'li-level2'})

    for tag in li_tags:
        # print(tag)
        if 'title' in tag.attrs and tag.find('span'):
            print("一级分类：", tag['title'])
        # 通过span 判断是否是一级标签
        if 'title' in tag.attrs and tag.find('span') is None:
            print("     二级分类：", tag['title'])

    my_dict = OrderedDict()
    key_temp = ''
    value = []

    for tag in li_tags:
        # print(tag)
        if 'title' in tag.attrs and tag.find('span'):
            print("一级分类：", tag['title'])
            key_temp = tag['title']
            my_dict[key_temp] = []
        # 通过span 判断是否是一级标签
        if 'title' in tag.attrs and tag.find('span') is None:
            print("     二级分类：", tag['title'])
            if key_temp != '':
                my_dict[key_temp].append(tag['title'])
            else:
                print('一级分类 is empty')

    # with open('auto_classify_config_tample.yaml', 'r', encoding='utf-8') as file:
    #     data_list = yaml.safe_load(file)

    # 生成自动分类模板
    # [
    #     ['一级分类', '二级分类', ['备注',......待手动添加关键字]],
    #     ['一级分类', '二级分类', ['备注',......待手动添加关键字]],
    #     ['一级分类', '二级分类', ['备注',......待手动添加关键字]],
    #     ....
    # ]
    # 第一层
    list_of_matches = []
    for key, value in my_dict.items():
        for secondClass in value:
            # 第二层
            tempt_list_sec = []
            tempt_list_sec.append(key)
            tempt_list_sec.append(secondClass)
            # 第三层
            tempt_list_third_0 = []
            tempt_list_sec.append(tempt_list_third_0)
            tempt_list_third_0.append('备注')
            # # 第三层
            # tempt_list_third_1 = []
            # tempt_list_sec.append(tempt_list_third_1)
            # tempt_list_third_1.append('交易对方')
            # # 第三层
            # tempt_list_third_2 = []
            # tempt_list_sec.append(tempt_list_third_2)
            # tempt_list_third_2.append('商品')
            # # 第三层
            # tempt_list_third_3 = []
            # tempt_list_sec.append(tempt_list_third_3)
            # tempt_list_third_3.append('账单原始备注')

            list_of_matches.append(tempt_list_sec)

    # 导出自动分类模板
    with open('auto_classify_config_tample.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(list_of_matches, file, allow_unicode=True)



# Function to execute program2.py
def wechat_alipay_bill_convert():
    # 路径
    current_path = get_current_path()

    print(current_path)

    curpath = current_path
    print(curpath)

    yamlpath = select_file_from_tk('.yaml', '请选择配置文件')
    f = open(yamlpath, 'r', encoding='utf-8')
    cfg_str = f.read()

    cfg = yaml.load(cfg_str, Loader=yaml.SafeLoader)

    default_project_name = '家庭支出'
    try:
        user = cfg['user']
        family = cfg['character']
        min_pay = cfg['min_pay_filter']
        default_project_name = cfg['default_proj_name']
    except:
        pass

    print_hi(user)

    # 读取帐单 文件
    csv_file_path = select_file_from_tk('.csv', show_title='请选择账单文件(支付宝、微信都可以)')

    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

    # df = pd.read_csv(csv_file_path, names=names, skiprows=0)

    # for i in ('gbk', 'utf-8', 'gb18030', 'ansi'):
    #     try:
    #         data = pd.read_csv(csv_file_path, encoding=i,error_bad_lines=False)
    #         print(i + 'decode success')
    #     except:
    #         print(i + 'decode fail')

    csv_file_path = os.path.abspath(csv_file_path)
    # csv_file_path = csv_file_path.encode('utf-8')

    try:
        # df = pd.read_csv(csv_file_path, names=names, skiprows=0)
        # 仅用于打开支付宝账单，打开微信账单会报错
        df = pd.read_csv(csv_file_path, names=names, skiprows=0, encoding='gbk')
    except Exception as ex:
        # engine='python' 可以打开，但是中文是乱码 encoding='utf-8' 可以打开，中文正常
        df = pd.read_csv(csv_file_path, names=names, skiprows=0, engine='python', encoding='utf-8')


    if df.at[0, 'A'].find('微信') != -1:
        print("wechat list")
        flag = 'wechat'

        df.fillna('', inplace=True)

        # 收红包  账户 从“/” 调整至“零钱”
        result_wechat_account = df['E'].str.contains('收入') & df['B'].str.contains('微信红包|转账') & df[
            'H'].str.contains('已存入零钱')
        df.loc[result_wechat_account, 'G'] = '零钱'

        # 交易对方 具体商品 时间 金额 收支类型 商户消费or红包or转账 账户 备注
        order = ['C', 'D', 'A', 'F', 'E', 'B', 'G', 'K']
        data_verbose = df[order]
        # 大分类使用微信自己的分类 商户消费 红包 转账
        data_verbose['classify'] = df['B']
        data_verbose['交易渠道'] = '微信'
        data_verbose['记账人'] = user
        data_verbose['项目'] = " "
        # 去人民币符号¥
        data_verbose['F'] = data_verbose['F'].str.replace('¥', '')
        # 去空备注
        data_verbose['K'] = data_verbose['K'].str.replace('/', '')

        data_verbose['G'] = data_verbose['G'].str.replace('零钱', family + '微信零钱')
        # data_verbose['G'] = family + data_verbose['G'].astype('str')
        # 有银行账号的添加家人角色
        bank_match_result = data_verbose['G'].str.contains('银行').fillna(False)

        print(data_verbose.loc[bank_match_result, 'G'])
        data_verbose.loc[bank_match_result, 'G'] = family + data_verbose.loc[bank_match_result, 'G']
        # 删掉前面多余的行
        data_verbose.drop(data_verbose.head(17).index, inplace=True)
        data_verbose['Time'] = pd.to_datetime(data_verbose['A'])
        # data_verbose['A'] = data_verbose['Time'].dt.strftime('%Y/%m/%d')

        # 判断指定列是否包含关键词
        # '红包|转账' 改成  '红包转账'
        data_verbose.loc[data_verbose['B'].str.contains('红包|转账'), 'classify'] = '红包转账'

        # 删除多余的列
        data_verbose.drop('Time', axis=1, inplace=True)
        # data_verbose.drop('B',axis=1,inplace=True)
        # 备注列放到最后
        column_to_move = data_verbose.pop('K')
        # data_verbose.insert(len(data_verbose.columns),'K',column_to_move)
        data_verbose.insert(10, 'K', column_to_move)

        data_verbose.rename(columns={'C': '交易对方', 'D': '商品', 'A': '交易时间', 'F': '金额', 'E': '收/支',
                                     'G': '支付账号', 'classify': '分类', '交易渠道': '支付渠道', 'K': '账单原始备注'},
                            inplace=True)
        data_verbose.sort_values('交易时间', inplace=True)

        # 备注信息尽量保留
        data_verbose['备注'] = data_verbose['商品'] + '#' + data_verbose['交易对方'] + data_verbose['账单原始备注']
        # 敏感交易号屏蔽
        data_verbose = redacte_key_number(data_verbose,'备注',redacte_show_char="****")
        data_verbose['成员'] = user
        result_pay = data_verbose['收/支'].str.contains('支出')
        data_verbose.loc[result_pay, '项目'] = default_project_name
        # data_verbose['项目'] = '家庭支出'
        # data_verbose['分类'] = '未分类'
        data_verbose['子分类'] = '未分类'
        data_verbose['账户2'] = ''
        data_verbose['商家'] = '微信支付'

        # 改名
        data_verbose.rename(columns={'交易时间': '日期', '收/支': '交易类型', '支付账号': '账户1', '分类': '分类'},
                            inplace=True)
        new_order = ['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目', '备注',
                     '交易对方', '商品', '账单原始备注']
        dstDf = data_verbose[new_order]

        # 根据关键字匹配，自动调整二级自动分类
        dstDf = auto_classify(dstDf, use_tamplate=True)

        # dstDf.to_excel("随手记导入wechat.xls",encoding="utf_8_sig",index=False)
        dstDf.to_excel(op.join(get_current_path(), "随手记导入wechat.xls"), encoding="utf_8_sig", index=False)

        # data_verbose.to_csv("notion_wechat.csv",index_label="index_label",encoding="utf_8_sig",index=False)


    # elif df.at[0, 'A'].find('支付宝') != -1:
    elif True:

        print("alipay list")
        flag = 'alipay'

        order = ['交易时间', '交易分类', '交易对方', '对方账号', '商品说明', '收/支', '金额', '收/付款方式', '交易状态',
                 '交易订单号', '商家订单号', '备注', 'M',
                 'N', 'O', 'P']
        alipay_dict = dict(zip(names, order))
        df.rename(columns=alipay_dict, inplace=True)
        df['交易时间'] = pd.to_datetime(df['交易时间'], errors='coerce')  # 将错误设置为'coerce'将强制非法值为NaT
        df = df.dropna(subset=['交易时间'])
        # 删除还款失败、交易关闭 的 数据
        mask = (~df['交易状态'].str.contains('交易关闭|还款失败|已关闭'))
        df = df[mask]

        # 删除自动从支付宝账户余额转入到余利宝的数据（一般是收的红包自动转入余额宝）(收支分类是不确定的)
        # 设置红包直接转到余额宝，而不是先转到支付宝账户余额，再转移到余额宝
        mask = df['交易对方'].str.contains('余额宝') & df['商品说明'].str.contains('转账收款到余额宝') & df[
            '收/支'].str.contains('不计收支') & df['收/付款方式'].str.contains('账户余额')
        df = df[~mask]
        mask = df['收/支'].str.contains('收入') & df['收/付款方式'].isin(['账户余额', np.nan])
        df.loc[mask, '收/付款方式'] = '余额宝'
        # 自动转入的也就到余额宝
        df['收/付款方式'] = df['收/付款方式'].str.replace('账户余额', '余额宝')

        # 把退款成功 的 改成收入
        mask = df['交易状态'].str.contains('退款成功') & df['收/支'].str.contains('不计收支')
        df.loc[mask, '收/支'] = '收入'
        # 把还花呗的改成 支出
        mask = df['交易状态'].str.contains('还款成功') & df['收/支'].str.contains('不计收支') & df[
            '交易对方'].str.contains('花呗|信用购')
        df.loc[mask, '收/支'] = '支出'
        # 自动转入到余额宝的改成收入
        mask = df['商品说明'].str.contains('余额宝-自动转入') & df['收/支'].str.contains('不计收支') | df[
            '商品说明'].str.contains(r'余额宝-\d{4}.\d{2}.\d{2}-收益发放')
        df.loc[mask, '收/支'] = '收入'
        # 支付宝转帐到余额宝的删除（资金腾挪） 不属于支出，也不属于收入
        mask = df['商品说明'].str.contains('支付宝转入到余利宝')
        df = df[~mask]
        # 去掉小于最小金额的
        df.drop(df[df['金额'].astype('float') < min_pay].index, inplace=True)

        # 中信银行信用卡分期(0123) 2期 ->  中信银行信用卡(0123)
        # 冗余内容移动到备注后面
        df['备注'] = df['备注'].fillna('')

        df['账单原始备注'] = df['备注']
        df['收/付款方式'] = df['收/付款方式'].fillna('')
        # mask = df['收/付款方式'].str.contains(r')')
        mask = df['收/付款方式'].str.contains('\)', na=False)
        # df.loc[mask,'temp'] =
        # df['temp'] = df['收/付款方式'].apply(lambda x: '\)'.join(x.split('\)')[1:]))
        # 分期、积分抵、刷卡立减抹零信息 df['temp']
        df['temp'] = df['收/付款方式'].str.split('\)', expand=True).get(1)

        df.loc[mask, '收/付款方式'] = df.loc[mask, '收/付款方式'].str.split(')').str[0] + ")"

        # df['备注'] = df['备注'].str.split('&').str[0]
        df['temp'] = df['temp'].fillna('')
        df['备注'] = df['备注'] + df['商品说明'] + '#' + df['temp'] + '#' + df['交易对方']

        # 屏蔽交易号
        df = redacte_key_number(df,'备注',redacte_show_char="****")

        # df['备注'] = df['备注']  + df['temp']
        # df = df.drop(columns=['temp'])

        df['收/付款方式'] = df['收/付款方式'].str.replace('分期', '')

        # df = df.drop(columns=['temp']) ## drop raise错误
        df['商家'] = '支付宝'
        df['成员'] = user
        parter_pay_result = df['收/付款方式'].str.contains('亲情卡')
        df.loc[parter_pay_result, '收/支'] = '支出'

        result_pay = df['收/支'].str.contains('支出')
        df.loc[result_pay, '项目'] = default_project_name
        # df['项目'] = '家庭支出'

        df['子分类'] = '未分类'
        df['账户2'] = ''

        rename_dict = {'交易时间': '日期', '收/支': '交易类型', '收/付款方式': '账户1', '交易分类': '分类',
                       '商品说明': '商品'}

        df.rename(columns=rename_dict, inplace=True)
        new_order = ['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目', '备注',
                     '交易对方', '商品', '账单原始备注']
        dstDf = df[new_order]

        dstDf = dstDf.sort_values('日期')

        # 根据关键字匹配，自动调整二级自动分类
        dstDf = auto_classify(dstDf, use_tamplate=True)

        #  导出随手记web 格式账单
        with pd.ExcelWriter(op.join(get_current_path(), '支付宝随手记导入.xls')) as writer:
            # 不保存序号
            dstDf.to_excel(writer, sheet_name='Sheet1', index=False)

    print(df.head(5))



if __name__ == "__main__":

    print_hi("富强、民主、文明、和谐、自由、平等、公正、法治、爱国、敬业、诚信、友善")

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

    # Create Tkinter window
    root = tk.Tk()
    root.title("Narymax 随手记帐 V1.0")
    root.geometry("500x300")



    # Create a frame for buttons in the top half of the window
    top_frame = tk.Frame(root)
    top_frame.grid(row=0, column=0, padx=50,pady=50)

    # Create buttons to run program1.py and program2.py
    button1 = tk.Button(top_frame, text="通过html文件导入自定义支出分类", command=load_sui_html_category)
    # button1 = tk.Button(top_frame, text="通过html文件导入自定义支出分类", command=print_hi("Hello World"))

    button1.pack()

    # Create a frame for buttons in the bottom half of the window
    bottom_frame = tk.Frame(root)
    bottom_frame.grid(row=1, column=0, pady=50)

    # button2 = tk.Button(bottom_frame, text="生成微信支付宝帐单(随手记web模板)", command=wechat_alipay_bill_convert)
    button2 = tk.Button(bottom_frame, text="生成微信支付宝帐单(随手记web模板)", command=wechat_alipay_bill_convert)

    button2.pack()


    root.mainloop()

    print("Hello World")