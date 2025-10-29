# from langchain.agents import create_react_agent, AgentExecutor
# from langgraph.prebuilt import create_react_agent

# 最新的创建Agent的方式是langchain的create_agent提供了中间件能力更加灵活
from langchain.agents import create_agent

import requests
from langchain_openai import ChatOpenAI

# from langchain import hub 迁移到 langchainhub库当中了
# from langchainhub import Client

from langchain_core.tools import tool
# 文本处理相关都转移到langchain_core而不是langchain了
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from config import settings
amap_key = settings.AMAP_API_KEY

# 下载一个现有的 Prompt 模板
# hub = Client()
# prompt = hub.pull("hwchase17/react")

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
    """
    ⚠️ 重要说明：create_agent 的工作原理
    
    1. create_agent 默认使用 OpenAI 的 Function Calling API
       - LLM 直接输出结构化的工具调用（JSON格式）
       - 框架自动调用工具并返回结果
       - 不需要解析文本中的 "Action:" "Observation:" 等格式
    
    2. system_prompt 参数是可选的
       - 不传 system_prompt：完全使用 Function Calling（推荐）
       - 传简单提示：例如 "你是天气助手"（如需角色设定）
       - 传 ReAct 格式：旧方式，会强制 LLM 输出文本，效率低，不推荐
    
    3. 为什么下面注释掉的 ReAct prompt 是多余的？
       - 旧版 LangChain (0.x) 需要通过文本格式让 LLM 输出 Action
       - 新版 LangChain (1.0) 使用 Function Calling，自动处理工具调用
       - ReAct prompt 会干扰 Function Calling，反而降低准确性
    """
    
    # ❌ 旧方式：ReAct 格式 prompt（已过时，不推荐使用）
    # 这种格式只在不支持 Function Calling 的旧模型中需要
    # react_prompt = """
    # Answer the following questions as best you can. You have access to the following tools:
    # {tools}
    # 
    # Use the following format:
    # Question: the input question you must answer
    # Thought: you should always think about what to do
    # Action: the action to take, should be one of [{tool_names}]
    # Action Input: the input to the action
    # Observation: the result of the action
    # ... (this Thought/Action/Action Input/Observation can repeat N times)
    # Thought: I now know the final answer
    # Final Answer: the final answer to the original input question
    # 
    # Begin!
    # Question: {input}
    # Thought:{agent_scratchpad}
    # """
    
    tools = [get_adCode, get_weather]
    llm = ChatOpenAI(
        temperature=0,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL
    )
    
    # ✅ 推荐方式1：不传 system_prompt，完全使用 Function Calling
    agent = create_agent(llm, tools)
    
    # ✅ 推荐方式2：只传简单的角色设定（不是 ReAct 格式）
    # agent = create_agent(
    #     llm, 
    #     tools,
    #     system_prompt="你是一个天气查询助手，帮助用户查询中国各地的天气信息。"
    # )
    
    # 调用 agent
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "武汉今天天气怎么样"}
        ]
    })
    
    # 打印结果
    print("\n" + "="*60)
    print("Agent 执行结果：")
    print("="*60)
    
    # 显示完整的消息历史（包括工具调用过程）
    for i, msg in enumerate(result['messages'], 1):
        print(f"\n[消息 {i}] {msg.__class__.__name__}")
        
        # 打印消息内容
        if hasattr(msg, 'content') and msg.content:
            print(f"内容: {msg.content}")
        
        # 如果有工具调用，显示出来
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                print(f"工具调用: {tool_call['name']}({tool_call['args']})")
    
    print("\n" + "="*60)