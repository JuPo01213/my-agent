# ADR-015: 后续方向 C — first_match 看门人模式

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

当前 demo 全是 priority 线性流水线，没演示 first_match 真正擅长的"看门人"场景。

## 决策

在 `demos/` 新增一个 `gatekeeper_demo.py`：

- Agent A: `preconditions: "open_questions == []"`（简单问题直接答）
- Agent B: `preconditions: "open_questions != []"`（复杂问题进多 Agent 流程）
- 用 `first_match` 策略，根据问题复杂度自动分流。

## 后果

证明 `preconditions` 子集化不仅能做流水线，还能做"看门人 + 派单"。
