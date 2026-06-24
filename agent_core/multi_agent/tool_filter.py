"""
agent_core.multi_agent.tool_filter - 工具过滤
============================================

根据工具名列表，从全局 TOOLS 中过滤出对应的 OpenAI Function Calling Schema。

**用途**：Supervisor 给子 Agent 配置"能用什么工具"。
"""
from __future__ import annotations

from typing import Any

from ..core import TOOLS


def filter_tools_schema(tools: list[str]) -> list[dict[str, Any]]:
    """
    根据工具名列表，过滤出对应的 OpenAI Function Calling Schema。

    Args:
        tools: 工具名列表，如 ["search", "get_time"]

    Returns:
        OpenAI Function Calling Schema 列表
    """
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": TOOLS[name]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        param_name: {
                            "type": param_spec.get("type", "string"),
                            "description": param_spec.get("description", ""),
                        }
                        for param_name, param_spec in TOOLS[name].get("params", {}).items()
                    },
                    "required": TOOLS[name].get("required", []),
                },
            },
        }
        for name in tools
        if name in TOOLS
    ]
