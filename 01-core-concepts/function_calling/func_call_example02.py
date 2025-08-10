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
import os
import json
import requests

_ = load_dotenv(find_dotenv())

client = OpenAI()

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



amap_key = "6d672e6194caa3b639fccf2caf06c342"

# 地图接口：可以通过关键字和城市名称，搜索地点列表
# https://restapi.amap.com/v5/place/text?key=6d672e6194caa3b639fccf2caf06c342&keywords=咖啡厅&region=武汉
def get_location_coordinate(location, city):
    url = f"https://restapi.amap.com/v5/place/text?key={amap_key}&keywords={location}&region={city}"
    print(url)
    r = requests.get(url)
    result = r.json()
    if "pois" in result and result["pois"]:
        return result["pois"][0]
    return None

# 地图接口：可以通过关键字和地点经纬度，搜索该地点附近满足关键字的地方
# https://restapi.amap.com/v5/place/around?key=6d672e6194caa3b639fccf2caf06c342&keywords=咖啡厅&location=113.587617,37.862361
def search_nearby_pois(longitude, latitude, keyword):
    url = f"https://restapi.amap.com/v5/place/around?key={amap_key}&keywords={keyword}&location={longitude},{latitude}"
    print(url)
    r = requests.get(url)
    result = r.json()
    ans = ""
    if "pois" in result and result["pois"]:
        for i in range(min(3, len(result["pois"]))):
            name = result["pois"][i]["name"]
            address = result["pois"][i]["address"]
            distance = result["pois"][i]["distance"]
            ans += f"{name}\n{address}\n距离：{distance}米\n\n"
    return ans

def get_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,  # 模型输出的随机性，0 表示随机性最小
        seed=1024,      # 随机种子保持不变，temperature 和 prompt 不变的情况下，输出就会不变
        tool_choice="auto",  # 默认值，由 GPT 自主决定返回 function call 还是返回文字回复。也可以强制要求必须调用指定的函数，详见官方文档
        tools=[{
            "type": "function",
            "function": {
                "name": "get_location_coordinate",
                "description": "根据POI名称，获得POI的经纬度坐标",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "POI名称，必须是中文",
                        },
                        "city": {
                            "type": "string",
                            "description": "POI所在的城市名，必须是中文",
                        }
                    },
                    "required": ["location", "city"],
                }
            }
        },
            {
            "type": "function",
            "function": {
                "name": "search_nearby_pois",
                "description": "搜索给定坐标附近的poi",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "longitude": {
                            "type": "string",
                            "description": "中心点的经度",
                        },
                        "latitude": {
                            "type": "string",
                            "description": "中心点的纬度",
                        },
                        "keyword": {
                            "type": "string",
                            "description": "目标poi的关键字",
                        }
                    },
                    "required": ["longitude", "latitude", "keyword"],
                }
            }
        }],
    )
    return response.choices[0].message

def result():
    prompt = "我想在北京五道口附近喝咖啡，给我推荐几个"
    # prompt = "我到北京出差，给我推荐三里屯的酒店，和五道口附近的咖啡"
    print(f"用户发送：{prompt}")

    messages = [
        {"role": "system", "content": "你是一个地图通，你可以找到任何地址。"},
        {"role": "user", "content": prompt}
    ]
    response = get_completion(messages)
    messages.append(response)  # 把大模型的回复加入到对话中
    print("=====GPT回复=====")
    print_json(response)

    # 若按照预期响应了tool_calls
    while (response.tool_calls is not None):
        # 1106 版新模型支持一次返回多个函数调用请求，所以要考虑到这种情况
        for i, tool_call in enumerate(response.tool_calls):
            args = json.loads(tool_call.function.arguments)
            print("函数参数展开：")
            print_json(args)
            # 如果函数名称是获取地点，则调用get_location_coordinate
            if (tool_call.function.name == "get_location_coordinate"):
                print("Call: get_location_coordinate")
                result = get_location_coordinate(**args)
            # 如果函数名称是获取地点附近的地方，则调用search_nearby_pois
            elif (tool_call.function.name == "search_nearby_pois"):
                print("Call: search_nearby_pois")
                result = search_nearby_pois(**args)

            print("=====函数返回=====")
            print_json(result)

            # 对话会话进行填充 函数ID 角色tool name函数名称 函数返回内容
            messages.append({
                "tool_call_id": tool_call.id,  # 用于标识函数调用的 ID
                "role": "tool",
                "name": tool_call.function.name,
                "content": str(result)  # 数值result 必须转成字符串
            })

        # 会话全部发回大模型，并且将结果覆盖给while条件使用的response,触发第二次while循环
        response = get_completion(messages)
        print("=====返回函数结果给大模型，得到回复：=====")
        print(response)

        # 回复最后也加入到会话
        messages.append(response)  # 把大模型的回复加入到对话中
    print("=====最终模型返回结果不再是函数：=====")
    print(response.content)


if __name__ == '__main__':
    result()

