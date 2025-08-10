from datetime import datetime

from dotenv import load_dotenv, find_dotenv
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import QianfanChatEndpoint # 千帆大模型也一样，使用该函数创建模型传入chain就行了
from langfuse.decorators import observe, langfuse_context

_ = load_dotenv(find_dotenv())  # 加载.env进环境变量

# Initialize Langfuse handler
from langfuse.callback import CallbackHandler

# 可以通过CallbackHandler去手动创建这个回调处理器，但一般在trace当中获取当前trace的处理器即可
# langfuse_handler = CallbackHandler(
#     secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
#     public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
#     host=os.getenv("LANGFUSE_HOST"),  # 🇪🇺 EU region
#     # host="https://us.cloud.langfuse.com", # 🇺🇸 US region
# )

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


# 由于langchain提供了回调参数，能自定义函数传过去接收信息，langfuse利用这一点提供了一个函数来采集数据到自己平台
@observe()
def main(key,num):
    user_id = "001"
    session_id = user_id + "_" + datetime.now().strftime("%Y%m%d")
    langfuse_context.update_current_trace(name="会话里的trace",user_id=user_id,session_id=session_id)
    # 配置回调处理器，来记录到langfuse
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    return chain.invoke(  {"context": key, "num": num}, config={"callbacks": [langfuse_handler]})


if __name__ == '__main__':
    res = main("小狗",30)
    print(res)