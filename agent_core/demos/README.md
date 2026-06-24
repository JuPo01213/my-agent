# Demos 目录说明

> **创建日期**：2026-06-24
> **最后更新**：2026-06-24（E2 任务扩写）
> **作用**：存放多 Agent 架构的演示代码，**不参与主项目运行**

---

## 为什么独立出来

1. **避免污染主项目**：演示代码可能依赖额外库（如 langgraph），不应该影响主项目稳定性
2. **便于学习参考**：所有演示代码集中管理，方便对比不同实现方式
3. **保持极简内核**：主项目 `relationship.py` 核心约 330 行 + `core/react_agent.py` 约 100 行
4. **依赖隔离**：每个 demo 各自管理依赖，主项目不强制安装

---

## 文件列表

| 文件 | 内容 | 依赖 | 何时看 |
|------|------|------|--------|
| `multi_agent_demo.py` | 简单 Supervisor 模式演示（函数调用链） | 无 | 理解 Supervisor 基础概念 |
| `stategraph_demo.py` | 自定义状态图模式演示（自实现图引擎） | 无 | 学习状态图原理，了解 ADR-005 重构前的旧设计 |
| `relationship_demo.py` | **关系驱动引擎**演示（Blackboard + Command + KS） | 无 | 看主项目怎么用 / 准备写自定义协作流程 |
| `langgraph_demo.py` | LangGraph 框架模式演示（自实现 StateGraph 风格） | langgraph | 对比自研 vs LangGraph |
| `langgraph_official.py` | LangGraph 官方 Supervisor 示例 | langgraph | 学习 LangGraph 最佳实践 |

---

## 模式选择指南

| 模式 | 文件 | 适用场景 | 优缺点 |
|------|------|----------|--------|
| **简单 Supervisor** | `multi_agent_demo.py` | Agent 固定几种，任务简单 | 简单直接，但耦合度高 |
| **自定义状态图** | `stategraph_demo.py` | 复杂分支、需保持零依赖 | 灵活但维护成本高 |
| **关系驱动**（主项目） | `relationship_demo.py` | **生产项目首选**，需要 YAML 配置 + 调度策略 | 配置驱动，3 种策略，可演进 |
| **LangGraph** | `langgraph_demo.py` / `langgraph_official.py` | 需要完整框架支持 / 团队熟悉 LangGraph | 生态全，但引入重型依赖 |

---

## 怎么选

```
你要做什么？
│
├─ 我想学原理，理解多 Agent 协作是怎么回事
│  └─ 从 multi_agent_demo.py 开始（最简单）
│
├─ 我要在主项目上写自己的协作流程
│  └─ relationship_demo.py（用 RelationshipEngine.from_yaml）
│
├─ 我想对比自研 vs LangGraph 的设计哲学
│  └─ 顺序读：stategraph_demo.py → langgraph_demo.py → 关系驱动
│
└─ 我想直接用 LangGraph
   └─ langgraph_official.py（参考官方模式）
```

---

## 运行方式

```bash
# 基础 demo（无需额外依赖）
python agent_core/demos/multi_agent_demo.py
python agent_core/demos/stategraph_demo.py
python agent_core/demos/relationship_demo.py

# LangGraph（需要先安装）
pip install langgraph
python agent_core/demos/langgraph_demo.py
python agent_core/demos/langgraph_official.py
```

---

## 与主项目的关系

**Demos 是参考实现，主项目才是生产代码**：

- 主项目路径：`agent_core/multi_agent/relationship.py`（实际生产引擎）
- 演示路径：`agent_core/demos/relationship_demo.py`（如何调用的样板）
- 一致性原则：主项目演进时，demos 必须同步更新（参见 ADR-005 违反原则 vs 收益）

---

## 相关文档

- [多智能体协作系统设计模式完整调研报告](../../docs/report/多智能体协作系统设计模式完整调研报告.md)
- [LangGraph多Agent架构官方模式参考](../../docs/report/LangGraph多Agent架构官方模式参考.md)
- [关系驱动多Agent协作架构实现方案](../../docs/report/关系驱动多Agent协作架构实现方案.md)
