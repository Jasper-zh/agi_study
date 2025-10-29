"""
⚠️ 这个文件展示的是 Self-Ask with Search Agent 模式（已过时）

什么是 Self-Ask with Search？
- 让 LLM 把复杂问题分解成多个子问题
- 通过搜索引擎回答每个子问题
- 最后综合得出答案

例如："吴京的老婆主持过哪些综艺节目？"
→ 子问题1: 吴京的老婆是谁？→ 搜索 → 谢楠
→ 子问题2: 谢楠主持过哪些综艺？→ 搜索 → 《快乐大本营》等

为什么这个代码过时了？
1. ❌ create_self_ask_with_search_agent 在 LangChain 1.0 中已废弃
2. ❌ AgentExecutor 已废弃
3. ❌ hub.pull 已移除
4. ❌ 需要付费的 SerpAPI key（每月有限免费额度）
5. ❌ 限制太多：只能用一个名为 'Intermediate Answer' 的工具
6. ❌ 效率低：需要多次搜索，不如直接用一次大模型推理

新版本怎么做？
- 使用 create_agent + 搜索工具，让 LLM 自己决定如何分解问题
- 或者直接用支持联网的 LLM（如 GPT-4 with browsing）

建议：这个文件可以删除，或者作为历史参考保留
"""

# 以下代码在 LangChain 1.0 中已无法运行，仅作为参考
# from langchain.agents import create_self_ask_with_search_agent, AgentExecutor  # 已废弃
# from langchain_core.prompts import PromptTemplate
# from langchain.tools import Tool
# from langchain_openai import ChatOpenAI
# from langchain_community.utilities import SerpAPIWrapper
# from langchain import hub  # 已移除

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# ==================== 旧版 Self-Ask 的 Prompt（仅供参考）====================
# 这个 prompt 展示了 Self-Ask 模式的思维链格式
# 但在新版本中不需要这样手动定义，LLM 可以自己决定如何分解问题

prompt_str_old = """
问题:谁活得更久，穆罕默德·阿里还是艾伦·图灵?
接下来还需要问什么问题吗?
追问:穆罕默德·阿里去世时多大年纪?
中间答案:穆罕默德·阿里去世时享年74岁。
追问:艾伦·图灵去世时多大?
中间答案:图灵去世时41岁。
所以最后的答案是:穆罕默德·阿里
...
问题:{input}
这里需要后续问题吗? {agent_scratchpad}
"""

# ==================== 旧版代码（已无法运行）====================
# if __name__ == '__main__':
#     prompt = hub.pull("hwchase17/self-ask-with-search")  # hub 已移除
#     search = SerpAPIWrapper()  # 需要 SERPAPI_API_KEY
#     tools = [
#         Tool(
#             name="Intermediate Answer",  # 必须是这个名字
#             func=search.run,
#             description="useful for when you need to ask with search.",
#         )
#     ]
#     
#     llm = ChatOpenAI()
#     agent = create_self_ask_with_search_agent(llm, tools, prompt)  # 已废弃
#     agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)  # 已废弃
#     agent_executor.invoke({"input": "吴京的老婆主持过哪些综艺节目？"})


# ==================== 新版替代方案 ====================
"""
如果你需要实现类似的"分解问题+搜索"功能，推荐用新版 create_agent：

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from config import settings

@tool
def search_web(query: str) -> str:
    '''通过搜索引擎搜索信息'''
    # 可以使用：
    # - DuckDuckGo (免费): from langchain_community.tools import DuckDuckGoSearchRun
    # - Tavily (推荐): from langchain_community.tools.tavily_search import TavilySearchResults
    # - Google Search API
    return f"搜索结果: {query}"

llm = ChatOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

# LLM 会自动决定如何分解问题和何时搜索
agent = create_agent(
    llm, 
    [search_web],
    system_prompt="你是一个助手，善于分解复杂问题并通过搜索获取信息。"
)

result = agent.invoke({
    "messages": [("user", "吴京的老婆主持过哪些综艺节目？")]
})

优势：
✅ 不需要特殊的 prompt 格式
✅ LLM 自己决定如何分解问题
✅ 可以使用多个工具
✅ 使用 Function Calling，更准确
"""

if __name__ == '__main__':
    print(__doc__)
    print("\n" + "="*60)
    print("这个文件展示的 Self-Ask Agent 模式已过时")
    print("请参考上面的新版替代方案")
    print("="*60)