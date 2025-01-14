"""
rag_vector_example04 -

Author: zhang
Date: 2024/3/6
"""
import numpy as np
from numpy import dot
from numpy.linalg import norm
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())
# 配置 OpenAI 服务 （从系统环境读取）
client = OpenAI()

def cos_sim(a, b):
    '''余弦距离 -- 越大越相似'''
    return dot(a, b)/(norm(a)*norm(b))


def l2(a, b):
    '''欧式距离 -- 越小越相似'''
    x = np.asarray(a)-np.asarray(b)
    return norm(x)

def get_embeddings(texts, model="text-embedding-ada-002"):
    '''封装 OpenAI 的 Embedding 模型接口'''
    data = client.embeddings.create(input=texts, model=model).data
    return [x.embedding for x in data]

if __name__ == '__main__':
    test_query = ["这个苹果多少钱", "这有好多苹果", "这个苹果需要洗下", "How much is the apple"]
    vec = get_embeddings("苹果价格多少")[0]
    print("余弦距离：")
    for text in test_query:
        vector = get_embeddings(text)[0]
        res = cos_sim(vec,vector)
        print(res)
    print("欧几里得距离：")
    for text in test_query:
        vector = get_embeddings(text)[0]
        res = l2(vec, vector)
        print(res)
