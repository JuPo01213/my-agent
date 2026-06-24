"""
agent_core.multi_agent.agent_api - 公开 API
===========================================

**Supervisor 唯一需要 import 的模块**。

提供：
- run_react_agent: 多 Agent 场景下的统一 API
- filter_tools_schema: 工具过滤
- call_tool_safe: 工具调用

**这是为多 Agent 协作准备的接口**：
- Supervisor 调用时，可以传入专属的 tools 和 system_prompt
- 让不同的 Agent 拥有不同的能力集合和人设

**与 core.run_loop 的区别**：
- core.run_loop: 接收 openai_tools（OpenAI Schema 格式）
- run_react_agent: 接收 tools（工具名列表，更高层抽象）
"""
from __future__ import annotations

from typing import Any

from ..core import build_openai_tools_schema, run_loop
from .tool_caller import call_tool_safe
from .tool_filter import filter_tools_schema

# 默认系统提示（多 Agent 场景的通用基线）
DEFAULT_AGENT_SYSTEM_PROMPT = """\
你是一个专业的智能助手，使用 ReAct（推理+行动）模式解决用户问题。
你可以使用提供的工具来获取信息或完成计算，当你获得足够信息后，请直接给出最终答案。

规则：
1. 仔细分析用户问题，思考需要使用什么工具来获取必要的信息。
2. 每次可以调用一个工具，系统会返回工具执行结果。
3. 根据工具返回的结果继续思考，如果信息足够就给出最终答案，否则继续调用工具。
4. 如果工具报错，请分析错误原因并修正参数后重试。
5. 不要编造工具返回的结果，所有信息必须来自工具返回或你确定的常识。
6. 最终答案请清晰、准确、直接地回答用户问题。
"""

DEFAULT_MAX_STEPS = 10


def run_react_agent(
    user_input: str,
    client: Any,
    model: str,
    tools: list[str] | None = None,
    system_prompt: str | None = None,
    max_steps: int = DEFAULT_MAX_STEPS,
) -> str:
    """
    运行一个独立的 ReAct Agent，返回最终答案。

    **这是多 Agent 协作的统一 API**。Supervisor 给不同的子 Agent 传不同的
    `tools` 和 `system_prompt`，就能让每个 Agent 拥有不同的能力集合和人设。

    Args:
        user_input: 用户输入的问题
        client: LLM 客户端（OpenAI 兼容协议）
        model: 模型名称
        tools: 此 Agent 可用的工具名列表，None 表示使用所有已注册工具
        system_prompt: 自定义系统提示，None 表示使用默认
        max_steps: 最大步数限制

    Returns:
        最终答案字符串
    """
    # 工具名列表 → OpenAI Schema
    if tools is None:
        openai_tools = build_openai_tools_schema()
    else:
        openai_tools = filter_tools_schema(tools)

    # 系统提示默认值
    if system_prompt is None:
        system_prompt = DEFAULT_AGENT_SYSTEM_PROMPT

    # 调用核心循环
    return run_loop(
        user_input=user_input,
        client=client,
        model=model,
        system_prompt=system_prompt,
        openai_tools=openai_tools,
        max_steps=max_steps,
    )


__all__ = [
    "run_react_agent",
    "filter_tools_schema",
    "call_tool_safe",
    "DEFAULT_AGENT_SYSTEM_PROMPT",
    "DEFAULT_MAX_STEPS",
]
