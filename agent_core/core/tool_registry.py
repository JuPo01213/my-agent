"""
agent_core.core.tool_registry - 工具注册表
=========================================

负责：
- 工具注册（@register_tool 装饰器）
- 工具转 OpenAI Function Calling Schema
- 参数校验

**核心原则**：不依赖 LLM 客户端，纯数据层。
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# 工具注册表
# ---------------------------------------------------------------------------
# 全局工具字典：{工具名: {description, params, required, func}}
# 任何装饰了 @register_tool 的函数都会注册到这里。

TOOLS: dict[str, dict[str, Any]] = {}


def register_tool(
    name: str,
    description: str,
    params: dict[str, dict[str, Any]] | None = None,
    required: list[str] | None = None,
):
    """
    注册一个工具，供 LLM 在 ReAct 循环中调用。

    Args:
        name: 工具名称
        description: 工具功能描述
        params: 参数 Schema，格式为 {参数名: {"type": "类型", "description": "描述"}}
        required: 必填参数列表
    """
    if params is None:
        params = {}
    if required is None:
        required = []

    def decorator(func):
        TOOLS[name] = {
            "name": name,
            "description": description,
            "params": params,
            "required": required,
            "func": func,
        }
        return func

    return decorator


def build_openai_tools_schema() -> list[dict[str, Any]]:
    """
    把所有已注册工具转成 OpenAI Function Calling Schema 格式。
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        param_name: {
                            "type": param_spec.get("type", "string"),
                            "description": param_spec.get("description", ""),
                        }
                        for param_name, param_spec in tool.get("params", {}).items()
                    },
                    "required": tool.get("required", []),
                },
            },
        }
        for tool in TOOLS.values()
    ]


def validate_tool_args(tool_name: str, args: dict[str, Any]) -> tuple[bool, str]:
    """
    校验工具参数是否合法。
    返回 (是否合法, 错误信息)。
    """
    if tool_name not in TOOLS:
        return False, f"工具 {tool_name} 未注册"

    tool = TOOLS[tool_name]

    # 检查必填参数
    for req_param in tool.get("required", []):
        if req_param not in args:
            return False, f"工具 {tool_name} 缺少必填参数：{req_param}"

    # 检查参数类型
    for param_name, param_value in args.items():
        if param_name not in tool["params"]:
            return False, f"工具 {tool_name} 不支持参数：{param_name}"
        expected_type = tool["params"][param_name].get("type", "string")
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
        }
        if expected_type in type_map and not isinstance(param_value, type_map[expected_type]):
            return False, f"参数 {param_name} 类型错误，期望 {expected_type}，实际 {type(param_value).__name__}"

    return True, ""


# ---------------------------------------------------------------------------
# 内置工具
# ---------------------------------------------------------------------------
# 这里注册 3 个示例工具：calculator / search / get_time
# 实际项目里应替换为真实的搜索 API、数据库连接等。

import re
from datetime import datetime


@register_tool(
    name="calculator",
    description="执行基础数学计算，支持加减乘除和括号。",
    params={
        "expression": {
            "type": "string",
            "description": "要计算的数学表达式，例如 12 * (3 + 4)",
        }
    },
    required=["expression"],
)
def calculator(expression: str) -> str:
    """
    安全的数学表达式求值（仅允许数字和运算符）。
    白名单过滤，避免执行任意代码。
    """
    allowed = re.compile(r"^[0-9+\-*/().\s]+$")
    if not allowed.match(expression):
        return "错误：表达式包含非法字符，仅支持数字和 +-*/(). 运算符。"
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果：{result}"
    except Exception as exc:
        return f"计算失败：{str(exc)}"


@register_tool(
    name="search",
    description="搜索互联网获取最新信息。返回一段摘要。",
    params={
        "query": {
            "type": "string",
            "description": "搜索关键词",
        }
    },
    required=["query"],
)
def search(query: str) -> str:
    """
    占位搜索工具。
    实际项目里这里替换成 Tavily / Exa / Google Serper 等搜索 API。
    """
    return f"[搜索占位] 针对「{query}」的搜索结果：这是模拟返回，请接入真实搜索 API。"


@register_tool(
    name="get_time",
    description="获取当前系统时间。",
    params={},
    required=[],
)
def get_time() -> str:
    """
    返回当前时间字符串。
    """
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
