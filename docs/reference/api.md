# API 速查

本文档提供 my-agent 核心 API 的快速参考。

## 核心层 API

### run_loop

```python
from agent_core.core import run_loop

result = run_loop(
    user_input="用户输入",
    client=client,
    model="step-3.7-flash",
    system_prompt="系统提示",
    openai_tools=[...],
    max_steps=10
)
```

### 工具注册表

```python
from agent_core.core import TOOLS, register_tool, build_openai_tools_schema

# 查看已注册工具
print(TOOLS)

# 注册新工具
@register_tool("my_tool")
def my_tool(arg: str) -> str:
    """工具描述"""
    return f"结果: {arg}"

# 构建 OpenAI Schema
schema = build_openai_tools_schema()
```

## 多 Agent 层 API

### run_react_agent

```python
from agent_core.multi_agent import run_react_agent

result = run_react_agent(
    user_input="用户输入",
    client=client,
    model="step-3.7-flash",
    tools=["calculator", "search"],
    system_prompt="系统提示",
    max_steps=10
)
```

### 关系引擎

```python
from agent_core.multi_agent import RelationshipEngine, Blackboard, Command

# 从 YAML 加载
engine = RelationshipEngine.from_yaml("config/relationships.yaml")

# 或手动构建
bb = Blackboard()
cmd = Command.goto("agent_id")
```

## 事件 API

```python
from agent_core.frontend.events import EVENT_SCHEMAS

# 事件类型
# - user.input
# - agent.activate
# - llm.thought
# - tool.call / tool.observation
# - llm.final
# - run.done
```
