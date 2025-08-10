import json

import requests
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch

# Elasticsearch 配置
ELASTICSEARCH_URL = "https://172.17.25.140:9200"
INDEX_NAME = "blog_sections"
USERNAME = "elastic"  # 替换为你的用户名
PASSWORD = "TKKY6oVXN6CSUOqai6y+"  # 替换为你的密码
# Ollama 配置
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
EMBEDDING_URL = "http://localhost:8000/embed"

def retrieve_documents(query):
    """
    ES关键字检索

    param: 查询语句
    """

    # 从 Elasticsearch 检索文档
    search_url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_search"
    search_query = {
        "query": {
            "match": {
                "text": query
            }
        },
        "from": 0,
        "size": 20
    }
    response = requests.get(search_url, json=search_query, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    if response.status_code == 200:
        print("查询结果：",response.json()["hits"]["hits"][:3])
        return response.json()["hits"]["hits"][:3]
    else:
        raise Exception(f"Elasticsearch search failed: {response.text}")


def retrieve_documents_vector(query):
    """
    ES向量检索

    param：查询语句
    """

    # 查询向量
    # query_vector = [0.1] * 384  # 示例查询向量（384 维#）
    query_vector = get_embedding(query)
    print("向量查询", query_vector)

    # 构建查询
    es_query = {
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }
    }

    # 执行查询
    es = Elasticsearch(ELASTICSEARCH_URL, basic_auth=(USERNAME, PASSWORD),verify_certs=False)
    response = es.search(index=INDEX_NAME, body=es_query)

    # 复制并去掉 embedding 字段
    hits = response["hits"]["hits"][:5]
    cleaned_hits = []
    for hit in hits:
        cleaned_hit = hit.copy()  # 复制原始 hit
        cleaned_hit['_source'] = cleaned_hit['_source'].copy()  # 复制 _source
        cleaned_hit['_source'].pop('embedding', None)  # 删除 embedding 字段
        cleaned_hits.append(cleaned_hit)
    print("向量查询结果：", cleaned_hits)
    return cleaned_hits

def get_embedding(query):
    """
    调用词嵌入模型

    param：查询语句
    """

    # 调用 API
    url = EMBEDDING_URL
    data = [query]
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["embeddings"][0]
    else:
        raise Exception(f"请求失败: {response.status_code}, {response.text}")


def generate_response(query, context, reference):
    """
    获取大模型响应

    param1: 查询语句
    param2: ES检索内容
    param3: ES检索内容元信息
    """

    # 使用 Ollama 生成回答 默认是流式
    prompt = f"""
    你是一个问答助手，你的任务是根据检索到的信息回答用户的问题。
    请严格按照以下要求生成回答：
    1. 仅使用检索到的信息回答问题。
    2. 不要添加任何与问题无关的内容。
    3. 如果检索到的信息不足以回答问题，请直接回答“无法回答”。
    4. 在回答末尾附上参考文档的元信息，记得去重哦。

    检索到的信息：
    {context}
    
    参考的元信息：
    {reference}

    用户查询：
    {query}

    请根据以上信息回答问题：
    """
    generate_data = {
        "model": "deepseek-r1:7b",
        "prompt":  prompt
    }
    print("提示词：", generate_data)
    # response = requests.post(OLLAMA_URL, json=generate_data)
    #
    # if response.status_code == 200:
    #     print(response.text)
    #     return response.json()["response"]
    # else:
    #     raise Exception(f"Ollama generation failed: {response.text}")
    try:
        response = requests.post(OLLAMA_URL, json=generate_data, stream=True)
        response.raise_for_status()  # 如果状态码不是 200，抛出异常

        full_response = ""
        for line in response.iter_lines():
            if line:
                # 解析每行的 JSON
                chunk = json.loads(line.decode("utf-8"))
                if "response" in chunk:
                    full_response += chunk["response"]
                if chunk.get("done", False):
                    break  # 如果生成完成，退出循环

        return full_response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON: {e}, raw response: {line}")

def rag_pipeline(query):
    """
    RAG流程：检索 + 生成

    param: 查询语句
    """

    # 检索文档
    documents = retrieve_documents_vector(query)
    context = " ".join([doc["_source"]["text"] for doc in documents])
    references = [doc["_source"]["metadata"] for doc in documents]  # 提取元信息

    # 生成回答
    response = generate_response(query, context, references)
    return response

if __name__ == "__main__":
    # 测试 RAG 流程
    query = "docker安装"
    # retrieve_documents(query)
    response = rag_pipeline(query)
    print("Response:", response)