"""
像之前直接使用提示词来进行判定会有两个不好的点：

第一上下文太大，比如大纲或者历史问题消耗token太多
第二判断一句文本在一堆文本（即使有结构）中是否存在相似的，并不准确

判断相似性首先用embedding
"""
import numpy as np
import openai
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langfuse.decorators import observe, langfuse_context

cache = {}
template_check_quest = """
你是一个课堂助教，帮助老师记录课堂问题，对学员问题进行整理判断
如下是课堂大纲：
{outlines}
学员输入：
{student_input}
如果这个问题是老师需要回答的则回复Y否则回复N
只回复Y或者N，不要回复其他内容
"""
prompt = ChatPromptTemplate.from_template(template_check_quest)
outlines = """
大模型概述
提示词
函数回调
RAG
智能体
模型微调
"""
llm = ChatOpenAI(temperature=0)
chain = (
        {"outlines": lambda _: outlines, "student_input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
)

# 获取文本的词嵌入，仍然属于模型算法但不是chat操作，langfuse不会主动标记为generation
@observe(as_type="generation")
def get_embeddings(text):
    if text in cache:
        return cache[text]
    data = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small",
        dimensions=256
    ).data
    cache[text] = data[0].embeding
    return cache[text]


@observe()
def cos_sim(v, m):
    # 点乘除以范数积得到相似度列表
    score = np.dot(m, v)/(np.linalg.norm(m, axis=1)*np.linalg.norm(v))
    return score.tolist()

@observe()
def check_duplicated(query,existing,threshold=0.825):
    query_vec = np.array(get_embeddings(query))  # 待校验向量 一维
    mat = np.array([item[1] for item in existing])  # 历史向量 二维
    cos = cos_sim(query_vec,mat) # 一对多进行相似度比较
    return max(cos) >= threshold

@observe
def need_answer(question,outlines):
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    res = chain.invoke(question, config={"callbacks": [langfuse_handler]})
    print(res)
    if res == 'Y':
        print("问题符合")
    else:
        print("不相关")


question_list = [("langchain支持java么", get_embeddings("langchain支持java么"))]
@observe()
def verify_question(question: str, outlines: str, question_list: list, user_id):
    langfuse_context.update_current_trace(name="课堂助手", user_id="001")
    if need_answer(question,outlines):
        if not check_duplicated(question, question_list):
            vec = cache[question]
            question_list.append((question,vec))
            return True

    return False

