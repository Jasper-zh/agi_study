"""
rag_llm_example03 - 搜索结果汇入大模型

Author: zhang
Date: 2024/2/22
"""

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from elasticsearch8 import Elasticsearch
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re


# 加载当前目录下的.env到系统环境
_ = load_dotenv(find_dotenv())
# 配置 OpenAI 服务 （从系统环境读取）
client = OpenAI()

prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。

已知信息:
__INFO__

用户问：
__QUERY__

请用中文回答用户问题。
"""

es = Elasticsearch(
    hosts=['http://127.0.0.1:9900'],  # 服务地址与端口
    # http_auth=("elastic", "password"),  # 用户名，密码
)
# 2. 定义索引名称
index_name = "index_agi_study"


def build_prompt(prompt_template, user_input, known_info):
    '''将 Prompt 模板赋值'''
    prompt = prompt_template
    prompt = prompt.replace("__INFO__", known_info)
    prompt = prompt.replace("__QUERY__", user_input)
    return prompt

def get_completion(prompt, model="gpt-3.5-turbo"):
    '''封装 openai 接口'''
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

# 从es搜索数据
def search(query_string, top_n=3):
    # ES 的查询语言
    search_query = {
        "match": {
            "keywords": to_keywords(query_string)
        }
    }
    res = es.search(index=index_name, query=search_query, size=top_n)
    return [hit["_source"]["text"] for hit in res["hits"]["hits"]]

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
    user_input = 'sora是啥时候发布的呀'
    # hits = search('When was Sora released')
    hits = search('sora')
    # 用户问题结合检索结果构成提示词
    prompt = build_prompt(prompt_template, user_input, str(hits))
    print("提示词："+prompt)
    res = get_completion(prompt)
    print("GPT-3.5回复：\n" + res)
