
import pandas as pd
import numpy as np
import os.path as op
from info_class import InfoClass
from util import init_df_columns
from util import redacte_key_number
from util import auto_calssify_by_keyword
from util import get_current_path
from util import add_count_prefix_character
from util import cut_df_Acol_tails_to_Bcol
from util import write_dst_template_file
from datetime import datetime

# 微信原始数据
# 交易时间,交易分类,交易对方,对方账号,商品说明,收/支,金额,收/付款方式,交易状态,交易订单号,商家订单号,备注,
# 2024-02-11 19:02:59,餐饮美食,大润发,fn***@feiniu.com,300080,中国银行信用卡(0000),交易成功,2029,8114,,
#
# 变成标准模板
# | 交易类型 | 日期 | 一级分类名称 | 二级分类名称 | 账户 | *账户 | 金额 | 成员 | 支付渠道 | 项目 | 备注 | +   "交易对方","交易信息","交易状态"
def convert_ali_paybill_to_standard_accountlist(df,info_data):
    # 定义新列的占位值
    secondClassName_values = ["未分类"] * len(df)
    account2_values = [""] * len(df)
    user_values = [info_data.user] * len(df)
    paymentMethod_values = ["支付宝"] * len(df)
    projectName_values = [""] * len(df)  # 空字符串
    # 一步完成列名修改、增加新列和重新排序
    df = (
        df.rename(columns={"交易时间": "日期", "交易分类":"一级分类名称","收/支": "交易类型", "收/付款方式": "账户","商品说明":"交易信息"})
        .assign(secondClassName_values=secondClassName_values, account2_values=account2_values, user_values=user_values,
                paymentMethod_values=paymentMethod_values, projectName_values=projectName_values)
        .rename(columns={"secondClassName_values": "二级分类名称", "account2_values": "*账户", "user_values": "成员",
                         "paymentMethod_values": "支付渠道", "projectName_values": "项目"})
        .reindex(
            columns=["交易类型", "日期", "一级分类名称", "二级分类名称", "账户", "*账户", "金额", "成员", "支付渠道",
                     "项目", "备注", "商品", "交易对方","交易信息","交易状态"])
    )
    df['备注'] = df['备注']+df['交易对方'] + '#' + df['交易信息']


    return df

