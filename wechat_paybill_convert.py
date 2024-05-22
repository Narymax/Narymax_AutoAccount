
import pandas as pd
import os.path as op
from info_class import InfoClass
from util import redacte_key_number
from util import get_current_path
from util import auto_calssify_by_keyword
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
    dstDf = auto_calssify_by_keyword(dstDf, match_list_rule=info_data.match_list_rule)

    dstDf.to_excel(op.join(get_current_path(), "随手记导入微信账单.xls"), encoding="utf_8_sig", index=False)


