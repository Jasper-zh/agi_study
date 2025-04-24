import json

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # 加载.env进环境变量


from llama_index.core import VectorStoreIndex, SimpleDirectoryReader



documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# query_engine = index.as_query_engine()
#
# response = query_engine.query("出行意外包括哪些")
# print(response)

query_engine = index.as_query_engine(
    similarity_top_k=5,
    vector_store_query_mode="mmr",  # 使用最大边际相关性(MMR)而不是简单相似度
    mmr_diversity_bias=0.3,  # MMR多样性参数(0-1之间)
    response_mode="no_text",  # 这会返回原始检索节点
)
response = query_engine.query("出行意外包括哪些")
print(json.dumps(response))
for node in response.source_nodes:
    print(f"Score: {node.score} \n Text: {node.node.get_text()[:500]}...\n")
