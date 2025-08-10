"""
rag_example02 - 文本内容处理&填入ES

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

# nltk.download('punkt')  # 下载用于英文分词、词根提取、句子切分等的数据
# nltk.download('stopwords')  # 下载英文停用词库

es = Elasticsearch(
    hosts=['http://117.50.198.53:9200'],  # 服务地址与端口
    http_auth=("elastic", "FKaB1Jpz0Rlw0l6G"),  # 用户名，密码
)
# 2. 定义索引名称
#index_name = "teacher_demo_index123"
index_name = "xuc_index_tmp"

# 文本处理分词过滤
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

# 添加数据
def putEs():

    # 3. 如果索引已存在，删除它（仅供演示，实际应用时不需要这步）
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

    # 4. 创建索引
    es.indices.create(index=index_name)

    # 5. 灌库指令
    actions = [
        {
            "_index": index_name,
            "_source": {
                "keywords": to_keywords(para),
                "text": para
            }
        }
        for para in paragraphs
    ]

    # 6. 文本灌库
    helpers.bulk(es, actions)

# 搜索数据
def search(query_string, top_n=3):
    # ES 的查询语言
    search_query = {
        "match": {
            "text": to_keywords(query_string)
        }
    }
    res = es.search(index="xuc_index_t2", query=search_query, size=top_n)
    return [hit["_source"]["text"] for hit in res["hits"]["hits"]]

if __name__ == '__main__':
    #results = search("how many parameters does llama 2 have?", 2)
    results = search("hello", 2)
    for r in results:
        print(r + "\n")
