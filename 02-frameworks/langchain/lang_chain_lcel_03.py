from langchain_core.tools import tool
import requests
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import JsonOutputToolsParser
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())
amap_key = "986f275457d96f16ec8cba3f12e3eaba"

@tool
def add(first_int: int, second_int: int) -> int:
    "求和"
    return first_int + second_int


@tool
def get_adCode(address: str) -> str:
    "根据地址串，查出adcode"
    url = f"https://restapi.amap.com/v3/geocode/geo?key={amap_key}&address={address}"
    r = requests.get(url)
    result = r.json()
    return result['geocodes'][0]['adcode']

# 地图接口：可以通过关键字和地点经纬度，搜索该地点附近满足关键字的地方
# https://restapi.amap.com/v5/place/around?key=6d672e6194caa3b639fccf2caf06c342&keywords=咖啡厅&location=113.587617,37.862361
@tool
def get_weather(adcode: str) -> object:
    "根据adcode查出天气信息"
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?key={amap_key}&city={adcode}"
    r = requests.get(url)
    result = r.json()
    return result

if __name__ == '__main__':
    tools = [add, get_adCode, get_weather]
    # 带有分支的 LCEL
    llm = ChatOpenAI(temperature=0)
    llm_with_tools = llm.bind_tools(tools) | {
        "functions": JsonOutputToolsParser(),
        "text": StrOutputParser()
    }
    result = llm_with_tools.invoke("桌上两个苹果，盘子有一个，一共多少个")
    print(result)