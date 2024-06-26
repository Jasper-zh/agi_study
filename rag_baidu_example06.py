"""
rag_baidu_example06 -

Author: zhang
Date: 2024/3/6
"""
import json
import requests
import os
import re
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())



# 通过鉴权接口获取 access token
def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": os.getenv('ERNIE_CLIENT_ID'),
        "client_secret": os.getenv('ERNIE_CLIENT_SECRET')
    }
    res = requests.post(url, params=params)
    match = re.search(r'"access_token":"(.*?)"', res.text)
    return match.group(1)


# 调用文心千帆 调用 BGE Embedding 接口
def get_embeddings_bge(prompts):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/bge_large_en?access_token=" + get_access_token()
    payload = json.dumps({
        "input": prompts
    })
    print(payload)
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=payload).json()
    data = response['data']
    return [x["embedding"] for x in data]


# 调用文心4.0对话接口
def get_completion_ernie(prompt):

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + get_access_token()
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    headers = {'Content-Type': 'application/json'}

    response = requests.request(
        "POST", url, headers=headers, data=payload).json()

    return response["result"]


if __name__ == '__main__':
    res = get_embeddings_bge(["苹果多少钱"])
    print(res)