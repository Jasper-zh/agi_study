"""
func_call_example02 -

Author: zhang
Date: 2024/1/31
"""
"""
func_call_example -

Author: zhang
Date: 2024/1/31
"""

# 初始化
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import json
import requests

_ = load_dotenv(find_dotenv())

client = OpenAI()


amap_key = "986f275457d96f16ec8cba3f12e3eaba"


def get_adCode(address):
    url = f"https://restapi.amap.com/v3/geocode/geo?key={amap_key}&address={address}"
    print(url)
    r = requests.get(url)
    result = r.json()
    return result['geocodes'][0]['adcode']

# 地图接口：可以通过关键字和地点经纬度，搜索该地点附近满足关键字的地方
# https://restapi.amap.com/v5/place/around?key=6d672e6194caa3b639fccf2caf06c342&keywords=咖啡厅&location=113.587617,37.862361
def get_weather(adcode):
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?key={amap_key}&city={adcode}"
    print(url)
    r = requests.get(url)
    result = r.json()
    print(result)
    return result

def get_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
        tools=[{  # 用 JSON 描述函数。可以定义多个。由大模型决定调用谁。也可能都不调用
            "type": "function",
            "function": {
                "name": "get_adcode",   # 函数名称
                "description": "根据地址文本获取adcode",  # 函数描述
                "parameters": {        # 函数参数
                    "type": "object",  # 参数类型：对象
                    "properties": {    # 对象属性
                        "address": {
                            "type": "string", # 该属性类型：字符串
                        }
                    }
                }
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather",  # 函数名称
                "description": "根据adcode获取天气",  # 函数描述
                "parameters": {  # 函数参数
                    "type": "object",  # 参数类型：对象
                    "properties": {  # 对象属性
                        "adcode": {
                            "type": "string",  # 该属性类型：字符串
                        }
                    }
                }
            }
        }
        ],
    )
    return response.choices[0].message

def handle(prompt):
    print(f"用户发送：{prompt}")

    messages = [
        {"role": "system", "content": "你是一个向导能结合天气推荐地点"},
        {"role": "user", "content": prompt}
    ]
    response = get_completion(messages)
    messages.append(response)  # 把大模型的回复加入到对话中
    print(f"GPT响应：{response}")

    # 若按照预期响应了tool_calls
    while (response.tool_calls is not None):
        # 1106 版新模型支持一次返回多个函数调用请求，所以要考虑到这种情况
        for i, tool_call in enumerate(response.tool_calls):
            args = json.loads(tool_call.function.arguments)
            print("函数参数：")
            print(args)
            # 如果函数名称是获取地点，则调用get_location_coordinate
            if (tool_call.function.name == "get_adcode"):
                print("调用获取adcode")
                result = get_adCode(args['address'])
            # 如果函数名称是获取地点附近的地方，则调用search_nearby_pois
            elif (tool_call.function.name == "get_weather"):
                print("调用获取天气")
                result = get_weather(args['adcode'])

            print(f"API调用结果: {result}")

            # 对话会话进行填充 函数ID 角色tool name函数名称 函数返回内容
            messages.append({
                "tool_call_id": tool_call.id,  # 用于标识函数调用的 ID
                "role": "tool",
                "name": tool_call.function.name,
                "content": str(result)  # 数值result 必须转成字符串
            })

        # 会话全部发回大模型，并且将结果覆盖给while条件使用的response,触发第二次while循环
        response = get_completion(messages)
        print(f"GPT响应: {response}")
        # 回复最后也加入到会话
        messages.append(response)  # 把大模型的回复加入到对话中
    print(f"应用回复：{response.content}")


if __name__ == '__main__':
    handle("武汉天气怎么样去哪好")
