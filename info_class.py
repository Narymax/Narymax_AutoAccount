import yaml
from util import select_file_from_tk
from collections import OrderedDict
from bs4 import BeautifulSoup

# 用户配置类
# 查看测试用例
class InfoClass:
    def __init__(self, user="小明"):
        self.user = user
        self.min_pay_filter = 0.1
        self.default_proj_name = "家庭支出"
        self.character = "M"
        self.match_list_rule = []


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

    def get_match_list_from_tk(self):
        htmlpath = select_file_from_tk('.html',
                '请选择随手记支出分类.html (https://www.sui.com/category/budgetCategory.do)')
        if htmlpath != '':
            self.get_match_list_from_htmlpath(htmlpath)
            return True
        else:
            print("打开失败")
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