def ali_paybill_auto_classify(df,info_data):
    #  对标准模板进行数据预计处理，排序，数据清洗。。。
    df = info_data.preprocess_standardize_tample(df)

    # 删除还款失败、交易关闭 的 数据
    mask = (~df['交易状态'].str.contains('交易关闭|还款失败|已关闭'))
    df = df[mask]

    # 删除自动从支付宝账户余额转入到余利宝的数据（一般是收的红包自动转入余额宝）(收支分类是不确定的)
    # 设置红包直接转到余额宝，而不是先转到支付宝账户余额，再转移到余额宝
    mask = df['交易对方'].str.contains('余额宝') & df['交易信息'].str.contains('转账收款到余额宝') & df[
        '交易类型'].str.contains('不计收支') & df['账户'].str.contains('账户余额')
    df = df[~mask]
    mask = df['交易类型'].str.contains('收入') & df['账户'].isin(['账户余额', np.nan])
    df.loc[mask, '账户'] = '余额宝'
    # 自动转入的也就到余额宝
    df['账户'] = df['账户'].str.replace('账户余额', '余额宝')

    # 把退款成功 的 改成收入
    mask = df['交易状态'].str.contains('退款成功') & df['交易类型'].str.contains('不计收支')
    df.loc[mask, '交易类型'] = '收入'
    # 把还花呗的改成 支出
    mask = df['交易状态'].str.contains('还款成功') & df['交易类型'].str.contains('不计收支') & df[
        '交易对方'].str.contains('花呗|信用购')
    df.loc[mask, '交易类型'] = '支出'
    # 自动转入到余额宝的改成收入
    mask = df['交易信息'].str.contains('余额宝-自动转入') & df['交易类型'].str.contains('不计收支') | df[
        '交易信息'].str.contains(r'余额宝-\d{4}.\d{2}.\d{2}-收益发放')
    df.loc[mask, '交易类型'] = '收入'
    # 支付宝转帐到余额宝的删除（资金腾挪） 不属于支出，也不属于收入
    mask = df['交易信息'].str.contains('支付宝转入到余利宝')
    df = df[~mask]
    # 去掉小于最小金额的
    df.drop(df[df['金额'].astype('float') < info_data.min_pay_filter].index, inplace=True)

    # 中信银行信用卡分期(0123) 2期 ->  中信银行信用卡(0123)
    # 冗余内容移动到备注后面
    df['备注'] = df['备注'].fillna('')

    df['账单原始备注'] = df['备注']
    df['账户'] = df['账户'].fillna('')
    # mask = df['账户'].str.contains(r')')
    mask = df['账户'].str.contains('\)', na=False)

    # 分期、积分抵、刷卡立减抹零信息 df['temp']
    df['temp'] = df['账户'].str.split('\)', expand=True).get(1)

    df.loc[mask, '账户'] = df.loc[mask, '账户'].str.split(')').str[0] + ")"

    # df['备注'] = df['备注'].str.split('&').str[0]
    df['temp'] = df['temp'].fillna('')
    df['备注'] = df['备注'] + df['temp']

    df = cut_df_Acol_tails_to_Bcol(df, Acol_name='账户', Bcol_name='备注', sep='&')

    # 自动分类
    df = auto_calssify_by_keyword(df,first_classify_col='一级分类名称',second_classify_col='二级分类名称' ,match_list_rule=info_data.classify_csv_rule)

    # 屏蔽交易号
    df = redacte_key_number(df, '备注', redacte_show_char="****")
    df['账户'] = df['账户'].str.replace('分期', '')

    # 默认支出项目名称
    if info_data.default_proj_name != '':
        condition_default_payout_proj = (df['交易类型'] == '支出')
        df.loc[condition_default_payout_proj, '项目'] = info_data.default_proj_name

    # 账户前面加 字母编号
    # 银行卡 -> M银行卡
    df = add_count_prefix_character(df, '账户', '*账户', info_data.character)

    return df


def ali_paybill_conv_dev(df ,info_data,dst_app):
    # 原始账单格式
    # |交易时间|交易分类|交易对方|对方账号|商品说明|收/支|金额|收/付款方式|交易状态|交易订单号|商家订单号|备注|
    # 2024-02-11 19:02:59,餐饮美食,大润发,fn***@feiniu.com,300080,中国银行信用卡(0000),交易成功,2029,8114,,

    # 变成标准模板 +  "交易对方","交易信息","交易状态"
    # | 交易类型 | 日期 | 一级分类名称 | 二级分类名称 | 账户 | *账户 | 金额 | 成员 | 支付渠道 | 项目 | 备注 | +   "交易对方","交易信息","交易状态"
    #  最后3列是自定义的
    df = convert_ali_paybill_to_standard_accountlist(df,info_data)

    # 自动分类，对标准模板进行数据处理
    df = ali_paybill_auto_classify(df,info_data)

    # 写入指定app 模板
    write_dst_template_file(df,src_name='支付宝',dst_app_name=dst_app)

    return






if __name__ == "__main__":

    wechat_file_path =  "D:\\Roots\\2024-01-29pay_list_csv_import\\dist\\csv_file_input\\deng\\alipay_record_20240223_210448.csv"
    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    try:
        # 仅用于打开支付宝账单，打开微信、京东账单会报错
        df = pd.read_csv(wechat_file_path, names=names, skiprows=0, encoding='gbk')
    except Exception as ex:
        # engine='python' 可以打开，但是中文是乱码 encoding='utf-8' 可以打开，中文正常
        df = pd.read_csv(wechat_file_path, names=names, skiprows=0, engine='python', encoding='utf-8')

    df.fillna('', inplace=True)

    df = init_df_columns(df,21,True)

    userInfo =  InfoClass(user="小明")
    xls_path = "D:\\Roots\\2024-01-29pay_list_csv_import\\my_personal_data\\config\\config.xls"
    userInfo.load_config_file(xls_path)

    ali_paybill_conv_dev(df,userInfo,"随手记")


    print("")
