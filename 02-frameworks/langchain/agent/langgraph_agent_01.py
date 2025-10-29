"""
🎯 项目统一的 Agent 创建函数

使用 LangGraph 底层进行实现，并提供简单的接口
这样既保持了使用的简单性，又保留了底层的灵活性和可控性

核心优势：
1. 简单接口 - 和 langchain 的 create_agent 一样简单
2. 完全可控 - 底层基于 LangGraph，可以随时定制
3. 易于调试 - 每个节点都可以打印日志，容易排查问题
4. 统一管理 - 整个项目使用同一套 Agent 实现

ReAct 流程：
1. 用户输入 → LLM 思考
2. LLM 决定：调用工具 or 给出答案
3. 如果调用工具 → 执行工具 → 返回 LLM 继续思考
4. 如果给出答案 → 结束
"""

from typing import TypedDict, Annotated, Literal, Optional, Sequence
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool, BaseTool
from langchain_core.language_models import BaseChatModel
from config import settings
import requests


# ==================== 示例工具 ====================
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 这里简化处理，实际应调用天气API
    weather_data = {
        "北京": "晴天，温度25℃",
        "上海": "多云，温度28℃",
        "武汉": "小雨，温度22℃",
        "深圳": "晴天，温度30℃"
    }
    return weather_data.get(city, f"{city}的天气信息暂时无法获取")


