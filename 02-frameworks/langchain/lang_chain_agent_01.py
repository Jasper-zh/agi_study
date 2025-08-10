from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
import requests
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import JsonOutputToolsParser
from langchain import hub
from langchain.prompts import PromptTemplate
import json

# 下载一个现有的 Prompt 模板
prompt = hub.pull("hwchase17/react")
from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())
amap_key = "986f275457d96f16ec8cba3f12e3eaba"


@tool
def get_adCode(address: str) -> str:
    "根据地址文本，查出adcode"
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
    # print(prompt)
    # prompt ="""
    # 尽你所能回答以下问题。您可以使用以下工具:
    #
    # {tools}
    #
    # 使用以下格式:
    #
    # Question: 您必须回答的输入问题
    # Thought: 你应该时刻思考接下来要做什么
    # Action: 应该采取的行动，选择以下工具之一[{tool_names}]
    # Action Input: 行动的输入
    # Observation: 行动的结果
    # ...(这个思考/动作/动作输入/观察过程可以重复多次)
    # Thought: 现在我知道了最终答案
    # Final Answer: 对原始输入问题的最终回答
    #
    # 开始!
    #
    # Question: {input}
    # Thought: {agent_scratchpad}
    # """
    prompt = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}
    """
    promptTemplate = PromptTemplate.from_template(prompt)
    print(promptTemplate)
    tools = [get_adCode, get_weather]
    # 带有分支的 LCEL
    llm = ChatOpenAI(temperature=0)
    agent = create_react_agent(llm, tools, promptTemplate)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    result = agent_executor.invoke({"input": "武汉天气怎么样"})
    print(result)