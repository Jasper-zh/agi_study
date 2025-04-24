from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # 加载.env进环境变量

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# 创建Chroma客户端
# chroma_client = chromadb.Client()

# 创建持久化的Chroma客户端
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.create_collection("my_collection")

# 创建向量存储
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 加载文档
documents = SimpleDirectoryReader("./data").load_data()

# 使用自定义向量存储创建索引
index = VectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store
)