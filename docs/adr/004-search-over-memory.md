# ADR-004: 路由决策使用搜索而非记忆

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

多 Agent 协作中，调度器（Supervisor/Router）需要判断下一步行动，但 LLM 的知识有截止日期，容易产生幻觉。

## 决策

路由决策时，优先使用搜索技能获取实时准确信息，而不是依赖 LLM 的内部记忆。

## 路由原则

1. **信息不确定时 → 搜索**：如果需要判断某事是否为事实，先搜索再决定
2. **知识可能过时 → 搜索**：涉及最新资讯、技术文档、政策法规，必须搜索
3. **明确常识可复用**：纯粹的逻辑推理、数学计算可以用内部知识

## 示例

```python
# 错误：凭记忆判断
def router(state):
    if "Python" in state.task:
        return "code_agent"  # LLM 记忆可能过时

# 正确：搜索后判断
def router(state):
    search_result = web_search("Python 最新版本 2024")
    if "版本" in search_result:
        return "code_agent"
```

## 后果

- 路由准确性更高，减少幻觉导致的错误决策
- 会增加搜索调用次数
