import csv
import util
import os
# 二维列表数据
data = [
    ["Variables", "Values", "Description"],
    ["user", "快乐小猴", "记账人"],
    ["character", "M", "记账人代号，随便取一个字母"],
    ["min_pay_filter", "0.1", "最小筛选金额"],
    ["use_suggesstion_classify", "TRUE", "使用原始账单默认的分类"],
    ["default_proj_name", "家庭支出", "默认支出的项目名称"],
    ["redacte_show_string", "****", "屏蔽交易号码，显示字符，连续数字大于9个"]
]

current_path = util.get_current_path()
file_name = "config_test.csv"

# 先判断路径是否存在，如果不存在就创建
path = current_path + "/config"
if not os.path.exists(path):
    os.makedirs(path)
    print(f"Path '{path}' created successfully.")
else:
    print(f"Path '{path}' already exists.")

# 创建CSV文件
with open(current_path + "/config/" + file_name, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    for row in data:
        writer.writerow(row)

# 创建CSV文件 解决乱码问题
# 这个编码除了使用UTF-8编码外，还会在文件开头添加一个BOM（Byte Order Mark）标识，这有助于Excel正确地解析文件并避免乱码问题。
with open(current_path + "/config/" + 'config_test1.csv', mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    for row in data:
        writer.writerow(row)

print("CSV文件已创建并数据已写入成功：", current_path + "/config/" + file_name)

