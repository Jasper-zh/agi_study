import os

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

# 初始化 OpenAI 服务。会自动从环境变量加载 OPENAI_API_KEY 和 OPENAI_BASE_URL
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def say():
    # 消息
    messages = [
        {
            "role": "system",
            "content": "你是一个早餐店员，现在还售卖有热干面、汤面、米线"
        },
        {
            "role": "user",
            "content": "给我来碗牛肉面"  # 用户问题，可以自行尝试更改
        },
    ]
    # 调用 GPT-3.5
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    # 输出回复
    print(chat_completion.choices[0].message.content)

def prompt_():
    prompt = "下班了，今天我很"
    # 调用 GPT-3.5
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        stream=True
    )
    # 输出回复
    for chunk in response:
        print(chunk.choices[0].text, end='')



if __name__ == '__main__':
    say()
    #prompt_()


