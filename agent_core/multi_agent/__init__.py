"""
agent_core.multi_agent - 多 Agent 协作层
=======================================

**职责**：多 Agent 场景的统一 API 层。

公开 API（Supervisor 唯一入口）：

- `run_react_agent`：跑一个独立的 ReAct Agent（基础 API）
- `filter_tools_schema` / `call_tool_safe`：工具过滤与调用

**关系驱动 API**（v1.0 新增）：

- `Blackboard`：共享状态
- `Command`：路由原语（goto + update + terminate）
- `KnowledgeSource`：Agent 单元（preconditions + action）
- `ControlShell`：OODA 调度器
- `RelationshipEngine`：YAML 驱动的协作引擎

**设计原则**：

- 不依赖 dashboard、不依赖前端
- core/ 负责"怎么做"，multi_agent/ 负责"怎么配置"
- 关系驱动模式借鉴业界成熟实践（Blackboard / LangGraph Command / CrewAI YAML / SALLMA 目录）
"""
from .agent_api import (
    DEFAULT_AGENT_SYSTEM_PROMPT,
    DEFAULT_MAX_STEPS,
    call_tool_safe,
    filter_tools_schema,
    run_react_agent,
)
from .relationship import (
    Blackboard,
    Command,
    ControlShell,
    KnowledgeSource,
    RelationshipEngine,
)

__all__ = [
    # 基础 ReAct API
    "run_react_agent",
    "filter_tools_schema",
    "call_tool_safe",
    "DEFAULT_AGENT_SYSTEM_PROMPT",
    "DEFAULT_MAX_STEPS",
    # 关系驱动 API
    "Blackboard",
    "Command",
    "KnowledgeSource",
    "ControlShell",
    "RelationshipEngine",
]
