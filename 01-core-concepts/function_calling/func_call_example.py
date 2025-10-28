"""
func_call_example -

Author: zhang
Date: 2024/1/31
"""

# 初始化
from openai import OpenAI
from config import settings
import json


client = OpenAI(api_key=settings.OPENAI_API_KEY,base_url=settings.OPENAI_BASE_URL)

"""
打印参数。如果参数是有结构的（如字典或列表），则以格式化的 JSON 形式打印；
否则，直接打印该值。
"""
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

def get_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
        tools=[{  # 用 JSON 描述函数。可以定义多个。由大模型决定调用谁。也可能都不调用
            "type": "function",
            "function": {
                "name": "count",
                "description": "加法器,计算数字的和",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "numbers": {
                            "type": "array",
                            "items": {
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
    # prompt = "Tell me the sum of 1, 2, 3, 4, 5, 6, 7, 8, 9, 10."
    prompt = "桌上有 2 个苹果，四个桃子和 3 本书，一共有几个水果？"
    # prompt = "1+2+3...+99+100"
    # prompt = "1024 乘以 1024 是多少？"   # Tools 里没有定义乘法，会怎样？
    # rompt = "太阳从哪边升起？"           # 不需要算加法，会怎样？

    # 初始对话session
    messages = [
        {"role": "system", "content": "你是一个数学家"},
        {"role": "user", "content": prompt}
    ]
    # 初始对话得到一个回复(回复的是一个按照函数格式解析了用户问题)
    response = get_completion(messages)

    # 把大模型的回复加入到对话历史中
    messages.append(response)

    print("=====GPT回复=====")
    print(response)
    print_json(response)

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
                    "name": "count",
                    "content": str(result)  # 数值 result 必须转成字符串
                }
            )

            # 再次调用大模型
            print("=====最终回复=====")
            print(get_completion(messages).content)

if __name__ == '__main__':
    result()

