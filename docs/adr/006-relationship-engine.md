# ADR-006: 引入关系驱动多 Agent 协作引擎

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

单 Agent ReAct 循环在面对复杂任务（多步分析、协作生产）时存在天然瓶颈：上下文超载、工具与人设混用、无法拆分专业角色。需要在 ADR-002 自研内核的基础上，不引入 LangGraph 重型依赖，实现可配置的多 Agent 协作能力。

## 决策

在 `multi_agent/` 层新增 `relationship.py`（~330 行），实现**关系驱动**的多 Agent 协作引擎，借鉴 4 个业界成熟实践：

- **Blackboard 模式**（callisphere.ai / Hearsay-II 1970）：共享状态 + Knowledge Sources + Control Shell
- **LangGraph Command**（langchain-ai.github.io）：`Command(goto, update, terminate)` 路由原语
- **CrewAI YAML**（crewai.com 官方）：`role / goal / backstory` 三元组 + agents.yaml / tasks.yaml 声明式
- **SALLMA 目录化**（佛罗伦萨大学 SATrends 2025）：Knowledge/Operational 双层 + 目录驱动

## 核心抽象

- `Blackboard`：共享状态（facts / open_questions / history / status / metadata）
- `Command`：`goto + update + terminate` 路由原语
- `KnowledgeSource`：Agent 单元（preconditions + action + role/goal/backstory）
- `ControlShell`：OODA 循环调度器（first_match / priority / round_robin 三种 strategy）
- `RelationshipEngine`：YAML 驱动的协作引擎 + `from_yaml()` 工厂

## 强约束机制

- `_parse_precondition()`：**安全子集表达式**（不引入 eval()），仅支持 `True/False`、`facts.has('key')`、`open_questions`、and 组合
- `_activated` 集合：Agent 一次性激活，避免 first_match 死循环
- 重复激活需用 `Command.goto` 显式转交（用于反思/迭代场景）

## YAML 驱动

- `config/agents.yaml`：Agent 定义（role / goal / backstory / tools / max_iter / preconditions / system_prompt）
- `config/relationships.yaml`：关系定义（priority / termination）
- **修改 YAML 即可改变协作流程，零改 Python 代码**

## 违反原则 vs 收益

- **违反 KISS（短文件）**：单文件 330 行
- **收益**：
  - 完全零外部依赖（除 PyYAML + openai SDK），保留自研内核优势
  - 同时支持 3 种调度策略 + 自定义 done_when 终止条件
  - 演示代码 (`demos/relationship_demo.py`) 覆盖 3 种典型用法：Python API / YAML 驱动 / 自定义 action

## 后果

- v1.0 仅支持串行/优先级调度，**不**支持并行 / Swarm / Hierarchical
- 默认 action 调 `run_react_agent`（复用 core/ 循环），KnowledgeSource 仍然受 max_steps 限制
- 下一步演进：v1.1 加并行执行、v2.0 加 Swarm/Hierarchical、v3.0 加自动反思与记忆
