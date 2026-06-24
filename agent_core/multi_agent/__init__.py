"""
agent_core.multi_agent - 多 Agent 协作层
=======================================

**职责**：多 Agent 场景的统一 API 层。

公开 API（Supervisor 唯一入口）：
- agent_api.run_react_agent: 跑一个独立的 ReAct Agent
- agent_api.filter_tools_schema: 工具过滤
- agent_api.call_tool_safe: 工具调用

**设计原则**：
- 不依赖 dashboard、不依赖前端
- core/ 负责"怎么做"，multi_agent/ 负责"怎么配置"
"""
from .agent_api import (
    DEFAULT_AGENT_SYSTEM_PROMPT,
    DEFAULT_MAX_STEPS,
    call_tool_safe,
    filter_tools_schema,
    run_react_agent,
)

__all__ = [
    "run_react_agent",
    "filter_tools_schema",
    "call_tool_safe",
    "DEFAULT_AGENT_SYSTEM_PROMPT",
    "DEFAULT_MAX_STEPS",
]
