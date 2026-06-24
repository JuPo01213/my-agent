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
  - return_trace=True 时返回 (final_text, trace: list[dict])，trace 字段是
    **中性 trace**（`{"kind": "llm|tool|final", "step": int, "data": {...}}`），
    由上层模块 wrap 为具体事件契约，**核心层不感知任何上层 schema**。
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
    return_trace: bool = False,
):
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
        return_trace: 若 True，返回 (final_text, trace)。
                     trace 是**中性 trace**，由 frontend 层 wrap 为前端契约，
                     核心层不感知前端 schema。

    Returns:
        - return_trace=False: str（最终答案，与原版一致）
        - return_trace=True:  tuple[str, list[dict]] (final_text, trace)
    """
    if openai_tools is None:
        openai_tools = build_openai_tools_schema()
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    # 中性 trace：纯业务事件，core 完全不知道"前端"是什么
    trace: list[dict[str, Any]] = []

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
        # 兼容推理模型（StepFun step-3.7-flash 等）：content 经常为空，
        # 真实输出在 reasoning_content 字段。final answer 取自此。
        if not reply_content and getattr(response_msg, "reasoning_content", None):
            reply_content = response_msg.reasoning_content
        messages.append(response_msg)

        # 把 LLM 输出记到 trace（content 可能是 thought / reasoning_content）
        if reply_content:
            trace.append({
                "kind": "llm",
                "step": step,
                "data": {"content": reply_content, "has_tool_calls": bool(response_msg.tool_calls)},
            })

        # 没有工具调用 → 返回最终答案
        tool_calls = response_msg.tool_calls
        if not tool_calls:
            final_text = reply_content.strip() or "未得到有效回答。"
            trace.append({"kind": "final", "step": step, "data": {"content": final_text}})
            return (final_text, trace) if return_trace else final_text

        # 处理工具调用
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            # 记录 tool.call（中性事件）
            trace.append({
                "kind": "tool",
                "step": step,
                "data": {"phase": "call", "name": tool_name, "args": tool_args},
            })

            observation = _call_tool(tool_name, tool_args)

            # 记录 tool.observation（中性事件）
            trace.append({
                "kind": "tool",
                "step": step,
                "data": {"phase": "observation", "name": tool_name, "observation": observation},
            })

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": observation,
            })

    timeout_msg = "超过最大步数限制，未得出最终答案。"
    trace.append({"kind": "final", "step": max_steps, "data": {"content": timeout_msg}})
    return (timeout_msg, trace) if return_trace else timeout_msg
