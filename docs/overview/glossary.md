# 术语表

本文档定义 my-agent 项目中常用的术语和概念。

## 核心术语

- **ReAct**：Reasoning + Acting 循环，LLM 交替输出 thought 和 action
- **Agent**：具有角色定义、工具集和预条件的执行单元
- **KnowledgeSource**：项目中的 Agent 抽象，包含 preconditions + action
- **Blackboard**：共享状态板，存储 facts、open_questions、history
- **Command**：路由原语，包含 goto、update、terminate 三个字段
- **ControlShell**：调度器，负责选择 KnowledgeSource 并执行 OODA 循环
- **RelationshipEngine**：YAML 驱动的多 Agent 协作引擎

## 架构术语

- **core/**：最底层，只做 ReAct 循环和工具注册表
- **multi_agent/**：公开 API 层，Supervisor 唯一入口
- **frontend/**：前端事件协议层，独立于核心层
- **static/**：前端探索期静态文件，不与后端联通
- **demos/**：演示代码，不参与主项目运行

## 调度策略

- **first_match**：第一个满足 preconditions 的 Agent 被激活
- **priority**：按 metadata.priority 排序，优先激活高优先级 Agent
- **round_robin**：轮询调度，依次激活每个 Agent

## 文档术语

- **ADR**：Architecture Decision Record，架构决策记录
- **KPI**：Key Performance Indicator，关键性能指标
- **YAML**：配置文件格式，用于定义 Agent 和关系
- **SSE**：Server-Sent Events，服务器推送事件
- **OODA**：Observe-Orient-Decide-Act，观察-判断-决策-执行循环
