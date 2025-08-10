"""
sk-lf-f2e725da-7d72-40b2-bf78-d0125557c553
pk-lf-09c48a9f-f424-423b-9dfc-353620d006c8
https://us.cloud.langfuse.com
"""




from dotenv import load_dotenv, find_dotenv
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import QianfanChatEndpoint # 千帆大模型也一样，使用该函数创建模型传入chain就行了

_ = load_dotenv(find_dotenv())  # 加载.env进环境变量

# Initialize Langfuse handler
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST"),  # 🇪🇺 EU region
    # host="https://us.cloud.langfuse.com", # 🇺🇸 US region
)

# Your Langchain code

# Add Langfuse handler as callback (classic and LCEL)
# Prompt模板
template = """
请讲一个关于{context}的故事
注意字数限制不能超过{num}个汉字
"""
prompt = ChatPromptTemplate.from_template(template)

# 获取大模型
llm = ChatOpenAI(temperature=0)  # 发散性为0 无需传参密钥公钥都从环境变量读取了

# 构建链式调用器
chain = (
        {"context": RunnablePassthrough(), "num": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)
chain02 = (
        {"context": lambda _:"狗", "num": RunnablePassthrough()}  # (这里要注意，如果是固定参数需要以回调的形式而不能直接字符串，比如通过lambda _:"狗")
        | prompt
        | llm
        | StrOutputParser()
)

# 由于langchain提供了回调参数，能自定义函数传过去接收信息，langfuse利用这一点提供了一个函数来采集数据到自己平台
def main():
    #return chain02.invoke({"context": '狗', "num": 20}, config={"callbacks": [langfuse_handler]})
    return chain02.invoke( 100, config={"callbacks": [langfuse_handler]})


if __name__ == '__main__':
    res = main()
    print(res)