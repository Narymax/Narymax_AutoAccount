
import pandas as pd
import numpy as np
import os.path as op
from util import redacte_key_number
from util import auto_calssify_by_keyword
from util import get_current_path

def ali_paybill_conv(df ,info_data):
    print("alipay list converting...")
    flag = 'alipay'

    min_pay = info_data.min_pay_filter
    user = info_data.user
    default_project_name = info_data.default_proj_name
    character = info_data.character


    order = ['交易时间', '交易分类', '交易对方', '对方账号', '商品说明', '收/支', '金额', '收/付款方式', '交易状态',
             '交易订单号', '商家订单号', '备注', 'M',
             'N', 'O', 'P']
    names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
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
    df = redacte_key_number(df, '备注', redacte_show_char="****")

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

    # save_vobose_str = "save_vob"    # "not_save_vob"
    save_vobose_str = "not_save_vob"
    if save_vobose_str == "save_vob":
        new_order = ['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目', '备注',
                 '交易对方', '商品', '账单原始备注']
    else:
        new_order = ['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目', '备注']
    dstDf = df[new_order]

    # 有“银行”关键字的 前面添加家人角色 字母
    dstDf_mask = dstDf['账户1'].str.contains('银行').fillna(False)
    dstDf.loc[dstDf_mask, '账户1'] = character + dstDf.loc[dstDf_mask, '账户1']
    # 余额宝 前面加字母
    dstDf['账户1'] = dstDf['账户1'].str.replace('余额宝', character + '余额宝')

    dstDf = dstDf.sort_values('日期')

    # 根据关键字匹配，自动调整二级自动分类
    dstDf = auto_calssify_by_keyword(dstDf, match_list_rule=info_data.classify_csv_rule)

    #  导出随手记web 格式账单
    with pd.ExcelWriter(op.join(get_current_path(), '随手记导入支付宝账单.xls')) as writer:
        # 不保存序号
        dstDf.to_excel(writer, sheet_name='Sheet1', index=False)