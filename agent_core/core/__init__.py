"""
agent_core.core - 智能体核心层
==============================

**职责定位**：项目最底层，只做两件事
  1. 跑一次 ReAct 循环（react_agent.py）
  2. 维护工具注册表（tool_registry.py）

**核心原则**（依据 ADR-002 / ADR-005）：
  - 零业务参数：不接受 dashboard 事件、stop_event、on_event 等 UI 概念
  - 单向依赖：本层不依赖 multi_agent / static / config 中的任何东西
  - 易测试：run_loop 是纯函数，可被 unittest 直接 mock
  - 易演进：未来要加新能力（如持久化、checkpoint），只在本层内部扩展，不破坏公开 API

**公开 API**：
  - run_loop: 跑一次 ReAct 循环，返回最终答案字符串
  - TOOLS: 全局工具注册表（dict）
  - register_tool: 工具注册装饰器
  - build_openai_tools_schema: 工具 → OpenAI Function Calling Schema
  - validate_tool_args: 参数校验（必填 / 类型）

**典型用法**：
  ```python
  from agent_core.core import run_loop, TOOLS, build_openai_tools_schema
  from openai import OpenAI

  client = OpenAI(base_url=..., api_key=...)
  result = run_loop(
      user_input="1+2=?",
      client=client,
      model="step-3.7-flash",
      openai_tools=build_openai_tools_schema(),
  )
  print(result)  # "3"
  ```

**不要做**：
  - 不要在这里加 dashboard 事件协议（属于 UI 层）
  - 不要在这里加多 Agent 协作逻辑（属于 multi_agent 层）
  - 不要在这里加 YAML 加载（属于 multi_agent.relationship）
"""
from .react_agent import run_loop
from .tool_registry import (
    TOOLS,
    build_openai_tools_schema,
    register_tool,
    validate_tool_args,
)

__all__ = [
    "run_loop",
    "TOOLS",
    "register_tool",
    "build_openai_tools_schema",
    "validate_tool_args",
]
