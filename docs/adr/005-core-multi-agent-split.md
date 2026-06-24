# ADR-005: 后端核心分层重构 - core/ 与 multi_agent/ 分离

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

原 `react_agent.py` 410 行混了 4 类职责：
1. 工具注册（`TOOLS`、`register_tool`）
2. ReAct 核心循环
3. 多 Agent 协作参数（`tools`、`system_prompt`）
4. Dashboard 事件协议（`on_event`、`stop_event`、事件格式）

加上 `dashboard.py` 引入的"前后端耦合"问题——前端探索期的 SSE 推送、停止事件机制被塞进了核心 ReAct 循环，污染了核心抽象。

## 决策

按"职责分离 + 关注点分离"原则完全重构：

- **`agent_core/core/`**：最底层，只做 ReAct 循环 + 工具注册表
  - `react_agent.py`（~100 行）：纯 `run_loop()`，返回最终答案字符串
  - `tool_registry.py`：TOOLS + register_tool + build_openai_tools_schema + validate_tool_args
- **`agent_core/multi_agent/`**：多 Agent 协作的公开 API 层
  - `agent_api.py`：包装 core.run_loop，提供 `run_react_agent(user_input, client, model, tools, system_prompt, max_steps)`
  - `tool_filter.py`：`filter_tools_schema(tools)` 根据工具名列表过滤 OpenAI Schema
  - `tool_caller.py`：`call_tool_safe(tool_name, tool_args)` 安全调用工具
- **删除** `dashboard.py`（前端探索期不再维护，前后端解耦）
- **删除** 所有 dashboard 相关代码：`on_event`、`stop_event`、事件协议（thought/action/observation/final）

## 违反原则 vs 收益

- **违反向后兼容**：完全重构优于兼容改造（项目规则已明确）
- **违反 KISS（短文件）**：拆成 5 个文件，单个文件更简单
- **收益**：
  - 关注点分离：核心循环不再背负"事件协议"这种 UI 概念
  - 公开 API 聚拢：Supervisor 只需 import `agent_core.multi_agent`
  - 可测试性：纯函数 `run_loop` 易于 mock
  - 可演进：未来加新 Agent 类型只需在 multi_agent/ 加新文件，不动 core

## 后果

- `dashboard.py` 不再维护，前端探索期所有样式测试通过 `agent_core/static/*.html` 静态预览
- core/ 与 multi_agent/ 之间单向依赖：multi_agent → core，不反向
- 后续 Supervisor / Hierarchical / Swarm 等模式都基于 `run_react_agent` 实现
- 若未来要恢复 dashboard 集成，需要在 multi_agent/ 上层新建 `ui/` 层（而不是改 core）
