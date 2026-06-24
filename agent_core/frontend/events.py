"""
agent_core.frontend.events - 前端事件 Schema
============================================

**设计原则**（依据 ADR-013）：
  1. 字段名一律 snake_case
  2. 时间戳统一用 ISO-8601 字符串（`datetime.utcnow().isoformat() + "Z"`）
  3. 每个事件必有 `type` / `ts` / `run_id` 三个基础字段
  4. 提供工厂函数 + 类型常量，避免拼字典出错
  5. **不依赖任何前端框架**，纯 Python dict

**事件类型一览**（初版 7 种）：

| type 字段 | 含义 | 何时触发 |
|---|---|---|
| `user.input` | 用户原始问题 | run 启动时 |
| `agent.activate` | 调度器选中某 Agent | 每个 OODA 步骤开始 |
| `llm.thought` | LLM 推理过程 | 每次 LLM 响应（reasoning_content） |
| `tool.call` | 工具调用请求 | LLM 决定调工具 |
| `tool.observation` | 工具返回结果 | 工具执行完毕 |
| `llm.final` | 单 Agent 最终答案 | LLM 不再调工具，准备返回 |
| `run.done` | 整个 OODA 循环结束 | 终止条件触发或 max_steps 到限 |

**前端消费示例**（Vue）：

```js
// 消费同一份 schema
ws.onmessage = (ev) => {
  const e = JSON.parse(ev.data);
  switch (e.type) {
    case 'llm.thought': addBubble({type:'thinking', content: e.content}); break;
    case 'tool.call':    addBubble({type:'tool', name: e.name, args: e.args}); break;
    case 'tool.observation': addBubble({type:'tool', name:e.name, observation:e.observation}); break;
    case 'llm.final':    addBubble({type:'final', content: e.content}); break;
    case 'run.done':     playing.value = false; break;
  }
}
```
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# 事件类型常量
# ---------------------------------------------------------------------------

USER_INPUT = "user.input"
AGENT_ACTIVATE = "agent.activate"
LLM_THOUGHT = "llm.thought"
TOOL_CALL = "tool.call"
TOOL_OBSERVATION = "tool.observation"
LLM_FINAL = "llm.final"
RUN_DONE = "run.done"

# 错误事件（预留）
AGENT_ERROR = "agent.error"

EVENT_TYPES: tuple[str, ...] = (
    USER_INPUT,
    AGENT_ACTIVATE,
    LLM_THOUGHT,
    TOOL_CALL,
    TOOL_OBSERVATION,
    LLM_FINAL,
    RUN_DONE,
    AGENT_ERROR,
)


def _now_iso() -> str:
    """统一时间戳格式：UTC ISO-8601，结尾 'Z'。"""
    return datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


def _base(event_type: str, run_id: str, **extra: Any) -> dict[str, Any]:
    """构造事件基础结构：type / ts / run_id + 业务字段。"""
    return {
        "type": event_type,
        "ts": _now_iso(),
        "run_id": run_id,
        **extra,
    }


# ---------------------------------------------------------------------------
# 工厂函数
# ---------------------------------------------------------------------------


def make_user_input(run_id: str, content: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """用户输入事件。meta 可放 IP / 渠道 / 来源等。"""
    return _base(USER_INPUT, run_id, content=content, meta=meta or {})


def make_agent_activate(
    run_id: str,
    agent: str,
    role: str = "",
    step: int = 0,
    can_activate: list[str] | None = None,
) -> dict[str, Any]:
    """Agent 被调度器选中。can_activate 列出当前所有可激活的 Agent，便于前端展示调度过程。"""
    return _base(
        AGENT_ACTIVATE,
        run_id,
        agent=agent,
        role=role,
        step=step,
        can_activate=can_activate or [],
    )


def make_llm_thought(
    run_id: str,
    agent: str,
    content: str,
    step: int = 0,
) -> dict[str, Any]:
    """LLM 推理过程（来自 response.reasoning_content）。"""
    return _base(LLM_THOUGHT, run_id, agent=agent, step=step, content=content)


def make_tool_call(
    run_id: str,
    agent: str,
    name: str,
    args: dict[str, Any] | str,
    step: int = 0,
) -> dict[str, Any]:
    """工具调用请求。args 可以是 dict（已解析）或 str（原始 JSON 字符串）。"""
    return _base(TOOL_CALL, run_id, agent=agent, step=step, name=name, args=args)


def make_tool_observation(
    run_id: str,
    agent: str,
    name: str,
    observation: str,
    step: int = 0,
) -> dict[str, Any]:
    """工具执行结果（已校验 + 异常捕获后）。"""
    return _base(
        TOOL_OBSERVATION,
        run_id,
        agent=agent,
        step=step,
        name=name,
        observation=observation,
    )


def make_llm_final(
    run_id: str,
    agent: str,
    content: str,
    step: int = 0,
) -> dict[str, Any]:
    """单 Agent 最终答案（来自 run_loop 返回的字符串）。"""
    return _base(LLM_FINAL, run_id, agent=agent, step=step, content=content)


def make_run_done(
    run_id: str,
    status: str,
    summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """整个 OODA 循环结束。status: solved / failed / timeout。"""
    return _base(RUN_DONE, run_id, status=status, summary=summary or {})


def make_agent_error(
    run_id: str,
    agent: str,
    error: str,
    step: int = 0,
) -> dict[str, Any]:
    """Agent 异常事件。"""
    return _base(AGENT_ERROR, run_id, agent=agent, step=step, error=error)


__all__ = [
    "EVENT_TYPES",
    "USER_INPUT",
    "AGENT_ACTIVATE",
    "LLM_THOUGHT",
    "TOOL_CALL",
    "TOOL_OBSERVATION",
    "LLM_FINAL",
    "RUN_DONE",
    "AGENT_ERROR",
    "make_user_input",
    "make_agent_activate",
    "make_llm_thought",
    "make_tool_call",
    "make_tool_observation",
    "make_llm_final",
    "make_run_done",
    "make_agent_error",
]
