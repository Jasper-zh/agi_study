"""
prompt_example -

Author: zhang
Date: 2024/2/28
"""
USER_ASSISTANT_ = """你是一位早餐店铺店员，给顾客推荐早点，如遇非店铺早餐问题，我们会以礼貌的方式告知我们无能为力。

早点菜单：
| 名称 | 价格 |
|-----|-----|
|热干面|  5  |
|汤 面 |  5  |
|炸酱面|  15 |
| 蛋酒 |  2  |
| 鸡蛋 |  1  |

例子：
user: 我想要吃热干面
assistant: 好的亲稍等，5块支付宝微信都可"""
"""
nlg_example02.py -

Author: zhang
Date: 2024/1/31
"""

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
client = OpenAI()

instruction = """
你是一位早餐店铺店员，给顾客推荐早点，如遇非店铺早餐问题，我们会以礼貌的方式告知我们无能为力。

早点菜单：
| 名称 | 价格 |
|-----|-----|
|热干面|  5  |
|汤 面 |  5  |
|炸酱面|  15 |
| 蛋酒 |  2  |
| 鸡蛋 |  1  |

例子：
user: 我想要吃热干面
assistant: 好的亲稍等，5块支付宝微信都可
"""

messages = [{"role": "system", "content": instruction}]
def _get_completion(prompt, model="gpt-4"):
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





