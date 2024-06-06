
import pandas as pd
import os.path as op
from info_class import InfoClass
from util import redacte_key_number
from util import get_current_path
from util import auto_calssify_by_keyword
from util import init_df_columns
from util import add_count_prefix_character
from datetime import datetime

def wechat_paybill_conv_dev(df, info_data, dst_app):
    # df 列说明
    # 交易时间	     交易类型 交易对方	商品	收/支	金额(元)	支付方式	当前状态	交易单号	商户单号	备注
    # 2024-04-02 18:31:00,商户消费,肯德基,KFC全家桶,支出,¥32.90,中国银行信用卡(0123),已存入零钱,"42000012345890	","202405666678",/
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
    # 去金额里面的人民币符号 ¥ 和 备注的 / 一级分类的 |
    df['金额'] = df['金额'].str.replace('¥', '')
    df['备注'] = df['备注'].str.replace('/', '')
    df['一级分类名称'] = df['一级分类名称'].str.replace('|', '')

    # 红包 转账  对应账户   /  ->   微信零钱
    condition_wechat_changes = (df['交易类型'] == '收入') & (df['当前状态'] == '已存入零钱') & ( df['一级分类名称'].str.contains('红包|转账') )
    df.loc[condition_wechat_changes,'账户'] = '微信零钱'

    # 屏蔽敏感交易号
    df = redacte_key_number(df,'备注',redacte_show_char="****")

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
    # 变成指定app 模板
    if dst_app == '随手记':
        # 一步完成列名修改、增加新列和重新排序
        df = (
            df.rename(columns={"一级分类名称": "分类", "二级分类名称": "子分类", "账户": "账户1", "*账户": "账户2",
                               "支付渠道": "商家"})
            .reindex(columns=['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目',
                              '备注'])
        )
        print("完成 " + dst_app + "账单适配")

    file_name = datetime.now().strftime('%Y-%m-%d %H_%M_%S ') + dst_app + '导入微信账单.xls'
    with pd.ExcelWriter(op.join(str(get_current_path()), file_name)) as writer:
        # 不保存序号
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    print("导出文件完成: " + op.join(str(get_current_path()), file_name))

    print("")
    return


def wechat_paybill_conv(df, info_data):
    print("wechat list")
    flag = 'wechat'
    family = info_data.character

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
    data_verbose['记账人'] = info_data.user
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
    # 备注列放到最后
    column_to_move = data_verbose.pop('K')
    data_verbose.insert(10, 'K', column_to_move)

    data_verbose.rename(columns={'C': '交易对方', 'D': '商品', 'A': '交易时间', 'F': '金额', 'E': '收/支',
                                 'G': '支付账号', 'classify': '分类', '交易渠道': '支付渠道', 'K': '账单原始备注'},
                        inplace=True)
    data_verbose.sort_values('交易时间', inplace=True)

    # 备注信息尽量保留
    data_verbose['备注'] = data_verbose['商品'] + '#' + data_verbose['交易对方'] + data_verbose['账单原始备注']
    # 敏感交易号屏蔽
    data_verbose = redacte_key_number(data_verbose, '备注', redacte_show_char="****")
    data_verbose['成员'] = info_data.user
    result_pay = data_verbose['收/支'].str.contains('支出')
    data_verbose.loc[result_pay, '项目'] = info_data.default_proj_name
    data_verbose['子分类'] = '未分类'
    data_verbose['账户2'] = ''
    data_verbose['商家'] = '微信支付'

    # 改名
    data_verbose.rename(columns={'交易时间': '日期', '收/支': '交易类型', '支付账号': '账户1', '分类': '分类'},
                        inplace=True)

    # save_vobose_str = "save_vob"    # "not_save_vob"
    save_vobose_str = "not_save_vob"
    if save_vobose_str == "save_vob":
        new_order = ['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目', '备注',
                 '交易对方', '商品', '账单原始备注']
    else:
        new_order = ['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目', '备注']
    dstDf = data_verbose[new_order]

    # 根据关键字匹配，自动调整二级自动分类
    dstDf = auto_calssify_by_keyword(dstDf, match_list_rule=info_data.classify_csv_rule)

    dstDf.to_excel(op.join(get_current_path(), "随手记导入微信账单.xls"), encoding="utf_8_sig", index=False)


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