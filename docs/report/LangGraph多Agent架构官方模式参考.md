# LangGraph 多 Agent 架构官方模式参考

> **来源**：[LangGraph Multi-Agent 官方文档](https://langchain-ai.github.io/langgraph/agents/multi-agent/)
> **日期**：2026-06-24

---

## 一、两种核心多 Agent 架构模式

### 1. Supervisor（主管模式）

**架构图**：
```
        ┌─────────────────┐
        │    Supervisor   │
        │   (中央调度员)   │
        │                  │
        │ 分析任务 → 派给   │
        │  Worker Agent   │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│Worker A│  │Worker B│  │Worker C│
│ (订机票)│  │ (订酒店)│  │  ...   │
└────────┘  └────────┘  └────────┘
```

**特点**：
- 中央 Supervisor 统一调度，所有决策经过它
- 适合任务明确、需要集中控制的场景
- Supervisor 不做具体工作，只负责分配

**官方代码示例**（来源：[langgraph-supervisor](https://github.com/langchain-ai/langgraph-supervisor-py)）：

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

# 1. 定义工具
def book_hotel(hotel_name: str):
    """订酒店"""
    return f"Successfully booked a stay at {hotel_name}."

def book_flight(from_airport: str, to_airport: str):
    """订机票"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."

# 2. 创建专业 Agent
flight_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[book_flight],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

hotel_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[book_hotel],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)

# 3. 创建 Supervisor
supervisor = create_supervisor(
    agents=[flight_assistant, hotel_assistant],
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "You manage a hotel booking assistant and a"
        "flight booking assistant. Assign work to them."
    )
).compile()

# 4. 运行
for chunk in supervisor.stream({
    "messages": [{
        "role": "user",
        "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
    }]
}):
    print(chunk)
```

---

### 2. Swarm（蜂群模式）

**架构图**：
```
┌──────────────────────────────────────┐
│              Agent A                │
│   (可以主动转交给其他 Agent)         │
│                                      │
│   ┌──────────┐                      │
│   │transfer_to│ ────────────────────┼──→ Agent B
│   │  _bob()   │                     │
│   └──────────┘                     │
│                                      │
│   ┌──────────┐                      │
│   │transfer_to│ ────────────────────┼──→ Agent C
│   │  _carol() │                     │
│   └──────────┘                      │
└──────────────────────────────────────┘
         ▲                    │
         │                    │
         └────────────────────┘
            Agent B 可以主动转交给 Agent A
```

**特点**：
- Agent 之间可以**自由转交**任务
- 不需要中央调度，分布式决策
- 适合开放性任务、需要灵活协作的场景

**官方代码示例**（来源：[langgraph-swarm](https://github.com/langchain-ai/langgraph-swarm-py)）：

```python
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_swarm, create_handoff_tool

# 1. 创建转交工具
transfer_to_bob = create_handoff_tool(
    agent_name="Bob",
    description="Transfer to Bob for additional help"
)

transfer_to_alice = create_handoff_tool(
    agent_name="Alice",
    description="Transfer to Alice for additional help"
)

# 2. 创建 Agent，每个 Agent 都有转交工具
alice = create_react_agent(
    model="openai:gpt-4o",
    tools=[transfer_to_bob],
    prompt="You are Alice",
    name="Alice"
)

bob = create_react_agent(
    model="openai:gpt-4o",
    tools=[transfer_to_alice],
    prompt="You are Bob",
    name="Bob"
)

# 3. 创建 Swarm
swarm = create_swarm(
    agents=[alice, bob],
    default_active_agent="Alice"
).compile()

# 4. 运行
result = swarm.invoke({
    "messages": [{"role": "user", "content": "I'd like to talk to Bob"}]
})
```

---

## 二、两种条件边实现方式

### 1. Handoffs（基于工具的转交）

**概念**：Agent 通过调用工具来触发转交，工具返回一个 `Command` 对象。

```python
from langgraph.types import Command

@tool
def transfer_to_specialist() -> Command:
    """转交给专家 Agent"""
    return Command(
        update={
            "messages": [...],
            "current_step": "specialist"  # 触发行为变化
        }
    )
```

**适用场景**：
- 需要强制顺序约束
- Agent 需要直接与用户对话
- 多阶段对话流程

### 2. 条件边（基于状态的路由）

**概念**：图根据当前状态（`state`）决定下一步走哪条边。

```python
def router(state) -> str:
    """根据状态决定下一步"""
    if state.get("needs_search"):
        return "search_agent"
    elif state.get("needs_code"):
        return "code_agent"
    else:
        return END

graph.add_conditional_edges(
    "supervisor",
    router,
    {
        "search_agent": "search_agent",
        "code_agent": "code_agent"
    }
)
```

---

## 三、分层架构（Hierarchical）

**概念**：多个层级的 Supervisor，层层管理。

```
┌─────────────────────────────────┐
│    Top-Level Supervisor        │
│    (顶层主管)                   │
└───────────────┬─────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌─────────┐           ┌─────────┐
│Research │           │ Writing  │
│ Team   │           │  Team   │
│Supervisor│         │Supervisor│
└────┬────┘           └────┬────┘
     │                     │
     ▼                     ▼
┌─────────┐           ┌─────────┐
│ Search  │           │ Writer  │
│ Agent   │           │ Agent   │
└─────────┘           └─────────┘
```

**代码示例**：

```python
# 创建底层团队
research_team = create_supervisor(
    agents=[research_agent, math_agent],
    model=llm,
).compile(name="research_team")

writing_team = create_supervisor(
    agents=[writing_agent, publishing_agent],
    model=llm,
).compile(name="writing_team")

# 创建顶层主管
top_supervisor = create_supervisor(
    agents=[research_team, writing_team],
    model=llm,
    prompt="""你管理两个团队：
    - research_team: 研究团队
    - writing_team: 写作团队
    根据任务决定调用哪个团队。"""
).compile()
```

---

## 四、成熟案例参考

### 案例 1：Research + Writing 团队

**来源**：[LangGraph 官方教程](https://langchain-ai.github.io/langgraph/agents/multi-agent/)

```python
# 研究 Agent：搜索 + 网页抓取
research_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=[tavily_search, scrape_webpage],
    prompt="You are a world class researcher with web search access."
)

# 写作 Agent：写报告
writing_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=[file_write],
    prompt="You are an expert technical writer."
)

# Supervisor 调度
supervisor = create_supervisor(
    agents=[research_agent, writing_agent],
    model=ChatOpenAI(model="gpt-4o"),
    prompt="You coordinate research and writing agents."
).compile()
```

### 案例 2：Customer Support 客服系统

**来源**：[LangChain Handoffs 教程](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)

```python
@tool
def transfer_to_specialist() -> Command:
    """转交给专员"""
    return Command(
        update={
            "messages": [...],
            "current_step": "specialist"
        }
    )

# 客服 Agent
customer_support = create_react_agent(
    model="openai:gpt-4o",
    tools=[transfer_to_specialist, record_issue_type],
    prompt="You are a customer support agent."
)

# 专员 Agent
specialist = create_react_agent(
    model="openai:gpt-4o",
    tools=[provide_solution, escalate_to_human],
    prompt="You are a specialist agent."
)
```

---

## 五、模式选择指南

| 场景 | 推荐模式 | 原因 |
|------|----------|------|
| 任务明确、需要集中控制 | **Supervisor** | 中央调度，简单直接 |
| 开放性任务、需要灵活协作 | **Swarm** | 分布式、灵活 |
| 大型复杂任务、需要分层管理 | **Hierarchical** | 层层分解、易于扩展 |
| 需要严格顺序约束 | **Handoffs** | 状态驱动、强制顺序 |

---

## 六、关键设计原则

1. **每个 Agent 只做一件事**：保持 Agent 职责单一
2. **搜索优先**：路由决策时优先搜索，不依赖 LLM 记忆
3. **消息传递要清晰**：Agent 之间传递的消息要明确
4. **状态要持久化**：使用 checkpointer 保存对话状态
5. **错误处理**：考虑 Agent 执行失败的情况

---

## 七、参考资料

- [LangGraph Multi-Agent 官方文档](https://langchain-ai.github.io/langgraph/agents/multi-agent/)
- [langgraph-supervisor PyPI](https://pypi.org/project/langgraph-supervisor/)
- [langgraph-swarm PyPI](https://pypi.org/project/langgraph-swarm/)
- [LangChain Handoffs 文档](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)
