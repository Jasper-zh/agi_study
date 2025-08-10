"""
func_call_example03 -

Author: zhang
Date: 2024/1/31
"""
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
import json

_ = load_dotenv(find_dotenv())

client = OpenAI()

def print_json(data):
    if hasattr(data, 'model_dump_json'):
        data = json.loads(data.model_dump_json())

    if (isinstance(data, (list, dict))):
        print(json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ))
    else:
        print(data)

# 使用function_calling，可以更容易得到用户输入串形成准确的json信息
def get_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,  # 模型输出的随机性，0 表示随机性最小
        tools=[{
            "type": "function",
            "function": {
                "name": "add_contact",
                "description": "添加联系人",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "联系人姓名"
                        },
                        "address": {
                            "type": "string",
                            "description": "联系人地址"
                        },
                        "tel": {
                            "type": "string",
                            "description": "联系人电话"
                        },
                    }
                }
            }
        }],
    )
    return response.choices[0].message

if __name__ == '__main__':
    prompt = "帮我寄给王卓然，地址是北京市朝阳区亮马桥外交办公大楼，电话13012345678。"
    messages = [
        {"role": "system", "content": "你是一个联系人录入员。"},
        {"role": "user", "content": prompt}
    ]
    response = get_completion(messages)
    print("====GPT回复====")
    print(response)
    print_json(response)
    args = json.loads(response.tool_calls[0].function.arguments)
    print("====函数参数====")
    print(args)
    print_json(args)