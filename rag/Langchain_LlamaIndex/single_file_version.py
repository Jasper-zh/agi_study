from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

import pandas as pd
import json
from tqdm import tqdm
import os
import sys
import numpy as np
import torch
from typing import Any, List
from langchain_core.documents import Document as LangchainDocument

# 检查 numpy 版本  (目前faiss 1.7.4 对于 NumPy2.x 未适配可能出现错误)
print(f"NumPy version: {np.__version__}")
if np.__version__ != "1.23.5":
    print("Warning: NumPy version may cause compatibility issues with FAISS")
    print("Please run: pip install numpy==1.23.5")



# 打印模型缓存路径
print(f"HF_HOME: {os.getenv('HF_HOME')}")
print(f"模型将保存在: {os.path.join(os.getenv('HF_HOME', ''), 'models--BAAI--bge-m3')}")

try:
    from llama_index.core import Document, VectorStoreIndex, StorageContext
    from llama_index.core.node_parser import SimpleNodeParser
    from llama_index.core.settings import Settings
    from llama_index.vector_stores.faiss import FaissVectorStore
    from FlagEmbedding import FlagModel
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_openai import ChatOpenAI
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    from faiss import IndexFlatL2
    from llama_index.core.embeddings import BaseEmbedding
    from pydantic import Field
    from langchain_core.retrievers import BaseRetriever
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


# === 1. 加载知识库 Excel （格式确定手动加载）===
def load_excel_to_documents(excel_path):
    df = pd.read_excel(excel_path)
    docs = []
    for _, row in df.iterrows():
        concept = str(row["名词"])
        explanation = str(row["解释"])
        content = f"{concept}：{explanation}"
        docs.append(Document(text=content, metadata={"concept": concept}))
    return docs


# === 2. 初始化模型和索引 ===
def init_rag_pipeline(docs):
    print("正在加载 BGE 模型...")
    # 初始化 BGE 嵌入模型
    model = FlagModel(
        'BAAI/bge-m3',
        use_fp16=True,  # 使用半精度浮点数加速
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    print("BGE 模型加载完成！")
    
    # 创建自定义的嵌入类
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
    
    # 使用自定义的嵌入类
    embedding_model = BGEEmbeddings(model=model)
    
    # 设置全局设置
    Settings.embed_model = embedding_model
    
    # 初始化 FAISS 向量存储
    faiss_index = IndexFlatL2(1024)  # BGE-m3 的向量维度是 1024
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 创建索引
    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        show_progress=True
    )

    # 创建自定义的检索器类
    class LlamaIndexRetriever(BaseRetriever):
        index_retriever: Any = Field(default=None, description="LlamaIndex retriever instance")
        
        def __init__(self, index_retriever: Any, **kwargs):
            super().__init__(**kwargs)
            self.index_retriever = index_retriever
            
        def _get_relevant_documents(self, query: str) -> List[LangchainDocument]:
            nodes = self.index_retriever.retrieve(query)
            return [
                LangchainDocument(
                    page_content=node.text,
                    metadata=node.metadata
                )
                for node in nodes
            ]
            
        async def _aget_relevant_documents(self, query: str) -> List[LangchainDocument]:
            return self._get_relevant_documents(query)

    # 创建检索器
    index_retriever = index.as_retriever(similarity_top_k=3)
    retriever = LlamaIndexRetriever(index_retriever=index_retriever)

    # 构建 Langchain QA Chain，添加代理配置
    llm = ChatOpenAI(
        model='gpt-3.5-turbo',
        temperature=0,
        openai_api_base=os.getenv("OPENAI_API_BASE"),  # 使用环境变量中的代理地址
        request_timeout=60  # 设置超时时间
    )

    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "你是一个专业的中文智能助手。\n"
            "以下是一些参考资料：\n"
            "{context}\n\n"
            "根据这些资料回答下面的问题：\n"
            "{question}"
        )
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=True
    )

    return qa_chain


# === 3. 批量处理问题 ===
def process_questions(qa_chain, question_file, output_file):
    with open(question_file, 'r', encoding='utf-8') as f:
        questions = [line.strip() for line in f if line.strip()]

    with open(output_file, 'w', encoding='utf-8') as out_f:
        for question in tqdm(questions, desc="Processing"):
            try:
                result = qa_chain(question)
                retrieved_docs = [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result["source_documents"]
                ]

                # 自动判断是否命中知识库
                knowledge_hit = len(retrieved_docs) > 0

                data = {
                    "query": question,
                    "answer": result["result"],
                    "retrieved_docs": retrieved_docs,
                    "knowledge_hit": knowledge_hit,
                    "retrieval_hit": None,      # 后续可人工标注
                    "answer_quality": None,     # 后续可人工标注
                    "notes": ""
                }

                out_f.write(json.dumps(data, ensure_ascii=False) + '\n')

            except Exception as e:
                print(f"Error processing question: {question} | {e}")


# === 4. 主函数 ===
if __name__ == "__main__":
    excel_path = "data/knowledge_base.xlsx"
    question_file = "data/questions.txt"
    output_file = "data/output_annotations.jsonl"

    docs = load_excel_to_documents(excel_path)
    qa_chain = init_rag_pipeline(docs)
    process_questions(qa_chain, question_file, output_file)

    print(f"\n✅ 处理完成，标注数据保存在：{output_file}")