
import pandas as pd
from info_class import InfoClass
from util import redacte_key_number
from util import auto_calssify_by_keyword
from util import init_df_columns
from util import add_count_prefix_character
from util import write_dst_template_file



# 微信原始数据
# 交易时间	     交易类型 交易对方	商品	收/支	金额(元)	支付方式	当前状态	交易单号	商户单号	备注
# 2024-04-02 18:31:00,商户消费,肯德基,KFC全家桶,支出,¥32.90,中国银行信用卡(0123),已存入零钱,"42000012345890	","202405666678",/
# 变成标准模板
# | 交易类型 | 日期 | 一级分类名称 | 二级分类名称 | 账户 | *账户 | 金额 | 成员 | 支付渠道 | 项目 | 备注 | +   "交易对方","当前状态"
def convert_wechat_paybill_to_standard_accountlist(df, info_data):
    df['备注'] = df['备注']+ df['商品']+ '#' +df['交易对方']
    df = df.sort_values('交易时间')

    # 定义新列的占位值
    secondClassName_values = ["未分类"] * len(df)
    account2_values = [""] * len(df)
    user_values = [info_data.user] * len(df)
    paymentMethod_values = ["微信"] * len(df)
    projectName_values = [""] * len(df)  # 空字符串
    # 一步完成列名修改、增加新列和重新排序
    df = (
        df.rename(columns={"交易时间": "日期", "交易类型":"一级分类名称","收/支": "交易类型", "金额(元)": "金额", "支付方式": "账户"})
        .assign(secondClassName_values=secondClassName_values, account2_values=account2_values, user_values=user_values,
                paymentMethod_values=paymentMethod_values, projectName_values=projectName_values)
        .rename(columns={"secondClassName_values": "二级分类名称", "account2_values": "*账户", "user_values": "成员",
                         "paymentMethod_values": "支付渠道", "projectName_values": "项目"})
        .reindex(
            columns=["交易类型", "日期", "一级分类名称", "二级分类名称", "账户", "*账户", "金额", "成员", "支付渠道",
                     "项目", "备注", "商品", "交易对方","当前状态"])
    )

    return df


def wechat_paybill_auto_classify(df,info_data):
    # 去金额里面的人民币符号 ¥ 和 备注的 / 一级分类的 |
    df['金额'] = df['金额'].str.replace('¥', '')
    df['备注'] = df['备注'].str.replace('/', '')
    df['一级分类名称'] = df['一级分类名称'].str.replace('|', '')

    # 红包 转账  对应账户   /  ->   微信零钱
    condition_wechat_changes = (df['交易类型'] == '收入') & (df['当前状态'] == '已存入零钱') & (
        df['一级分类名称'].str.contains('红包|转账'))
    df.loc[condition_wechat_changes, '账户'] = '微信零钱'

    # 屏蔽敏感交易号
    df = redacte_key_number(df, '备注', redacte_show_char="****")

    # 小金额筛除的
    df.drop(df[df['金额'].astype('float') < info_data.min_pay_filter].index, inplace=True)

    # 支出自动分类
    df = auto_calssify_by_keyword(df, first_classify_col='一级分类名称', second_classify_col='二级分类名称',
                                  match_list_rule=info_data.classify_csv_rule)

    # 默认支出项目名称
    if info_data.default_proj_name != '':
        condition_default_payout_proj = (df['交易类型'] == '支出')
        df.loc[condition_default_payout_proj, '项目'] = info_data.default_proj_name

    # 账户前面加 字母编号
    # 银行卡 -> M银行卡
    df = add_count_prefix_character(df, '账户', '*账户', info_data.character)

    return df


def wechat_paybill_conv_dev(df, info_data, dst_app):
    # df 列说明
    # 交易时间	     交易类型 交易对方	商品	收/支	金额(元)	支付方式	当前状态	交易单号	商户单号	备注
    # 2024-04-02 18:31:00,商户消费,肯德基,KFC全家桶,支出,¥32.90,中国银行信用卡(0123),已存入零钱,"42000012345890	","202405666678",/

    # 变成标准模板
    # | 交易类型 | 日期 | 一级分类名称 | 二级分类名称 | 账户 | *账户 | 金额 | 成员 | 支付渠道 | 项目 | 备注 | +   "交易对方","当前状态"
    # 最后两列是自定义的
    df = convert_wechat_paybill_to_standard_accountlist(df, info_data)

    # 自动分类，对标准模板进行数据处理
    df = wechat_paybill_auto_classify(df,info_data)


    # 写入指定app 模板
    write_dst_template_file(df,src_name='微信',dst_app_name=dst_app)

    return




if __name__ == "__main__":
    wechat_file_path = "D:\\Roots\\2024-05-17github_narymax_AutoAccount\\Narymax_AutoAccount\\testdata\\微信支付账单(20240322-20240514)快乐小猴的日常微信账单_wechat.csv"
    wechat_file_path =  "D:\\Roots\\2024-01-29pay_list_csv_import\\my_personal_data\\微信支付账单(20240513-20240602)\\微信支付账单(20240513-20240602).csv"
    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    try:
        # 仅用于打开支付宝账单，打开微信、京东账单会报错
        df = pd.read_csv(wechat_file_path, names=names, skiprows=0, encoding='gbk')
    except Exception as ex:
        # engine='python' 可以打开，但是中文是乱码 encoding='utf-8' 可以打开，中文正常
        df = pd.read_csv(wechat_file_path, names=names, skiprows=0, engine='python', encoding='utf-8')

    df.fillna('', inplace=True)

    df = init_df_columns(df,15,True)

    userInfo =  InfoClass(user="小明")
    xls_path = "D:\\Roots\\2024-01-29pay_list_csv_import\\my_personal_data\\config\\config.xls"
    userInfo.load_config_file(xls_path)

    wechat_paybill_conv_dev(df,userInfo,"随手记")


    print("")

    # df = wechat_paybill_conv_dev(df, info_data, dst_app)