"""
lang_chain_example -

Author: zhang
Date: 2024/3/11
"""
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

# 加载当前目录下的.env到系统环境
_ = load_dotenv(find_dotenv())

llm = ChatOpenAI(model="gpt-3.5-turbo")  # 默认是gpt-3.5-turbo

if __name__ == '__main__':
    response = llm.invoke("你是谁")
    print(response.content)