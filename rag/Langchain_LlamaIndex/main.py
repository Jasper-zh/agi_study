from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

import json
import argparse
from tqdm import tqdm
from pathlib import Path

from config.config import (
    KNOWLEDGE_BASE_PATH,
    QUESTIONS_PATH,
    OUTPUT_PATH
)
from src.embeddings import get_embedding_model
from src.index import (
    load_documents,
    build_index,
    load_index,
    update_index,
    get_index_status
)
from src.retriever import get_retriever
from src.qa_chain import get_qa_chain

def process_questions(qa_chain, question_file, output_file):
    """处理问题并保存结果"""
    with open(question_file, 'r', encoding='utf-8') as f:
        questions = [line.strip() for line in f if line.strip()]

    with open(output_file, 'w', encoding='utf-8') as out_f:
        for question in tqdm(questions, desc="Processing"):
            try:
                print(f"\n处理问题: {question}")
                result = qa_chain(question)
                print("检索到的文档数量:", len(result["source_documents"]))
                
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
                print("处理完成")

            except Exception as e:
                print(f"Error processing question: {question} | {e}")
                import traceback
                traceback.print_exc()

def chat_mode(qa_chain):
    """持续对话模式"""
    print("\n进入持续对话模式，输入 'exit' 或 'quit' 退出")
    print("=" * 50)
    
    while True:
        try:
            # 获取用户输入
            question = input("\n请输入问题: ").strip()
            
            # 检查是否退出
            if question.lower() in ['exit', 'quit']:
                print("退出对话模式")
                break
                
            if not question:
                print("问题不能为空")
                continue
                
            # 处理问题
            result = qa_chain(question)
            
            # 打印检索到的文档
            print("\n检索到的相关文档:")
            for i, doc in enumerate(result["source_documents"], 1):
                print(f"\n文档 {i}:")
                print(f"内容: {doc.page_content}")
                print(f"元数据: {doc.metadata}")
            
            # 打印回答
            print("\n回答:")
            print(result["result"])
            print("=" * 50)
            
        except Exception as e:
            print(f"处理问题时发生错误: {e}")
            continue

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='RAG系统')
    parser.add_argument('--mode', choices=['run', 'update', 'chat'], default='chat',
                      help='运行模式：run（运行问答）或 update（更新索引）或 chat（持续对话）')
    parser.add_argument('--update-mode', choices=['append', 'overwrite'], default='append',
                      help='索引更新模式：append（追加）或 overwrite（覆盖）')
    parser.add_argument('--knowledge-base', type=str,
                      help='知识库文件路径（用于更新模式）')
    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()
    
    # 初始化嵌入模型
    print("初始化嵌入模型...")
    embed_model = get_embedding_model()
    
    if args.mode == 'update':
        # 更新索引模式
        print("检查索引状态...")
        status = get_index_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # 加载新文档
        excel_path = args.knowledge_base if args.knowledge_base else KNOWLEDGE_BASE_PATH
        print(f"从 {excel_path} 加载文档...")
        new_docs = load_documents(excel_path)
        
        # 更新索引
        print("更新索引...")
        index = update_index(
            new_docs=new_docs,
            embed_model=embed_model,
            mode=args.update_mode,
            excel_path=excel_path
        )
        print("索引更新完成！")
        
        # 显示更新后的状态
        status = get_index_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
    else:
        # 运行问答模式或持续对话模式
        # 尝试加载已存在的索引
        print("加载索引...")
        index = load_index(embed_model)
        
        # 如果索引不存在，则构建新的索引
        if index is None:
            print("未找到已存在的索引，正在构建新索引...")
            docs = load_documents()
            index = build_index(docs, embed_model)
            print("索引构建完成！")
        else:
            print("已加载现有索引！")
        
        # 创建检索器
        print("创建检索器...")
        retriever = get_retriever(index)
        print("检索器创建成功")
        
        # 创建 QA 链
        print("创建 QA 链...")
        qa_chain = get_qa_chain(retriever)
        print("QA 链创建成功")
        
        if args.mode == 'chat':
            # 持续对话模式
            chat_mode(qa_chain)
        else:
            # 处理问题
            print("开始处理问题...")
            process_questions(qa_chain, QUESTIONS_PATH, OUTPUT_PATH)
            print(f"\n✅ 处理完成，标注数据保存在：{OUTPUT_PATH}")

if __name__ == "__main__":
    main() 