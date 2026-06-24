"""
agent_core.multi_agent.tool_caller - 工具调用器
==============================================

供 Supervisor 在循环外独立调用工具使用，自动校验参数 + 捕获异常。

**与 core.react_agent 内部实现的区别**：
- core 内部用的是私有 `_call_tool`
- 这里暴露公开 `call_tool_safe`，给 Supervisor 复用
"""
from __future__ import annotations

from typing import Any

from ..core import TOOLS, validate_tool_args


def call_tool_safe(tool_name: str, tool_args: dict[str, Any]) -> str:
    """
    安全调用工具：执行工具并捕获异常。
    错误以字符串形式返回，便于 LLM 自我修正。

    Args:
        tool_name: 工具名
        tool_args: 工具参数字典

    Returns:
        工具执行结果的字符串表示，或错误信息字符串
    """
    if tool_name not in TOOLS:
        return f"错误：未知工具「{tool_name}」。可用工具：{', '.join(TOOLS.keys())}"

    valid, error_msg = validate_tool_args(tool_name, tool_args)
    if not valid:
        return f"参数错误：{error_msg}"

    try:
        tool = TOOLS[tool_name]
        result = tool["func"](**tool_args)
        return str(result)
    except Exception as exc:
        return f"工具执行异常：{str(exc)}"
