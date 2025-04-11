from typing import Any, List
from pydantic import Field
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document as LangchainDocument
from config.config import SIMILARITY_TOP_K

class LlamaIndexRetriever(BaseRetriever):
    index_retriever: Any = Field(default=None, description="LlamaIndex retriever instance")
    
    def __init__(self, index_retriever: Any, **kwargs):
        super().__init__(**kwargs)
        self.index_retriever = index_retriever
        
    def _get_relevant_documents(self, query: str) -> List[LangchainDocument]:
        # 打印查询时的维度
        print(f"查询时的维度: {self.index_retriever._vector_store._faiss_index.d}")
        print(f"查询向量: {self.index_retriever._vector_store._faiss_index.ntotal}")
        print(f"query: {query}")
        nodes = self.index_retriever.retrieve(query)
        print(f"检索到的节点数量: {nodes}")
        return [
            LangchainDocument(
                page_content=node.text,
                metadata=node.metadata
            )
            for node in nodes
        ]
        
    async def _aget_relevant_documents(self, query: str) -> List[LangchainDocument]:
        return self._get_relevant_documents(query)

def get_retriever(index):
    """创建检索器"""
    index_retriever = index.as_retriever(similarity_top_k=SIMILARITY_TOP_K)
    return LlamaIndexRetriever(index_retriever=index_retriever) 