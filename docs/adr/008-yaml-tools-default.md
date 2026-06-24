# ADR-008: YAML 缺省 tools 字段的隐性陷阱

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

2026-06-24 第一场场景实验跑通后，KPI 6/6 全过，但**实际工具调用 0 次**。用户问"过程中有工具调用吗"，grep 日志确认 `Action:` / `Observation:` / `tool_calls` 全部 0 次。根因不在 run_loop，而在 `relationship.py` 的 YAML 解析路径。

## 代码路径

```python
# relationship.py:533
tools=cfg.get("tools", [])    # YAML 没写 tools → 缺省 []
```

之后：
```python
# relationship.py:182
self.tools = tools or []

# relationship.py:196-197
if self.tools:
    prompt_parts.append(f"你可以使用工具：{', '.join(self.tools)}。")
# self.tools=[] → 整段 if 跳过 → prompt 里根本不告诉 LLM 有工具
```

接着：
```python
# relationship.py:236
tools=self.tools or None  # 传给 OpenAI client → LLM 看到 tools: null → 不可能发起 tool_call
```

## 问题表现

- YAML 注释写"默认为 None = LLM 看到所有已注册工具"但代码默认是 `[]` 不是 `None`，注释与实现不符
- 3 个 agent 全部 `tools=[]` → LLM 完全不知道 calculator / search / get_time 存在
- 用户 query 写"请调用 calculator" 但 LLM 看不到 calculator，不会调

## 修复

在 YAML 显式列 `tools: [calculator, get_time]`，让 LLM 真正看到工具。第二场场景跑出 **8 次 LLM 调用 + 10 次工具调用**（calculator × 8 + get_time × 2），`finish_reason=tool_calls` 6 次。

## 决策

**保留 core 默认行为 `[]`**（不引入隐式的"全部工具"魔法），但同时采取以下补救：

1. 在 `experiments/2026-06-24-tool-scenario.yaml` 模板**显式列 `tools:`**，附强制注释
2. 计划在 `RelationshipEngine.from_yaml()` 里加 `warning` 日志：检测到 `tools` 字段缺省时打印警告（下次重构时实施）
3. 修订 `experiments/2026-06-24-scenario.yaml` 注释（移除错误的"默认为 None"说法）

## 替代方案评估

- **A. 改默认 `tools=cfg.get("tools", None)`**（None = 全部已注册）：更符合"零配置可用"原则，但破坏了"显式优于隐式"的工程风格
- **B. 加运行时警告**：对 zero-config 友好，不破坏显式风格，但只能在 from_yaml 阶段检测
- **C. 引入 `tools_default` 全局配置**：增加配置项复杂度，对 v1.0 收益不明确

## 后果

- 用户每次写 YAML 必须显式列 `tools:`，无法"忘了写就拿到全部工具"
- 第二场实验 35.03s 完成工具调用全链路验证
- 未来重构 `from_yaml()` 时应同时实施警告日志

## 关联教训

与 ADR-005（核心层职责分离）一致——**核心代码不替用户做"看起来友好"的隐式行为**，避免出现 YAML 注释与代码不一致的认知陷阱。
