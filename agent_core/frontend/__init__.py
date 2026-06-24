"""
agent_core.frontend - 前端契约层
==================================

**职责定位**：定义核心层与前端之间的数据契约，**与任何具体前端框架（Vue/React）
或传输协议（HTTP/SSE/WS）解耦**。

**为什么单独成层**（依据 ADR-013）：
  - 核心层（core / multi_agent）只做"业务"，不应知道"有前端"
  - 前端层（agent_core/frontend/）只做"数据形态"，不应绑死 Vue/HTML
  - 任何上层（HTTP/SSE/WS/CLI 测试）都能消费同一份契约

**模块清单**：
  - events: 事件 Schema 定义 + 工厂函数 + 类型常量
  - （预留）stream: 未来 SSE/WS 适配器入口

**调用约定**：
  - 核心层通过 `on_event(dict)` 推送事件，前端层只负责"形状"
  - 事件字段稳定，**所有字段都是 snake_case + ISO-8601 时间戳**
  - 新增事件类型请同步更新 ADR
"""
from . import events, bus, adapter
from .events import (
    EVENT_TYPES,
    USER_INPUT, AGENT_ACTIVATE, LLM_THOUGHT,
    TOOL_CALL, TOOL_OBSERVATION, LLM_FINAL,
    RUN_DONE, AGENT_ERROR,
    make_user_input,
    make_agent_activate,
    make_llm_thought,
    make_tool_call,
    make_tool_observation,
    make_llm_final,
    make_run_done,
    make_agent_error,
)
from .bus import EventBus
from .adapter import wrap_trace_to_events, aggregate_run_events

__all__ = [
    "events",
    "bus",
    "adapter",
    "EventBus",
    "EVENT_TYPES",
    "USER_INPUT", "AGENT_ACTIVATE", "LLM_THOUGHT",
    "TOOL_CALL", "TOOL_OBSERVATION", "LLM_FINAL",
    "RUN_DONE", "AGENT_ERROR",
    "make_user_input",
    "make_agent_activate",
    "make_llm_thought",
    "make_tool_call",
    "make_tool_observation",
    "make_llm_final",
    "make_run_done",
    "make_agent_error",
    "wrap_trace_to_events",
    "aggregate_run_events",
]
