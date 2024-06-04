
# def init_df_columns(df, skiprows=0, use_column_name = True):
#     df = df.iloc[skiprows+1:]
#     first_row = df.iloc[0]
#     # 将第一行转换成字符串
#     new_column_names = [str(item) if item != "" else df.columns[idx] for idx, item in enumerate(first_row)]
#     # 设置新的列名
#     df.columns = new_column_names
#     print("导入原始账单")
#     print(new_column_names)
#     # 删除第一行，因为它已经被用作列名
#     df = df.drop(df.index[0])
#     # 重置索引
#     df.reset_index(drop=True, inplace=True)
#
#     return df


