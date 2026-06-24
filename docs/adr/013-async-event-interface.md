# ADR-013: 后续方向 A — 异步/流式事件接口

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

现在 3 个 Agent 跑 28 秒，前端什么都看不到，只能等最终结果。Demo 时想给用户看"advisor 在想 / strategist 在算 / writer 在写"。

## 决策

在 `core/run_loop` 与 `multi_agent/ControlShell` 加 `on_event: Callable[[dict], None]`，**事件 schema 统一放在 `agent_core/frontend/events.py`**，让 SSE/WS/HTTP POST 都能复用同一份契约。

## 事件类型（初版 6 类）

- `user.input`：原始用户输入
- `agent.activate`：调度器选中某个 Agent
- `llm.thought`：LLM 的 thought（reasoning_content 字段）
- `tool.call` / `tool.observation`：工具调用与结果
- `llm.final`：单 Agent 最终答案
- `run.done`：整个 OODA 循环结束

## 架构约束

核心层不依赖任何前端/网络库；事件 schema 放在独立 `agent_core/frontend/` 目录，便于后续抽 SDK 或对接 LangGraph/LangSmith 事件格式。

## 后果

- 优点：可观测性、可调试性、demo 表现力大幅提升
- 代价：核心层多一个 callback 参数，需要保证默认 None 时行为不变（向后兼容）
- 风险：用户忽略 callback，会"看起来没效果"，需在文档里强调默认要传
