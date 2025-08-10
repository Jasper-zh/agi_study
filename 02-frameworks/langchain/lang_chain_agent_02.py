from langchain.agents import create_self_ask_with_search_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langchain import hub


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

prompt_str = """
问题:谁活得更久，穆罕默德·阿里还是艾伦·图灵?
接下来还需要问什么问题吗?
追问:穆罕默德·阿里去世时多大年纪?
中间答案:穆罕默德·阿里去世时享年74岁。
追问:艾伦·图灵去世时多大?
中间答案:图灵去世时41岁。
所以最后的答案是:穆罕默德·阿里

问:craigslist的创始人是什么时候出生的?
接下来还需要问什么问题吗?
追问:谁是craigslist的创始人?
中级答案:Craigslist是由克雷格·纽马克创立的。
追问:克雷格·纽马克是何时出生的?
中间答案:克雷格·纽马克出生于1952年12月6日。
所以最后的答案是:1952年12月6日

问题:谁是乔治·华盛顿的外祖父?
接下来还需要问什么问题吗?
追问:谁是乔治·华盛顿的母亲?
中间答案:乔治·华盛顿的母亲是玛丽·鲍尔·华盛顿。
追问:玛丽·鲍尔·华盛顿的父亲是谁?
中间答案:玛丽·鲍尔·华盛顿的父亲是约瑟夫·鲍尔。
所以最后的答案是:约瑟夫·鲍尔

问:《大白鲨》和《皇家赌场》的导演都来自同一个国家吗?
接下来还需要问什么问题吗?
追问:《大白鲨》的导演是谁?
中级答案:《大白鲨》的导演是史蒂文·斯皮尔伯格。
追问:史蒂文·斯皮尔伯格是哪里人?
中间答案:美国。
追问:《皇家赌场》的导演是谁?
中级答案:《皇家赌场》的导演是马丁·坎贝尔。
追问:马丁·坎贝尔是哪里人?
中间答案:新西兰。
所以最后的答案是:不

问题:{input}
这里需要后续问题吗? {agent_scratchpad}
"""

if __name__ == '__main__':
    # prompt = PromptTemplate.from_template(prompt_str)
    prompt = hub.pull("hwchase17/self-ask-with-search")
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name="Intermediate Answer",
            func=search.run,
            description="useful for when you need to ask with search.",
        )
    ]

    # self_ask_with_search_agent 只能传一个名为 'Intermediate Answer' 的 tool
    llm = ChatOpenAI()
    agent = create_self_ask_with_search_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    agent_executor.invoke({"input": "吴京的老婆主持过哪些综艺节目？"})