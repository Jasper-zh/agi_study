import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 数据目录
DATA_DIR = ROOT_DIR / "data"
KNOWLEDGE_BASE_PATH = DATA_DIR / "knowledge_base.csv"
QUESTIONS_PATH = DATA_DIR / "questions.txt"
OUTPUT_PATH = DATA_DIR / "output_annotations.jsonl"

# 模型目录
MODELS_DIR = ROOT_DIR / "models"
VECTOR_STORE_PATH = MODELS_DIR / "vector_store"
###
# 坑：
# FaissVectorStore操作文件可能和别的操作不大一样，
# 会出现文件权限不足，但有权限且其他代码操作相同目录是正常
# 推测应该是路径中某些字符有些不能识别
# 由于大部分操作以及其他库都能操作所以不会往路径上去排查
###
VECTOR_STORE_PATH01 = "models/vector_store" 

# 模型配置
EMBEDDING_MODEL = "BAAI/bge-m3"
LLM_MODEL = "gpt-3.5-turbo"

# 检索配置
SIMILARITY_TOP_K = 3
VECTOR_DIMENSION = 1024  # BGE-m3 的向量维度

# 环境变量
os.environ["HF_HOME"] = str(MODELS_DIR / "huggingface") 