@tool
def calculator(expression: str) -> str:
    """计算数学表达式，例如: 2+3*4"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


# 工具列表
tools = [get_weather, calculator]


# ==================== 定义状态 ====================
class AgentState(TypedDict):
    """Agent 的状态
    
    messages: 对话历史，使用 add_messages 作为 reducer
              这意味着新消息会追加到列表中，而不是替换
    iterations: 迭代次数，用于限制循环
    """
    messages: Annotated[list, add_messages]
    iterations: int  # 迭代计数器


# ==================== 注释：旧的节点函数已整合到 create_agent 内部 ====================
# 
# 之前的 call_llm, call_tools, should_continue 函数现在都在 create_agent() 内部
# 通过闭包的方式，每个 Agent 都有独立的配置
# 
# 这样的好处：
# 1. 更干净 - 不需要全局变量
# 2. 更灵活 - 每个 Agent 可以有不同的配置
# 3. 更安全 - 避免配置互相干扰


# ==================== 🎯 项目统一的 Agent 创建函数 ====================

def create_agent(
    llm: BaseChatModel,
    tools: Sequence[BaseTool],
    system_prompt: Optional[str] = None,
    max_iterations: int = 10,
    enable_logging: bool = True,
):
    """
    创建一个 ReAct Agent（项目统一接口）
    
    这个函数封装了 LangGraph 的复杂性，提供简单的接口
    内部使用 LangGraph 实现，保留了完全的灵活性和可控性
    
    Args:
        llm: 语言模型实例（如 ChatOpenAI）
        tools: 工具列表
        system_prompt: 系统提示词（可选），用于设定 Agent 的角色和行为
        max_iterations: 最大迭代次数，防止死循环（默认10次）
        enable_logging: 是否启用日志打印（默认True）
        
    Returns:
        编译好的 Agent 图，可以直接调用 invoke()
        
    使用示例:
        >>> from langchain_openai import ChatOpenAI
        >>> from config import settings
        >>> 
        >>> llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY)
        >>> agent = create_agent(llm, [tool1, tool2], system_prompt="你是助手")
        >>> result = agent.invoke({"messages": [("user", "你好")]})
    """
    
    # ========== 节点1: 调用 LLM ==========
    def call_llm_node(state: AgentState) -> AgentState:
        """LLM 节点：调用大模型，决定是否使用工具"""
        if enable_logging:
            print(f"\n[LLM 节点] 第 {state.get('iterations', 0) + 1} 轮思考...")
        
        messages = state["messages"]
        
        # 如果有系统提示词，且消息列表中还没有系统消息，则添加
        if system_prompt and not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=system_prompt)] + messages
        
        # 绑定工具并调用 LLM
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(messages)
        
        if enable_logging:
            if response.content:
                print(f"  LLM 回复: {response.content[:100]}...")
            if response.tool_calls:
                print(f"  需要调用工具: {[tc['name'] for tc in response.tool_calls]}")
        
        return {
            "messages": [response]
        }
    
    # ========== 节点2: 执行工具 ==========
    def call_tools_node(state: AgentState) -> AgentState:
        """工具节点：执行工具调用"""
        if enable_logging:
            print(f"\n[工具节点] 执行工具...")
        
        last_message = state["messages"][-1]
        tools_dict = {t.name: t for t in tools}
        
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            if enable_logging:
                print(f"  执行: {tool_name}({tool_args})")
            
            # 执行工具
            tool = tools_dict[tool_name]
            result = tool.invoke(tool_args)
            
            if enable_logging:
                print(f"  结果: {result}")
            
            # 创建工具消息
            tool_message = ToolMessage(
                content=str(result),
                tool_call_id=tool_id,
                name=tool_name
            )
            tool_messages.append(tool_message)
        
        return {
            "messages": tool_messages,
            "iterations": state.get("iterations", 0) + 1
        }
    
    # ========== 条件判断: 是否继续 ==========
    def should_continue_edge(state: AgentState) -> Literal["tools", "end"]:
        """条件边：判断是否需要继续执行"""
        # 检查是否超过最大迭代次数
        if state.get("iterations", 0) >= max_iterations:
            if enable_logging:
                print(f"\n[条件判断] 达到最大迭代次数 {max_iterations}，停止")
            return "end"
        
        # 检查是否需要调用工具
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            if enable_logging:
                print(f"\n[条件判断] 需要调用工具，继续...")
            return "tools"
        
        if enable_logging:
            print(f"\n[条件判断] 无需调用工具，结束")
        return "end"
    
    # ========== 构建图 ==========
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("llm", call_llm_node)
    workflow.add_node("tools", call_tools_node)
    
    # 设置入口
    workflow.set_entry_point("llm")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "llm",
        should_continue_edge,
        {"tools": "tools", "end": END}
    )
    
    # 添加循环边
    workflow.add_edge("tools", "llm")
    
    # 编译并返回
    return workflow.compile()


# ==================== 可视化工具（可选）====================

def visualize_graph(agent):
    """可视化 Agent 图结构"""
    try:
        from IPython.display import Image, display
        display(Image(agent.get_graph().draw_mermaid_png()))
    except Exception as e:
        print(f"无法可视化图: {e}")
        print("图结构（文本形式）:")
        print(agent.get_graph().draw_ascii())


# ==================== 主程序 - 演示使用 ====================

if __name__ == '__main__':
    print("="*70)
    print("🎯 项目统一 Agent - 简单接口，强大底层")
    print("="*70)
    
    # ========== 准备 LLM 和工具 ==========
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0
    )
    
    my_tools = [get_weather, calculator]
    
    # ========== 创建 Agent（就这么简单！）==========
    print("\n✅ 使用方法1: 最简单（不传 system_prompt）")
    agent = create_agent(llm, my_tools)
    
    print("\n✅ 使用方法2: 带系统提示词和配置")
    agent = create_agent(
        llm,
        my_tools,
        system_prompt="你是一个智能助手，善于使用工具解决问题。",
        max_iterations=5,
        enable_logging=True
    )
    
    print("\n✅ 当前项目中，任何地方都可以这样一行代码创建 Agent！")
    
    # ========== 测试用例 ==========
    test_cases = [
        "北京今天天气怎么样？",
        "计算 (3 + 5) * 2",
        "上海天气如何？如果温度超过25度，计算 30 - 温度值",
    ]
    
    for i, question in enumerate(test_cases, 1):
        print("\n" + "="*70)
        print(f"📝 测试 {i}: {question}")
        print("="*70)
        
        # 调用 agent（和 langchain 的 create_agent 接口一样）
        result = agent.invoke({
            "messages": [("user", question)]
        })

    
    # ========== 演示不同配置 ==========
    print("\n\n" + "="*70)
    print("🔧 演示：不同配置的 Agent")
    print("="*70)
    
    print("\n1️⃣ 安静模式（不打印日志）")
    silent_agent = create_agent(llm, my_tools, enable_logging=False)
    result01 = silent_agent.invoke({"messages": [("user", "北京天气")]})
    print(f"   结果: {result01['messages'][-1].content}")
    
    print("\n2️⃣ 严格模式（最多1次工具调用）")
    strict_agent = create_agent(llm, my_tools, max_iterations=1, enable_logging=False)
    result02 = strict_agent.invoke({"messages": [("user", "上海天气然后计算温度*2")]})
    print(f"   结果: {result02['messages'][-1].content}")
    print(f"   迭代次数: {result02.get('iterations', 0)}")
    
    print("\n3️⃣ 角色定制")
    weather_agent = create_agent(
        llm, 
        [get_weather],
        system_prompt="你是专业的气象播报员，需要按照实际给出天气信息，且回答要专业且友好。",
        enable_logging=False
    )
    result03 = weather_agent.invoke({"messages": [("user", "深圳天气")]})
    print(f"   结果: {result03['messages'][-1].content}")
    
    print("\n\n" + "="*70)
    print("✅ 总结：")
    print("="*70)
    print("1. 接口简单 - 和 langchain.create_agent 一样容易")
    print("2. 功能强大 - 支持 system_prompt、max_iterations、日志等")
    print("3. 完全可控 - 底层是 LangGraph，可以随时定制")
    print("4. 统一管理 - 整个项目都用这个 create_agent")
    print("5. 易于调试 - 每个节点都有日志，容易排查问题")
    print("\n🎉 现在你有了自己的 Agent 创建函数，可以在项目中到处使用！")
    print("="*70)


# ==================== 🎓 设计思想和知识点 ====================
"""
🎯 设计思想：既简单又强大

