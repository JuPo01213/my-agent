"""
LangGraph 官方 Supervisor 模式（成熟代码）
==========================================
来源：https://langchain-ai.github.io/langgraph/agents/multi-agent/

这是一个"旅游助手"的例子：
- flight_assistant：负责订机票
- hotel_assistant：负责订酒店
- supervisor：中央调度员，决定派哪个

运行方式：
    pip install langgraph langgraph-supervisor langchain-openai
    python agent_core/langgraph_official.py
"""

# ---------------------------------------------------------------------------
# 1. 定义工具（和你的 react_agent.py 一样，用装饰器注册）
# ---------------------------------------------------------------------------

def book_hotel(hotel_name: str):
    """订酒店"""
    return f"Successfully booked a stay at {hotel_name}."


def book_flight(from_airport: str, to_airport: str):
    """订机票"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."


# ---------------------------------------------------------------------------
# 2. 创建专业 Agent（每个 Agent 只做一件事）
# ---------------------------------------------------------------------------

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

# 机票 Agent
flight_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[book_flight],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

# 酒店 Agent
hotel_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[book_hotel],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)


# ---------------------------------------------------------------------------
# 3. 创建 Supervisor（中央调度员）
# ---------------------------------------------------------------------------

supervisor = create_supervisor(
    agents=[flight_assistant, hotel_assistant],
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "You manage a hotel booking assistant and a"
        "flight booking assistant. Assign work to them."
    )
).compile()


# ---------------------------------------------------------------------------
# 4. 运行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  LangGraph Supervisor 多 Agent 示例")
    print("=" * 60)

    user_input = "book a flight from BOS to JFK and a stay at McKittrick Hotel"

    print(f"\n用户输入：{user_input}\n")

    for chunk in supervisor.stream({
        "messages": [
            {
                "role": "user",
                "content": user_input
            }
        ]
    }):
        print(chunk)
        print("\n")
