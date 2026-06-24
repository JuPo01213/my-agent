# Demos 目录说明

> **创建日期**：2026-06-24
> **作用**：存放多 Agent 架构的演示代码，**不参与主项目运行**

---

## 为什么独立出来

1. **避免污染主项目**：演示代码可能依赖额外库（如 langgraph），不应该影响主项目稳定性
2. **便于学习参考**：所有演示代码集中管理，方便对比不同实现方式
3. **保持极简内核**：主项目 `react_agent.py` 只有 ~300 行核心 ReAct 逻辑

---

## 文件列表

| 文件 | 内容 | 依赖 |
|------|------|------|
| `multi_agent_demo.py` | 简单 Supervisor 模式演示（函数调用链） | 无 |
| `stategraph_demo.py` | 自定义状态图模式演示（自实现图引擎） | 无 |
| `langgraph_demo.py` | LangGraph 框架模式演示 | langgraph |
| `langgraph_official.py` | LangGraph 官方代码示例 | langgraph |

---

## 模式选择指南

| 模式 | 文件 | 适用场景 |
|------|------|----------|
| **简单 Supervisor** | `multi_agent_demo.py` | Agent 固定几种，任务简单 |
| **自定义状态图** | `stategraph_demo.py` | 复杂分支、需保持零依赖 |
| **LangGraph** | `langgraph_demo.py` | 生产级应用，需要完整框架支持 |

---

## 运行方式

```bash
# 简单 Supervisor（无需额外依赖）
python demos/multi_agent_demo.py

# 自定义状态图（无需额外依赖）
python demos/stategraph_demo.py

# LangGraph（需要先 pip install langgraph）
python demos/langgraph_demo.py
```

---

## 相关文档

- [多智能体协作系统设计模式完整调研报告](../docs/report/多智能体协作系统设计模式完整调研报告.md)
- [LangGraph多Agent架构官方模式参考](../docs/report/LangGraph多Agent架构官方模式参考.md)
