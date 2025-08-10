"""
rag_llm_example03 - 搜索结果汇入大模型

Author: zhang
Date: 2024/2/22
"""
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv


# 加载当前目录下的.env到系统环境
_ = load_dotenv(find_dotenv())
# 配置 OpenAI 服务 （从系统环境读取）
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户问题。
确保你的回复完全依据下述已知信息。不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。

已知信息:
__INFO__

用户问：
__QUERY__

请用中文回答用户问题。
"""

def build_prompt(prompt_template, **kwargs):
    '''将 Prompt 模板赋值'''
    prompt = prompt_template
    for k, v in kwargs.items():
        if isinstance(v, str):
            val = v
        elif isinstance(v, list) and all(isinstance(elem, str) for elem in v):
            val = '\n'.join(v)
        else:
            val = str(v)
        prompt = prompt.replace(f"__{k.upper()}__", val)
    return prompt

def get_completion(prompt, model="gpt-3.5-turbo"):
    '''封装 openai 接口'''
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    """
    模拟定向检索结果
    传统关键字检索，关键字不一样则搜索出内容不同，
    增强检索会使用向量检索来对语义进行检索，即使搜索关键字不一样但意思是同等的也会得到匹配这个意思的结果
    """
    result = r" Llama 2 comes in a range of parameter sizes—7B, 13B, and 70B—as well as pretrained and fine-tuned variations. 1. Llama 2, an updated version of Llama 1, trained on a new mix of publicly available data. We also increased the size of the pretraining corpus by 40%, doubled the context length of the model, and adopted grouped-query attention (Ainslie et al., 2023). We are releasing variants of Llama 2 with 7B, 13B, and 70B parameters. We have also trained 34B variants, which we report on in this paper but are not releasing.§"
    # 用户问题结合检索结果构成提示词
    prompt = build_prompt(prompt_template, query="有几种规模？有什么区别介绍下", info=result)
    print("提示词："+prompt)
    res = get_completion(prompt)
    print(res)
