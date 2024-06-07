import pandas as pd
from info_class import InfoClass
from util import init_df_columns
from util import auto_calssify_by_keyword
from util import add_count_prefix_character
from util import redacte_key_number
from util import write_dst_template_file



# df 列说明
# 交易时间, 交易分类, 商户名称, 交易说明, 收 / 支, 金额, 收 / 付款方式, 交易状态, 交易订单号, 商家订单号, 备注
# 2024 - 06 - 02 22: 31:30, 医疗保健, 京东平台商户, H&K 一次性医用外科灭菌口罩, 支出, 14.10, 微信支付, 交易成功, 200000000000, 4000000000000008,
# 变成标准模板 +  "交易说明","商户名称"
# | 交易类型 | 日期 | 一级分类名称 | 二级分类名称 | 账户 | *账户 | 金额 | 成员 | 支付渠道 | 项目 | 备注 | +   "交易说明","商户名称"
#  最后2列是自定义的
def convert_jindong_bill_to_standard_accountlist(df,info_data):
    # 剔除京东与微信支付重复导出的账单
    df = df.drop(df[df['收/付款方式'] == '微信支付'].index)  # 删除指定行
    df = df.drop(df[df['交易状态'] != '交易成功'].index)  # 删除交易没有成功的账单

    df['备注'] = df['备注']+ df['交易说明']+ '#' +df['商户名称']
    df = df.sort_values('交易时间')

    # 定义新列的占位值
    secondClassName_values = ["未分类"] * len(df)
    account2_values = [""] * len(df)
    user_values = [info_data.user] * len(df)
    paymentMethod_values = ["京东"] * len(df)
    projectName_values = [""] * len(df)  # 空字符串
    # delta_values = [None] * len(df)  # 空值 可以是数字
    # 一步完成列名修改、增加新列和重新排序
    df = (
        df.rename(columns={"交易时间": "日期", "交易分类": "一级分类名称","收/支": "交易类型","收/付款方式":"账户"})
        .assign(secondClassName_values=secondClassName_values, account2_values=account2_values, user_values=user_values, paymentMethod_values=paymentMethod_values, projectName_values=projectName_values)
        .rename(columns={"secondClassName_values": "二级分类名称", "account2_values": "*账户", "user_values": "成员", "paymentMethod_values": "支付渠道", "projectName_values": "项目"})  # 将 Delta 列名修改为 得尔塔
        .reindex(columns=["交易类型", "日期", "一级分类名称", "二级分类名称", "账户", "*账户", "金额", "成员", "支付渠道", "项目","备注","交易说明","商户名称"])
    )
    print("完成标准模板转换")

    return df

def jindong_papbill_auto_classify(df,info_data):
    # 筛选还京东白条  交易类型： 不计收支 -> 转账 （类似还信用卡）
    condition_jindongcrediet = (df['交易类型'] == '不计收支') & (df['交易说明'] == '白条主动还款') & (df['商户名称'] == '京东金融')
    df.loc[condition_jindongcrediet, '交易类型'] = "转账"
    df.loc[condition_jindongcrediet, '账户'] = df.loc[condition_jindongcrediet, '账户'] + "还白条"
    df.loc[condition_jindongcrediet, '*账户'] = "京东白条"

    condition_cashout = (df['交易类型'] == '不计收支') & (df['账户'].str.contains('代付')) & (df['交易说明'] == '京东钱包余额提现')
    df.loc[condition_cashout, '交易类型'] = '转账'
    df.loc[condition_cashout, '账户'] = '京东钱包余额'
    df.loc[condition_cashout,'*账户'] = '京东提现账户'

    # 屏蔽敏感交易号
    df = redacte_key_number(df, '备注', redacte_show_char="****")

    # 小金额筛除的
    df.drop(df[df['金额'].astype('float') < info_data.min_pay_filter].index, inplace=True)

    # 支出自动分类
    df = auto_calssify_by_keyword(df,first_classify_col='一级分类名称',second_classify_col='二级分类名称',match_list_rule=info_data.classify_csv_rule)

    # 默认支出项目名称
    if (info_data.default_proj_name != ''):
        condition_default_payout_proj = (df['交易类型'] == '支出')
        df.loc[condition_default_payout_proj,'项目'] = info_data.default_proj_name

    # 账户前面加 字母编号
    # 银行卡 -> M银行卡
    df = add_count_prefix_character(df, '账户', '*账户',info_data.character)

    return df

def jindong_bill_conv(df,info_data,dst_app = '随手记'):

    # df 列说明
    # 交易时间, 交易分类, 商户名称, 交易说明, 收 / 支, 金额, 收 / 付款方式, 交易状态, 交易订单号, 商家订单号, 备注
    # 2024 - 06 - 02 22: 31:30, 医疗保健, 京东平台商户, H&K 一次性医用外科灭菌口罩, 支出, 14.10, 微信支付, 交易成功, 200000000000, 4000000000000008,

    # 变成标准模板 +  "交易说明","商户名称"
    # | 交易类型 | 日期 | 一级分类名称 | 二级分类名称 | 账户 | *账户 | 金额 | 成员 | 支付渠道 | 项目 | 备注 | +   "交易说明","商户名称"
    #  最后2列是自定义的

    df = convert_jindong_bill_to_standard_accountlist(df,info_data)

    # 自动分类，对标准模板进行数据处理
    df = jindong_papbill_auto_classify(df,info_data)

    # 写入指定app 模板
    write_dst_template_file(df, src_name='京东', dst_app_name=dst_app)

    return


    # # 变成指定app 模板
    # if dst_app == '随手记':
    #     # 一步完成列名修改、增加新列和重新排序
    #     df = (
    #         df.rename(columns={"一级分类名称":"分类","二级分类名称":"子分类","账户": "账户1","*账户": "账户2","支付渠道":"商家"})
    #         .reindex(columns=['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目', '备注'])
    #     )
    #     print("完成 " + dst_app + "账单适配")
    #
    #
    # file_name = datetime.now().strftime('%Y-%m-%d %H_%M_%S ')+ dst_app + '导入京东账单.xls'
    # with pd.ExcelWriter(op.join(get_current_path(), file_name)) as writer:
    #     # 不保存序号
    #     df.to_excel(writer, sheet_name='Sheet1', index=False)
    #
    # print("导出文件完成: " + op.join(get_current_path(), file_name))



if __name__ == "__main__":


    # 读取帐单 文件
    csv_file_path = "C:\\Users\\admin\\Downloads\\bill_20240602225321868_124.csv"
    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    try:
        # 仅用于打开支付宝账单，打开微信、京东账单会报错
        df = pd.read_csv(csv_file_path, names=names, skiprows=0, encoding='gbk')
    except Exception as ex:
        # engine='python' 可以打开，但是中文是乱码 encoding='utf-8' 可以打开，中文正常
        df = pd.read_csv(csv_file_path, names=names, skiprows=0, engine='python', encoding='utf-8')

    df.fillna('', inplace=True)

    df = init_df_columns(df,18,True)

    userInfo =  InfoClass(user="小明")
    xls_path = "D:\\Roots\\2024-01-29pay_list_csv_import\\my_personal_data\\config\\config.xls"
    userInfo.load_config_file(xls_path)
    df = jindong_bill_conv(df,userInfo)
    #  导出随手记web 格式账单
    # with pd.ExcelWriter(op.join(get_current_path(), '随手记导入京东账单.xls')) as writer:
    #     # 不保存序号
    #     df.to_excel(writer, sheet_name='Sheet1', index=False)



