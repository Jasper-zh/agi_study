"""
rag_example02 -

Author: zhang
Date: 2024/2/2
"""
from elasticsearch7 import Elasticsearch, helpers
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import re
import warnings
warnings.simplefilter("ignore")  # 屏蔽 ES 的一些Warnings

nltk.download('punkt')  # 下载用于英文分词、词根提取、句子切分等的数据
nltk.download('stopwords')  # 下载英文停用词库


def to_keywords(input_string):
    '''（英文）文本只保留关键字'''
    # 使用正则表达式替换所有非字母数字的字符为空格
    no_symbols = re.sub(r'[^a-zA-Z0-9\s]', ' ', input_string)
    word_tokens = word_tokenize(no_symbols)
    # 加载停用词表
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    # 去停用词，取词根
    filtered_sentence = [ps.stem(w) for w in word_tokens if not w.lower() in stop_words]
    return ' '.join(filtered_sentence)

if __name__ == '__main__':
    a = to_keywords("hello world! How are you?")
    print(a)