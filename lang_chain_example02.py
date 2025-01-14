"""
lang_chain_example02 -

Author: zhang
Date: 2024/3/11
"""
"""
lang_chain_example -

Author: zhang
Date: 2024/3/11
"""
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from langchain.schema import (
    AIMessage, #等价于OpenAI接口中的assistant role
    HumanMessage, #等价于OpenAI接口中的user role
    SystemMessage #等价于OpenAI接口中的system role
)

# 加载当前目录下的.env到系统环境
_ = load_dotenv(find_dotenv())

llm = ChatOpenAI(model="gpt-3.5-turbo")  # 默认是gpt-3.5-turbo
# 若其他大模型
# from langchain_community.chat_models import QianfanChatEndpoint
# from langchain_core.language_models.chat_models import HumanMessage
# import os
#
# qianfan = QianfanChatEndpoint(
#     qianfan_ak=os.getenv('ERNIE_CLIENT_ID'),
#     qianfan_sk=os.getenv('ERNIE_CLIENT_SECRET')
# )

messages = [
    SystemMessage(content="你是小胖早点，你有热干面、汤面、米线，均5元。若有非点餐相关问题礼貌说不知道"),
    HumanMessage(content="有什么吃的"),
    AIMessage(content="有热干面、汤面、米线哦"),
    HumanMessage(content="来碗热干面，多少钱呀")
]


if __name__ == '__main__':
    response = llm.invoke(messages)
    print(response.content)