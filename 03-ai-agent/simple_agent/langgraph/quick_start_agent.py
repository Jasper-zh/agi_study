from langchain_qwq import ChatQwQ
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """
    两数字相加
    Returns:
        sum of a and b
    """
    return a + b

llm = ChatQwQ(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
    temperature=0,
    streaming=True
)

agent = create_react_agent(llm, [add])

agent.invoke({"input": "1 + 2等于多少呀"})