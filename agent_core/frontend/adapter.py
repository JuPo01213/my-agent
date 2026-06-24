"""
agent_core.frontend.adapter - 翻译层
======================================

**职责**：把 core / multi_agent 产出的"中性事件"翻译成"前端契约事件"。

**为什么需要翻译层**（依据 ADR-013）：
  - core.run_loop 的 trace 是**业务中性事件**（kind: llm/tool/final）
  - 前端契约（agent_core.frontend.events）有 8 类带 schema 的事件
  - core 不应知道前端 schema，**翻译在这里做**

**核心函数**：
  - wrap_trace_to_events(trace, agent_name, run_id) -> Iterator[dict]
    把一个 Agent 的 trace 翻译成一串前端事件
  - aggregate_run_events(agents_traces, user_query, final_status) -> list[dict]
    把多 Agent 协作的多个 trace 聚合为完整 run 事件流（含 user.input / run.done）
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Iterator

from .events import (
    make_user_input,
    make_agent_activate,
    make_llm_thought,
    make_tool_call,
    make_tool_observation,
    make_llm_final,
    make_run_done,
    make_agent_error,
)


def wrap_trace_to_events(
    trace: list[dict[str, Any]],
    agent_name: str,
    run_id: str,
) -> Iterator[dict[str, Any]]:
    """
    把 core.run_loop 产出的中性 trace 翻译成前端契约事件流。

    中性 trace 格式（来自 core.run_loop return_trace=True）：
      {"kind": "llm",      "step": 1, "data": {"content": "...", "has_tool_calls": bool}}
      {"kind": "tool",     "step": 1, "data": {"phase": "call"|"observation", "name":..., "args":..., "observation":...}}
      {"kind": "final",    "step": 1, "data": {"content": "..."}}

    翻译规则：
      llm  → llm.thought（content 总是 LLM 推理过程）
      tool.call → tool.call
      tool.observation → tool.observation
      final → llm.final
    """
    for t in trace:
        kind = t.get("kind")
        step = t.get("step", 0)
        data = t.get("data", {})

        if kind == "llm":
            # content 既可能是 reasoning_content（推理模型），也可能是普通 content
            yield make_llm_thought(
                run_id=run_id,
                agent=agent_name,
                step=step,
                content=data.get("content", ""),
            )

        elif kind == "tool":
            phase = data.get("phase")
            name = data.get("name", "")
            if phase == "call":
                yield make_tool_call(
                    run_id=run_id,
                    agent=agent_name,
                    step=step,
                    name=name,
                    args=data.get("args", {}),
                )
            elif phase == "observation":
                yield make_tool_observation(
                    run_id=run_id,
                    agent=agent_name,
                    step=step,
                    name=name,
                    observation=data.get("observation", ""),
                )

        elif kind == "final":
            yield make_llm_final(
                run_id=run_id,
                agent=agent_name,
                step=step,
                content=data.get("content", ""),
            )

        elif kind == "error":
            yield make_agent_error(
                run_id=run_id,
                agent=agent_name,
                step=step,
                error=data.get("error", ""),
            )


def aggregate_run_events(
    user_query: str,
    agents_traces: list[tuple[str, list[dict[str, Any]]]],
    run_id: str | None = None,
    final_status: str = "solved",
    started_at: float | None = None,
    ended_at: float | None = None,
    can_activate_before: dict[str, list[str]] | None = None,
) -> list[dict[str, Any]]:
    """
    把"多 Agent 协作的多个 trace"聚合成一个完整 run 事件流。

    Args:
        user_query: 原始用户输入（→ user.input 事件）
        agents_traces: [(agent_name, trace), ...] 按执行顺序
        run_id: run 唯一 ID，不传则自动生成
        final_status: run 结束状态
        started_at / ended_at: 时间戳（time.time()），用于计算 elapsed_s
        can_activate_before: {agent_name: [可激活列表]}，用于还原 activate 事件

    Returns:
        完整的事件列表（user.input → agent.activate → llm.thought → tool.* → llm.final → ... → run.done）
    """
    if run_id is None:
        run_id = uuid.uuid4().hex
    if started_at is None:
        started_at = time.time()
    if ended_at is None:
        ended_at = time.time()
    if can_activate_before is None:
        can_activate_before = {}

    events: list[dict[str, Any]] = []

    # 1. user.input
    events.append(make_user_input(run_id, user_query))

    # 2. 每个 Agent：先 agent.activate，再翻译 trace
    for idx, (agent_name, trace) in enumerate(agents_traces):
        events.append(make_agent_activate(
            run_id=run_id,
            agent=agent_name,
            step=idx,
            can_activate=can_activate_before.get(agent_name, []),
        ))
        events.extend(wrap_trace_to_events(trace, agent_name, run_id))

    # 3. run.done
    events.append(make_run_done(
        run_id=run_id,
        status=final_status,
        summary={
            "elapsed_s": round(ended_at - started_at, 3),
            "agent_count": len(agents_traces),
        },
    ))

    return events


__all__ = ["wrap_trace_to_events", "aggregate_run_events"]
