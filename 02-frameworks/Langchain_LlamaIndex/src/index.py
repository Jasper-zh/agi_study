import pandas as pd
from pathlib import Path
from typing import List, Optional, Union
from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
from faiss import IndexFlatL2
import faiss
import os
from config.config import (
    KNOWLEDGE_BASE_PATH,
    VECTOR_STORE_PATH,
    VECTOR_STORE_PATH01,
    VECTOR_DIMENSION
)

def ensure_vector_store_dir():
    """确保向量存储目录存在"""
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)

def load_documents(excel_path: str = None, csv_encoding: str = 'utf-8') -> List[Document]:
    """从Excel或CSV文件加载文档
    
    Args:
        excel_path: 文件路径，如果为None则使用默认路径。支持 .xlsx 和 .csv 格式
        csv_encoding: CSV文件的编码格式，默认为 'utf-8'。常见编码包括：
            - 'utf-8': 通用编码
            - 'gbk': 中文Windows常用编码
            - 'gb2312': 简体中文编码
            - 'gb18030': 中文扩展编码
        
    Returns:
        List[Document]: 文档列表
    """
    if excel_path is None:
        excel_path = str(KNOWLEDGE_BASE_PATH)
    
    print(f"从 {excel_path} 加载文档...")
    
    try:
        # 根据文件扩展名选择读取方式
        file_extension = Path(excel_path).suffix.lower()
        
        if file_extension == '.xlsx':
            df = pd.read_excel(excel_path)
        elif file_extension == '.csv':
            try:
                # 首先尝试使用指定的编码
                df = pd.read_csv(excel_path, encoding=csv_encoding)
            except UnicodeDecodeError:
                # 如果指定的编码失败，尝试其他常见编码
                encodings = ['gbk', 'gb2312', 'gb18030', 'utf-8']
                for encoding in encodings:
                    try:
                        print(f"尝试使用 {encoding} 编码读取文件...")
                        df = pd.read_csv(excel_path, encoding=encoding)
                        print(f"成功使用 {encoding} 编码读取文件")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError(f"无法使用任何支持的编码读取文件。支持的编码: {', '.join(encodings)}")
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}。请使用 .xlsx 或 .csv 文件")
        
        # 获取第一行作为键
        keys = df.columns.tolist()
        print(f"检测到的列: {keys}")
        
        # 存储所有文档
        documents = []
        
        # 遍历每一行
        for _, row in df.iterrows():
            # 使用第一行的键来拼接内容
            content_parts = []
            for key in keys:
                if pd.notna(row[key]):  # 检查值是否非空
                    content_parts.append(f"{key}: {row[key]}")
            
            # 如果所有值都为空，跳过这一行
            if not content_parts:
                continue
                
            # 拼接所有内容
            content = "\n".join(content_parts)
            
            # 创建文档
            doc = Document(
                text=content,
                metadata={
                    "source": excel_path,
                    "row": _ + 2,  # 行号从1开始，且第一行是标题
                    "file_type": file_extension
                }
            )
            documents.append(doc)
        
        print(f"成功加载 {len(documents)} 个文档")
        return documents
        
    except Exception as e:
        print(f"加载文档时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return []

def build_index(docs: List[Document], embed_model, force_rebuild: bool = False) -> VectorStoreIndex:
    """构建向量索引
    
    Args:
        docs: 文档列表
        embed_model: 嵌入模型
        force_rebuild: 是否强制重建索引
    """
    try:
        # 确保向量存储目录存在
        ensure_vector_store_dir()
        
        print("初始化 FAISS 向量存储...")
        # 初始化 FAISS 向量存储
        faiss_index = IndexFlatL2(VECTOR_DIMENSION)
        faiss_vector_store = FaissVectorStore(faiss_index=faiss_index)
        
        print("创建存储上下文...")
        # 创建存储上下文 (构建索引时不要配置目录)
        storage_context = StorageContext.from_defaults(vector_store=faiss_vector_store)

        print("创建向量索引...")
        # 创建索引
        index = VectorStoreIndex.from_documents(
            docs,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True
        )
        
        print("持久化索引...")
        # 持久化索引
        index.storage_context.persist(persist_dir=str(VECTOR_STORE_PATH01))
        # faiss_vector_store.persist(persist_path=str(VECTOR_STORE_PATH01))
        # storage_context.persist(persist_dir=str(VECTOR_STORE_PATH))
        print("索引构建完成！")
        return index
        
    except Exception as e:
        print(f"构建索引时发生错误: {str(e)}")
        raise

def load_index(embed_model) -> Optional[VectorStoreIndex]:
    """加载已持久化的索引"""
    try:
        # 确保向量存储目录存在
        ensure_vector_store_dir()
        
        print("从向量存储加载索引...")
        faiss_index = IndexFlatL2(VECTOR_DIMENSION)
        faiss_vector_store = FaissVectorStore.from_persist_dir(str(VECTOR_STORE_PATH01))
        storage_context = StorageContext.from_defaults(vector_store=faiss_vector_store, persist_dir=str(VECTOR_STORE_PATH01))
        index = load_index_from_storage(storage_context=storage_context)
        print("从向量存储加载索引结束")
        
        # 打印加载的索引维度
        print(f"加载的索引维度: {index.storage_context.vector_store._faiss_index.d}")
        print(f"加载的索引向量数量: {index.storage_context.vector_store._faiss_index.ntotal}")

        return index
    except Exception as e:
        print(f"加载索引时发生错误: {str(e)}")
        return None

def update_index(
    new_docs: List[Document],
    embed_model,
    mode: str = "append",
    excel_path: Optional[Union[str, Path]] = None
) -> VectorStoreIndex:
    """更新索引
    
    Args:
        new_docs: 新文档列表
        embed_model: 嵌入模型
        mode: 更新模式，可选 "append"（追加）或 "overwrite"（覆盖）
        excel_path: 知识库文件路径，用于覆盖模式
    """
    try:
        # 确保向量存储目录存在
        ensure_vector_store_dir()
        
        if mode == "overwrite":
            # 覆盖模式：完全重建索引
            print("使用覆盖模式更新索引...")
            return build_index(new_docs, embed_model, force_rebuild=True)
            
        elif mode == "append":
            # 追加模式：加载现有索引并添加新文档
            print("使用追加模式更新索引...")
            index = load_index(embed_model)
            
            if index is None:
                print("未找到现有索引，创建新索引...")
                return build_index(new_docs, embed_model)
                
            print("向现有索引添加新文档...")
            for doc in new_docs:
                index.insert(doc)
                
            # 重新持久化索引
            index.storage_context.persist()
            return index
            
        else:
            raise ValueError(f"不支持的更新模式: {mode}")
    except Exception as e:
        print(f"更新索引时发生错误: {str(e)}")
        raise

def get_index_status() -> dict:
    """获取索引状态"""
    try:
        # 确保向量存储目录存在
        ensure_vector_store_dir()
        
        status = {
            "exists": VECTOR_STORE_PATH.exists(),
            "vector_store_path": str(VECTOR_STORE_PATH),
            "knowledge_base_path": str(KNOWLEDGE_BASE_PATH),
            "knowledge_base_exists": KNOWLEDGE_BASE_PATH.exists()
        }
        
        if status["exists"]:
            # 获取向量存储文件大小
            total_size = sum(f.stat().st_size for f in VECTOR_STORE_PATH.glob("**/*") if f.is_file())
            status["vector_store_size"] = f"{total_size / 1024 / 1024:.2f} MB"
            
        if status["knowledge_base_exists"]:
            # 获取知识库文档数量
            df = pd.read_excel(KNOWLEDGE_BASE_PATH)
            status["document_count"] = len(df)
            
        return status
    except Exception as e:
        print(f"获取索引状态时发生错误: {str(e)}")
        return {
            "error": str(e),
            "exists": False,
            "vector_store_path": str(VECTOR_STORE_PATH)
        } 