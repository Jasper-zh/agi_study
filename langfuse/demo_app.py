"""
判定一个问题要不要收集
第一该问题是否和课堂相关
第二该问题或者相似不能已经问过了
若两次都是Y,则该问题可以记录
"""




from dotenv import load_dotenv, find_dotenv
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langfuse.decorators import observe, langfuse_context

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
template_check_quest = """
你是一个课堂助教，帮助老师记录课堂问题，对学员问题进行整理判断
如下是课堂大纲：
{outlines}
学员输入：
{student_input}
如果这个问题是老师需要回答的则回复Y否则回复N
只回复Y或者N，不要回复其他内容
"""
template_check_duplicated = """
************
已有问题列表：
[
{questions}
]
************
新问题：
{new}
如果这个问题已经问过了在已有问题当中则回复N否则回复Y
只回复Y或者N，不要回复其他内容
"""

prompt1 = ChatPromptTemplate.from_template(template_check_quest)
prompt2 = ChatPromptTemplate.from_template(template_check_duplicated)

# 获取大模型
llm = ChatOpenAI(temperature=0)  # 发散性为0 无需传参密钥公钥都从环境变量读取了

# 构建链式调用器（参数question运行时输入，context为检索结果）
outlines = """
大模型概述
提示词
函数回调
RAG
智能体
模型微调
"""

chain1 = (
        {"outlines": lambda _: outlines, "student_input": RunnablePassthrough()}
        | prompt1
        | llm
        | StrOutputParser()
)
questions = """
'提示词怎么写更好'，
'什么叫做智能体'，
'函数回调是什么'，
"""


chain2 = (
        {"questions": lambda _: questions, "new": RunnablePassthrough()}
        | prompt2
        | llm
        | StrOutputParser()
)


@observe(name="锁定问题")
def lockQuestion(question: str):
    res = checkQuestion(question)
    if res == 'Y':
        current_question = question
        return current_question
    else:
        return


@observe(name="问题判定")
def checkQuestion(question: str):
    print(question)

    # 这里要注意这个langfuse处理器不能用第一行创建的，因为这样这次调用是独立记录，而不在一个trace
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    res = chain1.invoke(question, config={"callbacks": [langfuse_handler]})
    print(res)
    if res is None:
        print("问题无关")
        return
    else:
        return checkDuplicate(res)
    return res


@observe(name="重复判定")
def checkDuplicate(question: str):
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    res = chain2.invoke(question, config={"callbacks": [langfuse_handler]})
    print(res)
    if res == 'N':
        print("问题重复")
    return res


@observe(name="问题是否记录")
def main():
    langfuse_context.update_current_observation(name="课堂助手")
    res = lockQuestion("RAG需要哪些设施")




if __name__ == '__main__':
    res = main()
    print(res)