# ADR-014: 后续方向 B — 工具白名单让 LLM 真用工具

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

当前 `_default_action` 把 `self.tools` 透传给 `run_react_agent`，但 demo 故意没在 YAML 里列 `tools`，导致 LLM 看不到任何工具，工具调用次数恒为 0。

## 决策

在 `experiments/2026-06-24-scenario.yaml` 显式声明每个 Agent 的 `tools: [...]`：

- `advisor`: `["search", "get_time"]` —— 让它能联网/取时间
- `strategist`: `["calculator"]` —— 强制算预算百分比
- `writer`: `[]` —— 写报告不调工具

## 不破坏既有契约

`_default_action` 已经接受 `tools` 参数，本次只是 YAML 端补齐，与 ADR-008 配套。

## 后果

Advisor 真的去 search、Strategist 真的去算百分比，工具调用次数 > 0，对论文/汇报更可信。
