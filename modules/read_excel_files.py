import pandas as pd
import os
import sys
import openpyxl
print(sys.executable)
print(openpyxl.__file__)


# 读取 Excel 文件 只能读老的 xls
# xls xlsx区别前者最多256列
file_path = './output_chinese.xls'

print(os.path.exists(file_path))  # True 表示文件路径正确
# xlrd 读取xls,xlsx读取失败，应该是pandas版本不对 pandas/io/excel.py报错
df = pd.read_excel(file_path,engine='xlrd')

# 初始化一个空列表来存储每行数据
rows_as_lists = []

# 逐行遍历 DataFrame 并将每行转换为列表
for index, row in df.iterrows():
    row_list = row.tolist()  # 将每行转换为列表
    rows_as_lists.append(row_list)

# 打印每行数据列表
for row_list in rows_as_lists:
    print(row_list)