from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import numpy as np

import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
print(os.environ.get('HF_ENDPOINT'))

# 加载词嵌入模型
# model = SentenceTransformer('all-MiniLM-L6-v2')

model_path = r'G:\LLM\models\all-MiniLM-L6-v2'
if os.path.exists(model_path):
    print("路径存在")
else:
    print("路径不存在，请检查路径")
model = SentenceTransformer(model_path)

# 创建 FastAPI 应用
app = FastAPI()

# 定义 API 接口
@app.post("/embed")
def embed(texts: list[str]):
    print("参数：")
    print(texts)
    # 将文本转换为向量
    embeddings = model.encode(texts)
    # 将向量转换为列表（FastAPI 不支持直接返回 numpy 数组）
    embeddings = [embedding.tolist() for embedding in embeddings]
    return {"embeddings": embeddings}

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)