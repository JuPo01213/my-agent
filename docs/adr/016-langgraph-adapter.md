# ADR-016: 后续方向 D — LangGraph 兼容适配层

- **日期**：2026-06-24
- **状态**：延后

## 背景

自研内核可观测性弱、生态少，但 LangGraph 有 checkpoint / Studio 可视化等成熟工具。

## 决策

保留自研内核为 0 号实现，新增 `agent_core/adapters/langgraph.py` 把 YAML 转 LangGraph StateGraph：

- 每个 Agent → 一个 Node
- preconditions → 条件边
- Command.goto → 显式 edge
- 不反向依赖：本内核不 import LangGraph，adapters 是独立包

## 后果

可选启用 LangGraph 生态，不强制用户换内核。

## 状态

延后到多 Agent 协作模式稳定后实现。
