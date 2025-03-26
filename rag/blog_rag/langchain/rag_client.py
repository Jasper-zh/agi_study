from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.documents import Document
import requests
import json
from typing import List, Dict

# 配置信息
ELASTICSEARCH_URL = "https://172.17.25.140:9200"
INDEX_NAME = "blog_sections"
USERNAME = "elastic"
PASSWORD = "TKKY6oVXN6CSUOqai6y+"
EMBEDDING_URL = "http://localhost:8000/embed"  # 自定义嵌入模型 API
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


# 自定义嵌入模型（调用外部 API）
class CustomEmbeddings:
    def __init__(self, embedding_url: str):
        self.embedding_url = embedding_url

    def embed_query(self, text: str) -> List[float]:
        """嵌入查询文本"""
        response = requests.post(self.embedding_url, json=[text])
        if response.status_code == 200:
            return response.json()["embeddings"][0]
        else:
            raise Exception(f"Embedding request failed: {response.status_code}, {response.text}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入文档（批量）"""
        response = requests.post(self.embedding_url, json=texts)
        if response.status_code == 200:
            return response.json()["embeddings"]
        else:
            raise Exception(f"Embedding request failed: {response.status_code}, {response.text}")


# 初始化嵌入模型
embeddings = CustomEmbeddings(embedding_url=EMBEDDING_URL)

# 初始化 Elasticsearch 检索器
es = Elasticsearch(ELASTICSEARCH_URL, basic_auth=("elastic", "TKKY6oVXN6CSUOqai6y+"), verify_certs=False)
es_store = ElasticsearchStore(
    index_name=INDEX_NAME,
    embedding=embeddings,
    # ssl_verify=False,  # 禁用 SSL 证书验证
    distance_strategy="COSINE",  # 使用余弦相似度
    vector_query_field="embedding",  # 显式指定向量字段名
    es_connection=es,

)

# 初始化 Ollama 大模型
llm = ChatOllama(
    model="deepseek-r1:7b",
    base_url="http://127.0.0.1:11434",
    temperature=0.0,  # 设置温度为 0，避免生成随机内容
)

# 定义提示词模板
prompt_template = PromptTemplate.from_template(
    """
    你是一个问答助手，你的任务是根据检索到的信息回答用户的问题。
    请严格按照以下要求生成回答：
    1. 仅使用检索到的信息回答问题。
    2. 不要添加任何与问题无关的内容。
    3. 如果检索到的信息不足以回答问题，请直接回答“无法回答”。
    4. 在回答末尾附上参考文档的元信息，记得去重哦。

    检索到的信息：
    {context}

    参考的元信息：
    {references}

    用户查询：
    {query}

    请根据以上信息回答问题：
    """
)


# 定义 RAG 流程
def rag_pipeline(query: str) -> str:
    """
    RAG 流程：检索 + 生成

    Args:
        query (str): 用户查询语句

    Returns:
        str: 生成的回答
    """
    # 检索文档（向量检索）
    documents = es_store.similarity_search(
        query=query,
        k=5,  # 返回前 5 个结果
    )
    print("es_store查询", documents)

    # 提取上下文和元信息
    context = " ".join([doc.page_content for doc in documents])
    references = [doc.metadata for doc in documents]

    # 构建 RAG 链
    rag_chain = RunnableSequence(
        prompt_template | llm
    )

    # 生成回答
    response = rag_chain.invoke({
        "query": query,
        "context": context,
        "references": json.dumps(references, ensure_ascii=False, indent=2),
    })

    return response.content


if __name__ == "__main__":
    # 测试 RAG 流程
    query = "docker安装"

    # ===========================================================================================
    query_vector = embeddings.embed_query(query)
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
    es = Elasticsearch(ELASTICSEARCH_URL, basic_auth=(USERNAME, PASSWORD), verify_certs=False)
    response = es.search(index=INDEX_NAME, body=es_query)
    print("手动查询",response["hits"]["hits"])

    #===========================================================================================

    response = rag_pipeline(query)
    print("Response:", response)