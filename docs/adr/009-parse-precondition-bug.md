# ADR-009: 修复 _parse_precondition 三 key and 表达式分支顺序 bug

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

在 E2 任务（补单元测试）的 A2 阶段，写 `test_and_three_keys` 单元测试时**首次暴露**一个潜在 bug：

```python
expr = "facts.has('a') and facts.has('b') and facts.has('c')"
fn = _parse_precondition(expr)
fn({"facts": {"a": 1}})  # 期望 False，实际返回 True
```

## 根因

`_parse_precondition` 内分支顺序错误：

- 旧顺序：先判断 `"facts.has(" in expr and ")" in expr`（单 key 分支），再判断 `" and " in expr and "facts.has(" in expr`（and 组合分支）
- 三 key 表达式同时满足两个分支条件，但**单 key 分支在前**，`_extract_str` 只取了**第一个** key `'a'`，导致三 key 表达式的"全部满足"语义被错误实现为"任一满足"
- 实际效果：3 个 key 任一存在都返回 True → 与 YAML 设计意图（必须全部存在）相反

## 影响范围

- 当前 v1.0 实际跑过的 YAML 都只用了 1-2 个 key（researcher/analyst/writer 链），未触发该 bug
- 任何未来配置 3+ key 组合的 preconditions 都会**静默失效**（多条件退化为任一条件）
- 这种"静默成功"是最危险的 bug：流程能跑完但结果不对

## 决策

把 and 组合分支**前移**到单 key 分支之前：

```python
# 先匹配更具体的 "facts.has('a') and facts.has('b') and ..." 模式
if " and " in expr and "facts.has(" in expr:
    keys = re.findall(...)
    if keys:
        return lambda snap, ks=keys: all(k in snap.get("facts", {}) for k in ks)
# 再回退到单 key 模式
if "facts.has(" in expr and ")" in expr:
    ...
```

同时把 `import re` 从函数内部移到模块顶部（更规范，避免重复 import）

## 关联教训

1. **单元测试是潜在 bug 的第一道防线**：A2 任务的 20 个测试覆盖是首次发现该 bug 的唯一途径
2. **分支顺序需要按"特殊性 → 一般性"**：更具体的模式优先匹配，是解析器设计的通用原则
3. **与 ADR-005 一致**：核心层不替用户做"看起来友好"的隐式行为，所以 preconditions 写错不会崩，但必须返回**正确**的语义

## 检测手段

- `tests/test_parse_precondition.py::TestParsePreconditionAnd::test_and_three_keys` 作为回归测试
- 任何后续 PR 修改 `_parse_precondition` 必须同时跑该测试

## 后果

- 三 key and 表达式现在按预期返回 all() 语义
- 单 key 模式不受影响（旧测试全部通过验证）
- 文档承诺（"facts.has('a') and facts.has('b')" → 组合判断"）与实现一致
