import os
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config.config import LLM_MODEL

from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

def get_qa_chain(retriever):
    """创建 QA 链"""
    # 构建 Langchain QA Chain
    llm = ChatOpenAI(
        model=LLM_MODEL,
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

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=True
    ) 