本文件实现了一个重要的架构模式：
    简单的接口 + 灵活的底层实现

通过 create_agent() 函数，我们：
1. ✅ 对外提供简单接口（和 langchain.create_agent 一样简单）
2. ✅ 底层使用 LangGraph（完全可控、易调试）
3. ✅ 支持自定义配置（system_prompt、max_iterations、日志等）
4. ✅ 统一项目标准（全项目使用同一套 Agent）

═══════════════════════════════════════════════════════════

📚 核心知识点：

1. 闭包的巧妙应用
   - create_agent() 返回的节点函数是闭包
   - 它们捕获了外部的 llm, tools, system_prompt 等参数
   - 这样每次创建的 Agent 都有独立的配置

2. 状态管理
   - AgentState: 定义状态结构
   - Annotated[list, add_messages]: 使用 Reducer 自动合并消息
   - iterations: 自定义字段，用于循环控制

3. 节点设计
   - call_llm_node: 调用 LLM，支持 system_prompt
   - call_tools_node: 执行工具调用
   - 都是纯函数，易于测试和调试

4. 条件边
   - should_continue_edge: 判断是否继续
   - 检查迭代次数 + 工具调用
   - 实现循环控制和退出逻辑

5. 可配置性
   - system_prompt: 自定义 Agent 角色
   - max_iterations: 防止死循环
   - enable_logging: 开发时打日志，生产时关闭

═══════════════════════════════════════════════════════════

🆚 三种方式对比：

方式1: langchain.create_agent
   接口: agent = create_agent(llm, tools)
   优点: 官方实现，简单
   缺点: 黑盒，不灵活，难调试

方式2: 本文件的 create_agent
   接口: agent = create_agent(llm, tools, system_prompt="...")
   优点: 简单接口 + 可控底层 + 易调试
   缺点: 需要维护代码（但值得！）

方式3: 直接用 LangGraph 手写
   接口: 手动定义状态、节点、边...
   优点: 完全自由
   缺点: 每次都要写一堆代码，不适合项目统一使用

💡 推荐策略：
- 项目中使用方式2（本文件）
- 开始简单，需要时再定制
- 统一接口，灵活底层

═══════════════════════════════════════════════════════════

🚀 如何在项目中使用：

1. 复制 create_agent 函数到你的项目
2. 根据需求调整默认配置
3. 在整个项目中使用这个统一接口

示例项目结构：
    your_project/
    ├── agent/
    │   ├── __init__.py
    │   └── core.py        # 这个文件的 create_agent
    ├── tools/
    │   ├── weather.py
    │   └── search.py
    └── api/
        └── routes.py      # 使用 create_agent

═══════════════════════════════════════════════════════════

✨ 可扩展性：

未来如果需要添加功能，只需修改 create_agent()：
- 添加记忆节点 → 支持上下文记忆
- 添加验证节点 → 支持权限控制
- 添加监控 → 自动上报到监控系统
- 添加缓存 → 相同问题直接返回缓存

所有使用 create_agent 的地方自动获得新功能！

═══════════════════════════════════════════════════════════

🎓 软件工程价值：

这不只是一个技术实现，更体现了优秀的软件设计：
✅ 封装复杂性 - 把 LangGraph 的复杂性隐藏起来
✅ 简化接口 - 提供简单易用的 API
✅ 保留灵活性 - 需要时可以深入定制
✅ 统一标准 - 项目中使用同一套实现

这就是"简单的接口，强大的实现"的最佳实践！
"""

