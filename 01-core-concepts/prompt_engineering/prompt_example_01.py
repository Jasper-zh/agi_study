"""
prompt_example03 -

Author: zhang
Date: 2024/2/29
"""
from openai import OpenAI
from config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY,base_url=settings.OPENAI_BASE_URL)
messages = []


def _get_completion(prompt, model="gpt-3.5-turbo"):
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    print(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": response.choices[0].message.content})

if __name__ == '__main__':
    while True:
        print("请输入：")
        msg = input()
        _get_completion(msg)