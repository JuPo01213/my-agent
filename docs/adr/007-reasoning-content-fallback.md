# ADR-007: ReAct 循环兼容推理模型（reasoning_content fallback）

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

`run_loop()`（位于 `agent_core/core/react_agent.py:101-103`）原本只读 `response_msg.content` 字段作为 final_answer。StepFun `step-3.7-flash` 等推理模型（reasoning model）会先在内部完成 CoT 推理，再产出短 final answer；`content` 经常为空或极短（仅 17 字符级别），真实完整输出在 `reasoning_content` 字段里。

## 问题表现

- 2026-06-24-relationship-real.log 中 researcher 走默认 ReAct 循环，8 步 search 占位调用后 `final_answer` 为空
- 2026-06-24-scenario.py 第一版（绕过 ReAct 循环直接 chat.completions）虽然能用 reasoning_content，但违背了"ReAct 循环是项目核心"原则

## 决策

在 `run_loop` 调 LLM 之后，`reply_content = response_msg.content or ""` 后增加 fallback：

```python
if not reply_content and getattr(response_msg, "reasoning_content", None):
    reply_content = response_msg.reasoning_content
```

满足两个条件：
1. `content` 为空
2. `reasoning_content` 存在

才做 fallback；正常模型的 `content` 优先（避免污染非推理模型）。

## 优势

- ReAct 循环保持完整运行（用户原始诉求）
- 推理模型的 reasoning 过程 + final answer 全部进入 Blackboard.facts
- 3 段产出从原来 17 字跃升至 6865+7600+9866 字
- 对非推理模型零影响（content 仍优先）

## 替代方案评估

- **A. 改 system_prompt 强制 LLM 不调 reasoning**：StepFun reasoning model 不能关掉 reasoning，方案不可行
- **B. 在 default action 工厂里 merge reasoning_content**：增加一层抽象、不如在 run_loop 源头修
- **C. 提供开关参数 `use_reasoning_content: bool`**：留给未来，当前用最简单的 fallback 即可

## 后果

- 修复后，2026-06-24-scenario.py 在 129.6s 内完成 3 Agent ReAct 循环，8/8 KPI 全过
- ReAct 循环对 StepFun、Doubao-pro、Claude-3.7-Sonnet 等推理模型都生效
- 推理模型的输出会包含"思考过程"+"答案"，对最终用户而言略冗余（可后续让前端展示折叠）
