import pandas as pd

# 初始列名
initial_columns = ['Variables', 'Values', 'Description']
df = pd.DataFrame(columns=initial_columns)

# 假设这些是我们要逐行添加的数据列表，行数据长度不定
data = [
    [1, 2, 3],
    [4, 5, 6, 7],
    [8],
    [9, 10, 11, 12, '中文测试aa']
]

# 动态添加数据和列
for row in data:
    # 动态扩展 DataFrame 的列数
    if len(row) > len(df.columns):
        additional_columns = len(row) - len(df.columns)
        new_columns = [f'Column{len(df.columns) + i + 1}' for i in range(additional_columns)]
        df = df.reindex(columns=[*df.columns, *new_columns])

    # 将行数据作为字典，并用空字符串填充没有对应值的列
    row_dict = {df.columns[i]: row[i] if i < len(row) else '' for i in range(len(df.columns))}

    # 追加行到 DataFrame 中
    df = df.append(row_dict, ignore_index=True)

df = df.fillna('')
print(df)
# 指定文件路径，例如保存为当前路径下的 `output.xlsx`
file_path = './output_0602.xlsx'

# 保存到 Excel 文件
df.to_excel(file_path, index=False, engine='openpyxl')

print(f"数据已成功保存到 Excel 文件：{file_path}")

file_path_xls = './output_0602.xls'

# 保存到 Excel 文件
df.to_excel(file_path_xls, index=False, engine='xlwt')

print(f"数据已成功保存到 Excel 文件：{file_path_xls}")

