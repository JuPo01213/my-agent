"""
agent_core.core - 核心层
=======================

最底层的实现，**只做一件事**：跑一次 ReAct 循环 + 工具注册表。

不依赖任何外部 API，不暴露任何 dashboard 相关参数。

公开 API：
- run_loop: 跑一次 ReAct 循环，返回最终答案
- TOOLS: 全局工具注册表
- register_tool: 工具注册装饰器
- build_openai_tools_schema: 工具→OpenAI Schema 转换
- validate_tool_args: 参数校验
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
