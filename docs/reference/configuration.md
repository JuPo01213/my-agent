# 配置参考

本文档描述 my-agent 项目的配置文件结构和用法。

## 配置文件列表

| 文件 | 用途 |
|------|------|
| `config/agents.yaml` | Agent 定义（role / goal / backstory / tools / max_iter / preconditions） |
| `config/relationships.yaml` | 关系定义（priority / termination） |

## agents.yaml 结构

```yaml
agents:
  - id: advisor
    role: 顾问
    goal: 分析问题并提供建议
    backstory: 你是一个经验丰富的顾问
    tools: [search, get_time]
    max_iter: 5
    preconditions: "open_questions == []"
    system_prompt: |
      你是顾问 Agent，负责分析用户问题...
```

## relationships.yaml 结构

```yaml
relationships:
  - strategy: priority
    termination:
      type: max_steps
      value: 10
    agents: [advisor, strategist, writer]
```

## 关键字段说明

- **tools**：Agent 可使用的工具列表，必须显式声明
- **preconditions**：激活条件，支持 `facts.has('key')` 和 `and` 组合
- **strategy**：调度策略，可选 `first_match` / `priority` / `round_robin`
- **termination**：终止条件，支持 `max_steps` / `all_solved` / `custom`

## 注意事项

- YAML 中 `tools` 字段必须显式声明，缺省时为 `[]`（LLM 看不到任何工具）
- preconditions 表达式仅支持安全子集，不引入 eval()
- 修改 YAML 即可改变协作流程，零改 Python 代码
