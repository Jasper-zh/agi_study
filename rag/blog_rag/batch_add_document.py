import os
import glob
import frontmatter
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
import requests
import re


# 连接 Elasticsearch
es = Elasticsearch("https://172.17.25.140:9200/", basic_auth=("elastic", "TKKY6oVXN6CSUOqai6y+"),verify_certs=False)

# 指定文件夹路径
folder_path = "documents"


def get_embedding(arr):
    # 调用 API
    url = "http://localhost:8000/embed"
    data = arr
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["embeddings"]
    else:
        raise Exception(f"请求失败: {response.status_code}, {response.text}")

def parse_metadata(content):
    # 解析元信息
    metadata = frontmatter.loads(content)
    return metadata.metadata, metadata.content

# def split_markdown(content):
#     # 按段落分割文档
#     sections = content.split("\n\n")  # 假设段落之间用空行分隔
#     return [section.strip() for section in sections if section.strip()]

def split_markdown(md_text):
    # 按标题分割（以 # 开头）
    sections = re.split(r'\n#+\s+', md_text)
    # 去掉空字符串
    sections = [section.strip() for section in sections if section.strip()]
    return sections

def process_markdown(file_path, content):
    # 解析元信息
    metadata, content = parse_metadata(content)

    # 分割文档
    sections = split_markdown(content)

    # 词嵌入
    embeddings = get_embedding(sections)

    # 为每个部分生成词嵌入并灌入 Elasticsearch
    index_name = "blog_2"
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "mappings": {
                "properties": {
                    "text": {"type": "text"},
                    "embedding": {"type": "dense_vector", "dims": 384}  # 根据向量维度调整
                }
            }
        })
    for i, section in enumerate(sections):
        # 生成词嵌入
        embedding = embeddings[i]

        # 构建文档
        doc = {
            "text": section,
            "embedding": embedding,
            "metadata": metadata  # 包含元信息
        }

        # 灌入 Elasticsearch
        es.index(index=index_name, id=f"{file_path}_{i}", document=doc)
        print(f"灌入文档：{file_path}_{i}")

if __name__ == "__main__":
    # 获取所有 Markdown 文件
    markdown_files = glob.glob(os.path.join(folder_path, "*.md"))

    # 处理每个文件
    for file_path in markdown_files:
        print("处理文件：", file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        process_markdown(file_path, content)