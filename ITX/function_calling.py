# 初始化
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
import json

_ = load_dotenv(find_dotenv())
client = OpenAI()

# 获取大模型回复
def get_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
        tools=[{  # 用 JSON 描述函数。可以定义多个。由大模型决定调用谁。也可能都不调用
            "type": "function",
            "function": {
                "name": "count",   # 函数名称
                "description": "加法器,计算数字的和",  # 函数描述
                "parameters": {        # 函数参数
                    "type": "object",  # 参数类型：对象
                    "properties": {    # 对象属性
                        "numbers": {
                            "type": "array", # 该属性类型：数组
                            "items": {       # 数组子项的定义
                                "type": "number"
                            }
                        }
                    }
                }
            }
        }],
    )
    return response.choices[0].message

def result():
    prompt = "早餐店店员A做了5碗面条，店员B做了3碗，现在有多少碗了？"

    # 初始对话session
    messages = [
        {"role": "user", "content": prompt}
    ]
    # 初始对话得到一个回复(回复的是一个按照函数格式解析了用户问题)
    response = get_completion(messages)

    # 把大模型的回复加入到对话历史中
    messages.append(response)

    print("=====GPT回复=====")
    print(response)

    if (response.tool_calls is not None):
        # 取响应的函数对象
        tool_call = response.tool_calls[0]
        # 如果函数名称是求和，则取出参数的numbers属性进行求和
        if (tool_call.function.name == "count"):
            # 调用 sum
            args = json.loads(tool_call.function.arguments)
            result = sum(args["numbers"])
            print("=====函数返回=====")
            print(result)

            # 把函数调用结果加入到对话历史中（以及上面响应的函数的函数ID要传回，注意角色是tool）
            messages.append(
                {
                    "tool_call_id": tool_call.id,  # 用于标识函数调用的 ID
                    "role": "tool",
                    "name": "sum",
                    "content": str(result)  # 数值 result 必须转成字符串
                }
            )

            # 再次调用大模型
            print("=====最终回复=====")
            print(get_completion(messages).content)

if __name__ == '__main__':
    result()

