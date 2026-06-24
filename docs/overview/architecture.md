# 架构概览

本文档描述 my-agent 的架构设计，包括分层结构、核心模块和关键抽象。

## 分层架构

项目采用“core + multi_agent”分层：

```
agent_core/
├── core/           # 最底层：ReAct 循环 + 工具注册表
├── multi_agent/    # 公开 API 层：多 Agent 协作
├── frontend/       # 前端事件协议（schema + adapter）
├── static/         # 前端探索期静态文件
└── demos/          # 演示代码，不参与主项目运行
```

## 核心层（core/）

- `react_agent.py`：纯 ReAct 循环，返回最终答案字符串
- `tool_registry.py`：工具注册表 + 3 个内置工具

**约束**：不暴露任何 dashboard 相关参数，不依赖前端/网络库。

## 多 Agent 层（multi_agent/）

- `agent_api.py`：包装 core.run_loop，提供 `run_react_agent()`
- `relationship.py`：关系驱动协作引擎（Blackboard / Command / KnowledgeSource / ControlShell）
- `tool_filter.py` / `tool_caller.py`：工具过滤与安全调用

**约束**：Supervisor 唯一入口，单向依赖 core/。

## 前端层（frontend/）

- `events.py`：事件 schema 定义
- `adapter.py` / `bus.py`：事件适配与总线

**约束**：核心层不依赖前端库，事件 schema 独立存放。

## 关键抽象

| 抽象 | 职责 | 位置 |
|------|------|------|
| Blackboard | 共享状态（facts / open_questions / history） | relationship.py |
| Command | 路由原语（goto + update + terminate） | relationship.py |
| KnowledgeSource | Agent 单元（preconditions + action） | relationship.py |
| ControlShell | OODA 循环调度器 | relationship.py |
| RelationshipEngine | YAML 驱动的协作引擎 | relationship.py |

## 演进路线

- v1.0：串行/优先级调度，零外部依赖
- v1.1：并行执行
- v2.0：Swarm / Hierarchical 模式
- v3.0：自动反思与记忆
