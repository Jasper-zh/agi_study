import torch
from typing import Any
from pydantic import Field
from llama_index.core.embeddings import BaseEmbedding
from FlagEmbedding import FlagModel
from config.config import EMBEDDING_MODEL

class BGEEmbeddings(BaseEmbedding):
    model: Any = Field(default=None, description="BGE model instance")
    
    def __init__(self, model: Any, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        
    def _get_query_embedding(self, query: str) -> list[float]:
        return self.model.encode([query])[0].tolist()
        
    def _get_text_embedding(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()
        
    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)
        
    async def _aget_text_embedding(self, text: str) -> list[float]:
        return self._get_text_embedding(text)

def get_embedding_model():
    """初始化并返回 BGE 嵌入模型"""
    print("正在加载 BGE 模型...")
    model = FlagModel(
        EMBEDDING_MODEL,
        use_fp16=True,  # 使用半精度浮点数加速
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    print("BGE 模型加载完成！")
    return BGEEmbeddings(model=model) 