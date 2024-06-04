import pandas as pd
# from helper import init_df_columns
import os
import sys
# 将父目录加入 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from info_class import InfoClass
from util import get_current_path
import os.path as op
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

def jindong_bill_conv(df,info_data):

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

    # 筛选还京东白条  不计收支 -> 转账 （类似还信用卡）
    condition_jindongcrediet = (df['交易类型'] == '不计收支') & (df['交易说明'] == '白条主动还款') & (df['商户名称'] == '京东金融')
    df.loc[condition_jindongcrediet, '交易类型'] = "转账"
    df.loc[condition_jindongcrediet, '账户'] = df.loc[condition_jindongcrediet, '账户'] + "还白条"
    df.loc[condition_jindongcrediet, '*账户'] = "京东白条"

    condition_cashout = (df['交易类型'] == '不计收支') & (df['账户'].str.contains('代付')) & (df['交易说明'] == '京东钱包余额提现')
    df.loc[condition_cashout, '交易类型'] = '转账'
    df.loc[condition_cashout, '账户'] = '京东钱包余额'
    df.loc[condition_cashout,'*账户'] = '京东提现账户'

    # 一步完成列名修改、增加新列和重新排序
    df = (
        df.rename(columns={"一级分类名称":"分类","二级分类名称":"子分类","账户": "账户1","*账户": "账户2"})
        .reindex(columns=['交易类型', '日期', '分类', '子分类', '账户1', '账户2', '金额', '成员', '商家', '项目', '备注'])
    )





    return df




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
    with pd.ExcelWriter(op.join(get_current_path(), '随手记导入京东账单.xls')) as writer:
        # 不保存序号
        df.to_excel(writer, sheet_name='Sheet1', index=False)



