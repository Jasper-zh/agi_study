"""
lang_chain_template_example -

Author: zhang
Date: 2024/3/11
"""
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
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

# 多消息模板
messages = [
    SystemMessagePromptTemplate.from_template("你是小胖早点服务员，店内有热干面（5元）、汤面（5元）、米线（5元）、{x}。请服务用户点餐，若有非点餐相关问题礼貌回复不太清楚"),
    HumanMessage("有什么吃的"),
    AIMessage("您好，菜单如下，你想点些什么呢？"),
    HumanMessagePromptTemplate.from_template("来个{input}吧，多少钱呀")
]
if __name__ == '__main__':
    template = ChatPromptTemplate.from_messages(messages)
    messages = template.format_messages(x="杂酱面（15元）",input="杂酱面")
    print(messages)
    response = llm.invoke(messages)
    print(response.content)

# # 单条提示词模板
# if __name__ == '__main__':
#     template = PromptTemplate.from_template("介绍个{type}类的游戏")
#     print(template)
#     format_str = template.format(type='RPG')
#     print(format_str)
#     print(llm.invoke(format_str).content)