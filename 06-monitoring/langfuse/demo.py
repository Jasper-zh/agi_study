"""
sk-lf-f2e725da-7d72-40b2-bf78-d0125557c553
pk-lf-09c48a9f-f424-423b-9dfc-353620d006c8
https://us.cloud.langfuse.com
"""




from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # 加载.env进环境变量


from langfuse.decorators import observe, langfuse_context
from langfuse.openai import openai  # OpenAI integration

@observe(name="大模型交互")
def story():
    return openai.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=100,
        messages=[
            {"role": "system", "content": "You are a great storyteller."},
            {"role": "user", "content": "在很久很久以前..."}
        ],
    ).choices[0].message.content


@observe(name="查询数据库")
def queryData():
    # @oberve的属性是标记span的属性
    # langfuse_context.update_current_trace是标记当前trace的属性
    # 第一个span的属性为trace属性，但中途也能通过该函数修改trace属性
    langfuse_context.update_current_trace(name="一次RAG", user_id="001")
    return "一些数据"


@observe(name="一次交互")
def main():
    # 存在多个步骤；
    data = queryData()  # 查询数据库
    res = story()  # 调用大模型
    return res


if __name__ == '__main__':
    res = main()
    print(res)