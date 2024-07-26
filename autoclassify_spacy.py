import os
import spacy
import pandas as pd
from spacy.util import get_package_path

# chars_to_remove = '开票号'
list_char_to_remove = ['开票号','转账备注']

def clean_string(s, chars_to_remove):
    # 将列表中的字符合并成一个字符串
    chars_to_remove_str = ''.join(chars_to_remove)

    # 创建一个删除指定字符的翻译表
    translation_table = str.maketrans('', '', chars_to_remove_str)

    # 删除指定字符
    cleaned_string = s.translate(translation_table)

    # 删除所有数字
    cleaned_string = ''.join(c for c in cleaned_string if not c.isdigit())

    return cleaned_string

# 获取模型路径
# model_path = get_package_path("zh_core_web_md")

model_path = os.path.join(os.path.dirname(__file__), 'zh_core_web_md')
print(f"Model path: {model_path}")
model_path = "D:\\Roots\\2024-01-29pay_list_csv_import\\dist\\zh_core_web_md\\zh_core_web_md-3.7.0"
print(f"Model path: {model_path}")


# 加载spaCy的中文模型
nlp = spacy.load(model_path)



# 定义文本和分类
# texts = ["西安5号凉皮店凉皮", "滴滴快车-高师傅-03月13日行程#滴滴出行", "为70**********1881加油卡进行充值#中国石油昆仑加油卡网上服务平台"]
# categories = ['餐饮', '交通', '旅游', '娱乐', '话费', '医疗保健']
texts_path = 'D:\\Roots\\2024-01-29pay_list_csv_import\\res\\demoBillList.txt'
cateGories_path ='D:\\Roots\\2024-01-29pay_list_csv_import\\res\\democategories.txt'
texts = []
categories = []

with open(texts_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = clean_string(line, list_char_to_remove)
        texts.append(line.strip())

with open(cateGories_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = clean_string(line, list_char_to_remove)
        categories.append(line.strip())

# 计算文本和分类的相似度
similarity_data = []
for text in texts:
    text_doc = nlp(text)
    similarities = [text_doc.similarity(nlp(category)) for category in categories]
    max_similarity = max(similarities)
    most_similar_category = categories[similarities.index(max_similarity)]
    similarity_data.append(similarities + [most_similar_category, max_similarity])

# 创建 DataFrame
columns = categories + ["最相似的分类", "最高相似度"]
df = pd.DataFrame(similarity_data, columns=columns, index=texts)

# 打印表格
print(df)
