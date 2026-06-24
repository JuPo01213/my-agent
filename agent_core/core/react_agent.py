"""
agent_core.core.react_agent - 纯 ReAct 循环
===========================================

**核心原则**：
- 只做一件事：跑一次 ReAct 循环，返回最终答案
- **不暴露 on_event**（这是给前端用的，不应污染核心）
- **不暴露 stop_event**（同上）
- **不实现事件协议**（thought/action/observation/final 这些类型）

接口：
- run_loop(user_input, client, model, system_prompt, openai_tools) -> str
"""
from __future__ import annotations

import json
from typing import Any

from .tool_registry import TOOLS, build_openai_tools_schema, validate_tool_args


DEFAULT_SYSTEM_PROMPT = """\
你是一个智能助手，使用 ReAct（推理+行动）模式解决用户问题。
你可以使用提供的工具来获取信息或完成计算，当你获得足够信息后，请直接给出最终答案。

规则：
1. 仔细分析用户问题，思考需要使用什么工具来获取必要的信息。
2. 每次可以调用一个工具，系统会返回工具执行结果。
3. 根据工具返回的结果继续思考，如果信息足够就给出最终答案，否则继续调用工具。
4. 如果工具报错，请分析错误原因并修正参数后重试。
5. 不要编造工具返回的结果，所有信息必须来自工具返回或你确定的常识。
6. 最终答案请清晰、准确、直接地回答用户问题。
"""

MAX_STEPS = 10


def _call_tool(tool_name: str, tool_args: dict[str, Any]) -> str:
    """
    内部工具调用：执行工具并捕获异常。
    错误以字符串形式返回，让 LLM 自我修正。
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


def run_loop(
    user_input: str,
    client: Any,
    model: str,
    system_prompt: str | None = None,
    openai_tools: list[dict[str, Any]] | None = None,
    max_steps: int = MAX_STEPS,
) -> str:
    """
    执行一次完整的 ReAct 循环，返回最终答案。

    **这是核心 API**，所有更上层的封装（multi_agent.api）都基于这个函数。

    Args:
        user_input: 用户输入的问题
        client: LLM 客户端（OpenAI 兼容协议）
        model: 模型名称
        system_prompt: 系统提示，None 表示使用默认
        openai_tools: OpenAI Function Calling Schema，None 表示使用所有已注册工具
        max_steps: 最大步数限制，防止无限循环

    Returns:
        最终答案字符串
    """
    if openai_tools is None:
        openai_tools = build_openai_tools_schema()
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    for step in range(1, max_steps + 1):
        # 调用大模型
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            tools=openai_tools,
            tool_choice="auto",
        )
        response_msg = response.choices[0].message
        reply_content = response_msg.content or ""
        messages.append(response_msg)

        # 没有工具调用 → 返回最终答案
        tool_calls = response_msg.tool_calls
        if not tool_calls:
            return reply_content.strip() or "未得到有效回答。"

        # 处理工具调用
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            observation = _call_tool(tool_name, tool_args)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": observation,
            })

    return "超过最大步数限制，未得出最终答案。"
