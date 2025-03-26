from elasticsearch import Elasticsearch
import requests
import re


# 分割markdown
def split_markdown(md_text):
    # 按标题分割（以 # 开头）
    sections = re.split(r'\n#+\s+', md_text)
    # 去掉空字符串
    sections = [section.strip() for section in sections if section.strip()]
    return sections

# 多内容转vector_list
def get_embedding(arr):
    # 调用 API
    url = "http://localhost:8000/embed"
    data = arr
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["embeddings"]
    else:
        raise Exception(f"请求失败: {response.status_code}, {response.text}")

# 3. 灌入 Elasticsearch
def index_to_es(index_name, sections, vectors):
    es = Elasticsearch("https://172.17.25.140:9200/", basic_auth=("elastic", "TKKY6oVXN6CSUOqai6y+"),verify_certs=False)

    for i, (section, vector) in enumerate(zip(sections, vectors)):
        doc = {
            "text": section,
            "embedding": vector
        }
        es.index(index=index_name, id=i, document=doc)
    print("数据灌入完成！")

if __name__ == "__main__":
    # 读取 Markdown 文件
    with open('documents/example.md', 'r', encoding='utf-8') as file:
        md_text = file.read()

    # 分割 Markdown
    sections = split_markdown(md_text)
    for i, section in enumerate(sections):
        print(f"Section {i + 1}:\n{section}\n")

    # 转向量
    vector = get_embedding(sections)
    print(vector)

    # 灌入ES
    index_name = "blog"
    index_to_es(index_name,sections,vector)
