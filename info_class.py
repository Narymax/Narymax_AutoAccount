import yaml
import csv
import os
import pandas as pd
import openpyxl
import numpy as np
from util import select_file_from_tk
from util import get_current_path
from collections import OrderedDict
from bs4 import BeautifulSoup
from datetime import datetime

# 用户配置类
# 查看测试用例
class InfoClass:
    def __init__(self, user="小明"):
        self.user = user
        self.min_pay_filter = 0.1
        self.default_proj_name = "家庭支出"
        self.character = "M"
        self.use_suggestion_classify = True  # 没有分类规则的使用账单自带的分类标签
        self.redacte_show_string = "****"  # 屏蔽交易号
        self.match_list_rule = []   # 旧版本 ，使用两个yaml
        self.classify_csv_rule = []  # 新版本，使用一个xls  支出分类规则
        self.income_classify_csv_rule = []  # 新版本，使用一个xls  收入分类规则 默认捕捉关键字退款，把一级分类、二级分类都变成 退款 ['收入分类规则','退款','退款','退款']
        self.transfer_classify_csv_rule = []  # 新版本，使用一个xls  转账分类规则

    def load_config_file_from_tk_window(self):
        file_path = select_file_from_tk(file_extension = '.xls',show_title = '请选择配置文件 xls类型')
        self.load_config_file(file_path)

    def load_config_file(self,xls_path):

        print(os.path.exists(xls_path))  # True 表示文件路径正确

        # xlrd 读取xls,xlsx读取失败，应该是pandas版本不对 pandas/io/excel.py报错
        df = pd.read_excel(xls_path, engine='xlrd')
        # 初始化一个空列表来存储每行数据
        rows_as_lists = []
        # 逐行遍历 DataFrame 并将每行转换为列表
        for index, row in df.iterrows():
            row_list = row.tolist()  # 将每行转换为列表
            rows_as_lists.append(row_list)
        self.classify_csv_rule = []
        flag_configfile_exist_calssify_rule = False
        flag_income_configfile_exist_calssify_rule = False
        flag_transfer_configfile_exist_calssify_rule = False
        for row in rows_as_lists:
            parameter = row[0]
            value = row[1]
            description = row[2]
            # print(parameter, value, description)
            # 打印每行
            print([row_item for row_item in row if row_item not in [np.nan,'']])

            if 'user' in str(parameter):
                self.user = str(value)
            if 'character' in str(parameter):
                self.character = str(value)
            if 'min_pay_filter' in str(parameter):
                self.min_pay_filter = float(value)
            if 'use_suggertion_classify' in str(parameter):
                self.use_suggertion_classify = bool(value)
            if 'default_proj_name' in str(parameter):
                self.default_proj_name = str(value)
            if 'redacte_show_string' in str(parameter):
                self.redacte_show_string = str(value)
            if '支出分类规则' in str(parameter):
                if str(value) != '':
                    flag_configfile_exist_calssify_rule = True
                    self.classify_csv_rule.append(row)
            if '收入分类规则' in str(parameter):
                if str(value) != '':
                    flag_income_configfile_exist_calssify_rule = True
                    self.income_classify_csv_rule.append(row)
            if '转账分类规则' in str(parameter):
                if str(value) != '':
                    flag_transfer_configfile_exist_calssify_rule = True
                    self.transfer_classify_csv_rule.append(row)

        if not flag_configfile_exist_calssify_rule:
            # 如果配置文件中没有分类规则，那么就用默认的空列表
            self.classify_csv_rule = []
        if not flag_income_configfile_exist_calssify_rule:
            self.income_classify_csv_rule = []
        if not flag_transfer_configfile_exist_calssify_rule:
            self.transfer_classify_csv_rule = []


    def get_user_info_from_yaml(self, yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            cfg_str = f.read()
            cfg = yaml.load(cfg_str, Loader=yaml.SafeLoader)
            # 使用get 防止没有定义
            self.user = cfg.get('user', self.user)
            self.min_pay_filter = cfg.get('min_pay_filter', self.min_pay_filter)
            self.default_proj_name = cfg.get('default_proj_name', self.default_proj_name)
            self.character = cfg.get('character', self.character)

    def get_user_info_from_tk(self):
        yamlpath = select_file_from_tk('.yaml', '请选择用户配置文件')
        if yamlpath == '':
            return False
        else:
            self.get_user_info_from_yaml(yamlpath)
            return True

    # 导出自动分类模板 (模板生成'auto_classify_config_tample.yaml')
    def create_auto_classify_template(self):
        with open('auto_classify_config_tample.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(self.match_list_rule, file, allow_unicode=True)


    def create_csv_config_file(self):
        data = [
            # ["Variables", "Values", "Description"],
            ["user", self.user, "记账人"],
            ["character", self.character, "记账人代号，随便取一个字母"],
            ["min_pay_filter", self.min_pay_filter, "最小筛选金额"],
            ["use_suggesstion_classify", self.use_suggestion_classify, "使用原始账单默认的分类"],
            ["default_proj_name", self.default_proj_name, "默认支出的项目名称"],
            ["redacte_show_string", self.redacte_show_string, "屏蔽交易号码，显示字符，连续数字大于9个"],
            [""]
        ]
        if self.classify_csv_rule != []:
            data.append(['', '第一级分类名称', '第二级分类名称', '支出关键字','...','...'])
            for row in self.classify_csv_rule:
                data.append(row)

        if self.income_classify_csv_rule != []:
            data.append(['', '第一级分类名称', '第二级分类名称', '收入关键字','...','...'])
            for row in self.income_classify_csv_rule:
                data.append(row)

        if self.transfer_classify_csv_rule != []:
            data.append(['', '第一级分类名称', '第二级分类名称', '转账关键字','...','...'])
            for row in self.transfer_classify_csv_rule:
                data.append(row)

        # 初始列名
        initial_columns = ['Variables', 'Values', 'Description']
        df = pd.DataFrame(columns=initial_columns)

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

        current_path = get_current_path()

        file_name = datetime.now().strftime('%Y-%m-%d %H_%M_%S ')+"config.xls"

        # 先判断路径是否存在，如果不存在就创建
        path = current_path + "/config"
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Path '{path}' created successfully.")
        else:
            print(f"Path '{path}' already exists.")

        # 创建xls文件
        # 保存到 Excel 文件
        xls_file_path = current_path + "/config/" + file_name
        df.to_excel(xls_file_path, index=False, engine='xlwt')

        print(f"数据已成功保存到 Excel 文件：{xls_file_path}")



    def get_match_list_from_tk(self):
        htmlpath = select_file_from_tk('.html',
                '请选择随手记支出分类.html (https://www.sui.com/category/budgetCategory.do)')
        if htmlpath != '':
            self.get_match_list_from_htmlpath(htmlpath)
            return True
        else:
            print("打开失败")
            return False


    def get_classify_name_from_html(self,account_app_name):
        if account_app_name == '随手记':
            flag = self.get_match_list_from_tk()
            if flag:
                return True
            else:
                return False



    def get_match_list_from_htmlpath(self, html_file_path):
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_doc = f.read()

        soup = BeautifulSoup(html_doc, 'html.parser')
        li_tags = soup.find_all('li', {'class': 'li-level1'})

        for tag in li_tags:
            # print(tag)
            if 'title' in tag.attrs and tag.find('span'):
                print("一级分类：", tag['title'])
            # 通过span 判断是否是一级标签
            if 'title' in tag.attrs and tag.find('span') is None:
                print("     二级分类：", tag['title'])

        my_dict = OrderedDict()
        key_temp = ''

        for tag in li_tags:
            # print(tag)
            if 'title' in tag.attrs and tag.find('span'):
                print("一级分类：", tag['title'])
                key_temp = tag['title']
                my_dict[key_temp] = []
            # 通过span 判断是否是一级标签
            if 'title' in tag.attrs and tag.find('span') is None:
                print("     二级分类：", tag['title'])
                if key_temp != '':
                    my_dict[key_temp].append(tag['title'])
                else:
                    print('一级分类 is empty')

        # 适配yaml
        # 生成自动分类模板
        # [
        #     ['一级分类', '二级分类', ['备注',......待手动添加关键字]],
        #     ['一级分类', '二级分类', ['备注',......待手动添加关键字]],
        #     ['一级分类', '二级分类', ['备注',......待手动添加关键字]],
        #     ....
        # ]
        # 第一层
        list_of_matches = []
        for key, value in my_dict.items():
            for secondClass in value:
                # 第二层
                tempt_list_sec = []
                tempt_list_sec.append(key)
                tempt_list_sec.append(secondClass)
                # 第三层
                tempt_list_third_0 = []
                tempt_list_sec.append(tempt_list_third_0)
                tempt_list_third_0.append('备注')

                list_of_matches.append(tempt_list_sec)

        self.match_list_rule = list_of_matches

        # 适配csv
        # [
        #     ['支出分类规则','一级分类','二级分类'],
        #     ['支出分类规则','一级分类','二级分类'],
        #     ['支出分类规则','一级分类','二级分类'],
        # ]
        list_csv_list = []
        for firstClass, value in my_dict.items():
            for secondClass in value:
                # 第二层
                tempt_list_sec = []
                tempt_list_sec.append('支出分类规则')
                tempt_list_sec.append(firstClass)
                tempt_list_sec.append(secondClass)

                list_csv_list.append(tempt_list_sec)
        self.classify_csv_rule = list_csv_list


    def get_match_template_from_tk(self):
        yaml_path = select_file_from_tk('.yaml',
                '请选择分类模板： auto_classify_config_tample.yaml')
        if yaml_path == '':
            print("打开自动分类模板失败")
            return False
        else:
            self.get_match_template_from_yaml(yaml_path)
            return True


    def get_match_template_from_yaml(self, yaml_path):
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                cfg_str = f.read()
                match_list = yaml.load(cfg_str, Loader=yaml.SafeLoader)
        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
            return  # 退出当前函数
        except Exception as e:
            print(f"Error: {e}")
            return  # 退出当前函数

        if match_list is None:
            print('没有找到匹配模板')
        else:
            self.match_list_rule = match_list




    def greet(self):
        print(f"Hello, {self.user}!")


if __name__ == '__main__':
    my_obj = InfoClass("㗊")
    print(my_obj.user)

    #  打开config.yaml
    my_obj.get_user_info_from_tk()

    # 打开 网页.html，分析二级分类
    my_obj.get_match_list_from_tk()
    # 保存 模板.yaml
    my_obj.create_auto_classify_template()

    # 打开 分类模板.yaml
    my_obj.get_match_template_from_tk()
