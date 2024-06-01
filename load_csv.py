import csv
import util

current_path = util.get_current_path()
compare_config_path = '/config/config_test.csv'
f= open(current_path + compare_config_path,'r',encoding='utf-8-sig')
with f:
    reader = csv.reader(f,delimiter=',')
    user = '快乐小猴'
    character = 'M'
    min_pay_filter = 0.1
    use_suggertion_classify = True
    default_proj_name = '家庭支出'
    redacte_show_string = '****'
    classify_rule = []

    for row in reader:
        parameter = row[0]
        value = row[1]
        description = row[2]
        print(parameter,value,description)

        if 'user' in str(parameter):
            user = str(value)
        if 'character' in str(parameter):
            character = str(value)
        if 'min_pay_filter' in str(parameter):
            min_pay_filter = float(value)
        if 'use_suggertion_classify' in str(parameter):
            use_suggertion_classify = bool(value)
        if 'default_proj_name' in str(parameter):
            default_proj_name = str(value)
        if 'redacte_show_string' in str(parameter):
            redacte_show_string = str(value)
        if '分类规则' in str(parameter):
            if str(value) != '':
                classify_rule.append(row)

