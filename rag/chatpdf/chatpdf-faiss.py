from PyPDF2 import PdfReader
from langchain.chains.question_answering import load_qa_chain
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import OpenAI
from langchain_community.callbacks.manager import get_openai_callback
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Tuple
from collections import Counter
import os
import pickle

def extract_text_with_page_numbers(pdf) -> Tuple[str, List[int]]:
    """
    从PDF中提取文本并记录每行文本对应的页码
    
    参数:
        pdf: PDF文件对象
    
    返回:
        text: 提取的文本内容
        page_numbers: 每行文本对应的页码列表
    """
    text = ""
    page_numbers = []

    for page_number, page in enumerate(pdf.pages, start=1):
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text
            # 创建一个包含当前页码的列表，长度等于文本行数
            # 将这个页码列表添加到总的页码列表中
            page_numbers.extend([page_number] * len(extracted_text.split("\n")))
        else:
            Logger.warning(f"No text found on page {page_number}.")

    return text, page_numbers


def process_text_with_splitter(text: str, page_numbers: List[int], save_path: str = None) -> FAISS:
    """
    处理文本并创建向量存储
    
    参数:
        text: 提取的文本内容
        page_numbers: 每行文本对应的页码列表
    
    返回:
        knowledgeBase: 基于FAISS的向量存储对象
    """
    # 创建文本分割器，用于将长文本分割成小块
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " ", ""],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    # 分割文本
    chunks = text_splitter.split_text(text)
    #Logger.debug(f"Text split into {len(chunks)} chunks.")
    print(f"文本被分割成 {len(chunks)} 个块。")
        
    # 创建OpenAI的嵌入模型（也可以使用其他的比注释的国内的）
    # from langchain_community.embeddings import DashScopeEmbeddings
    # embeddings = DashScopeEmbeddings(
    #     model="text-embedding-v1",
    #     dashscope_api_key="xxx",
    # )
    embeddings = OpenAIEmbeddings()
    # 从文本块创建知识库
    knowledgeBase = FAISS.from_texts(chunks, embeddings)
    #Logger.info("Knowledge base created from text chunks.")
    print("已从文本块创建知识库。")
    
    # 创建一个与文本等长的页码列表，每个字符对应一个页码
    char_pages = []
    for page_num, page_text in zip(page_numbers, text.split('\n')):
        char_pages.extend([page_num] * len(page_text)) # 每个索引位置都表示一个字，值是页码
        char_pages.append(page_num)  # 为换行符添加页码

    # 为每个chunk找到最常见的页码
    chunk_page_info = {}
    for chunk in chunks:
        chunk_start = text.find(chunk)
        if chunk_start != -1 and chunk_start + len(chunk) <= len(char_pages):
            # 获取这个chunk中所有字符的页码
            chunk_pages = char_pages[chunk_start:chunk_start + len(chunk)]
            # 找出该区块占用最多的页码 比如一个区块五个字,最后一个字在第二页 [1,1,1,1,2]
            most_common_page = Counter(chunk_pages).most_common(1)[0][0] # Counter({1:4,2:1}) => [(1:4)] => 1
            chunk_page_info[chunk] = most_common_page
        else:
            chunk_page_info[chunk] = "未知"

    knowledgeBase.page_info = chunk_page_info # 得到了每个chunk对应主要页码

    # 如果提供了保存路径，则保存向量数据库和页码信息
    if save_path:
        # 确保目录存在
        os.makedirs(save_path, exist_ok=True)

        # 保存FAISS向量数据库
        knowledgeBase.save_local(save_path)
        print(f"向量数据库已保存到: {save_path}")

        # 保存页码信息到同一目录
        with open(os.path.join(save_path, "page_info.pkl"), "wb") as f:
            pickle.dump(page_info, f)
        print(f"页码信息已保存到: {os.path.join(save_path, 'page_info.pkl')}")

    return knowledgeBase


def load_knowledge_base(load_path: str, embeddings=None) -> FAISS:
    """
    从磁盘加载向量数据库和页码信息

    参数:
        load_path: 向量数据库的保存路径
        embeddings: 可选，嵌入模型。如果为None，将创建一个新的DashScopeEmbeddings实例

    返回:
        knowledgeBase: 加载的FAISS向量数据库对象
    """
    # 如果没有提供嵌入模型，则创建一个新的
    if embeddings is None:
        embeddings = OpenAIEmbeddings()

    # 加载FAISS向量数据库，添加allow_dangerous_deserialization=True参数以允许反序列化
    knowledgeBase = FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)
    print(f"向量数据库已从 {load_path} 加载。")

    # 加载页码信息
    page_info_path = os.path.join(load_path, "page_info.pkl")
    if os.path.exists(page_info_path):
        with open(page_info_path, "rb") as f:
            page_info = pickle.load(f)
        knowledgeBase.page_info = page_info
        print("页码信息已加载。")
    else:
        print("警告: 未找到页码信息文件。")

    return knowledgeBase


# 读取PDF文件
pdf_reader = PdfReader('浦发上海浦东发展银行西安分行个金客户经理考核办法.pdf')
# 提取文本和页码信息
text, page_numbers = extract_text_with_page_numbers(pdf_reader)
print('text=', text)
print('page_numbers=', page_numbers)
#text



print(f"提取的文本长度: {len(text)} 个字符。")
    
# 处理文本并创建知识库
save_dir = "./vector_db"
knowledgeBase = process_text_with_splitter(text, page_numbers, save_path=save_dir)


# In[ ]:


# 设置查询问题
query = "客户经理被投诉了，投诉一次扣多少分"
# query = "客户经理每年评聘申报时间是怎样的？"

if query:
    # 执行相似度搜索，找到与查询相关的文档
    docs = knowledgeBase.similarity_search(query)

    # 初始化OpenAI语言模型（或者其他模型）
    # from langchain_community.llms import Tongyi
    # llm = Tongyi(
    #     model_name="deepseek-v3",
    #     dashscope_api_key="xxx"
    # )
    api_key = ""
    llm = OpenAI(
        api_key = api_key,
        base_url = 'https://openai.itit.cc/v1'
    )

    # 加载问答链
    chain = load_qa_chain(llm, chain_type="stuff")

    # 准备输入数据
    input_data = {"input_documents": docs, "question": query}

    # 使用回调函数跟踪API调用成本
    with get_openai_callback() as cost:
        # 执行问答链
        response = chain.invoke(input=input_data)
        print(f"查询已处理。成本: {cost}")
        print(response["output_text"])
        print("来源:")

    # 记录唯一的页码
    unique_pages = set()

    # 显示每个文档块的来源页码
    for doc in docs:
        text_content = getattr(doc, "page_content", "")
        source_page = knowledgeBase.page_info.get(
            text_content.strip(), "未知"
        )

        if source_page not in unique_pages:
            unique_pages.add(source_page)
            print(f"文本块内容: {text_content}")
            print(f"文本块页码: {source_page}")
            print("-" * 50)  # 添加分隔线，使输出更清晰

