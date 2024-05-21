import pandas as pd


def match_phone_number():
        # 匹配手机号
        # 创建示例数据
        data = {'ID': [1, 2, 3, 4,5],
                'column_name': ['abc123456789def', '12345678900', 'xyz456789', '123456789012','15995705685']}
        df = pd.DataFrame(data)

        # 使用正则表达式筛选出含有连续11位数字的行
        pattern = r'^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}$'  # 匹配连续11位数字
        mask = df['column_name'].str.contains(pattern, regex=True)
        filtered_rows = df[mask]

        # 输出结果
        print(filtered_rows)

def delete_much_than_9_nums():
        # 创建示例数据
        data = {'ID': [1, 2, 3, 4],
                'column_name': ['abc123456789def', '12345678900', 'xyz456789', '123456789012']}
        df = pd.DataFrame(data)

        # 删除连续出现9位及以上数字的行
        pattern = r'\d{9,}'  # 匹配连续出现9位及以上数字
        df['column_name'] = df['column_name'].str.replace(pattern, '')  # 将匹配到的数字替换为空字符串
        filtered_rows = df[df['column_name'].str.len() > 0]  # 筛选出替换后不为空的行

        # 输出结果
        print(filtered_rows)

#  提取包含手机的mask
def extract_phone(df,column_name):

        pattern_middle = r'\D1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}\D'  # 匹配中间连续11位数字  aa1731234567bb
        mask_middle = df[column_name].str.contains(pattern_middle, regex=True)
        pattern_begin = r'^1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}\D'  # 匹配从头开始连续11位数字 1731234567aa
        mask_begin = df[column_name].str.contains(pattern_begin, regex=True)
        pattern_end = r'\D1(3[0-9]|5[0-3,5-9]|7[1-3,5-8]|8[0-9])\d{8}$'  # 匹配连续11位数字然后结束  aabb1731234567
        mask_end = df[column_name].str.contains(pattern_end, regex=True)
        mask = mask_middle | mask_begin | mask_end
        print("phone number extracted\n")
        print(df[mask])
        return mask

def replace_continue_number(df,colum_name,num=9,replace_char=''):
        pattern = r'(\d{{{0},}})'.format(num)   # 匹配连续出现num位及以上数字
        # 提取连续出现num位及以上数字的行
        matches = df[colum_name].str.extractall(pattern)
        print(matches)  # 打印匹配的结果

        df[colum_name] = df[colum_name].str.replace(pattern, replace_char)
        print("消除连续出现",num,"位及以上的数字，并且替换成\" ",replace_char,"\"\n")
        return df



# 屏蔽交易号 （默认不屏蔽手机号）
# 交易号判定，连续数字大于9个,(含有手机号的需要超过11个)
def redacte_key_number(df,colum_name,dedacte_phone_number=False,redacte_trade_number=True,redacte_show_char=''):
        # 含有手机号码的匹配行
        mask = extract_phone(df,colum_name)
        df[mask] = replace_continue_number(df[mask],colum_name,num=12,replace_char=redacte_show_char)

        # 不含有手机号码的行
        df[~mask] = replace_continue_number(df[~mask],colum_name,replace_char=redacte_show_char)
        return df




if __name__ == '__main__':


        data = {'ID': [1, 2, 3, 4,5,6,7],
                'column_name': ['abc123456789def', '12345678900', 'xyz456789', '123456789012','15995705685#154546464875643434','er15995700000sd','01234567']}
        df = pd.DataFrame(data)
        df = redacte_key_number(df,'column_name',redacte_show_char="****")
        print(df)
        print("test")
