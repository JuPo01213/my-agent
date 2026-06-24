# 关系驱动多 Agent 协作架构实现报告

> **版本**：v1.0
> **日期**：2026-06-24
> **作用**：基于 LangGraph / SALLMA / Accountability / CrewAI / Blackboard / SAMALM 等业界成熟实践，给出本项目"关系驱动多 Agent 协作层"的完整实现方案，包含模式融合策略、可运行的 Python 代码示例以及 YAML 声明式配置。
> **面向读者**：本项目主代理、Supervisor 工程师、关系引擎贡献者
> **核心立场**：单一模式无法应对所有场景；以 Blackboard 为底座，在其上叠加 Supervisor / Swarm / Hierarchical / Handoffs / Parallel 等模式，关系由 YAML 驱动、不改代码。

---

## 目录

1. 业界成熟实践案例
2. 对本项目的设计建议
3. 关系引擎 `multi_agent/relationship.py` 详细实现方案
4. 模式融合策略
5. 落地路线图
6. 参考资料

---

## 一、业界成熟实践案例

本节梳理与"关系驱动多 Agent 协作"主题最相关的 7 个实践/研究案例，每个案例都给出**出处链接**、**核心抽象**、**可借鉴点**三部分。

### 案例 1：LangGraph 官方多 Agent 架构

**出处**：
- 官方文档：[LangGraph Multi-agent Concepts](https://langchain-ai.github.io/langgraph/agents/multi-agent/)
- 官方文档：[LangGraph Multi-agent Systems](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- 子库：[langgraph-supervisor PyPI](https://pypi.org/project/langgraph-supervisor/)（版本 0.0.29）
- 子库：[langgraph-swarm PyPI](https://pypi.org/project/langgraph-swarm/)
- 源码：[langchain-ai/langgraph-supervisor-py](https://github.com/langchain-ai/langgraph-supervisor-py)
- 源码：[langchain-ai/langgraph-swarm-py](https://github.com/langchain-ai/langgraph-swarm-py)

**5 种架构概览**：

| 架构 | 控制中心 | 通信方式 | 适用场景 |
|------|----------|----------|----------|
| **Network** | 无中心 | 任意 Agent 互相通信 | 头脑风暴、复杂决策 |
| **Supervisor** | 单一中心 | Agent ↔ Supervisor | 任务明确、需要集中控制 |
| **Supervisor (tool-calling)** | 单一中心 | Supervisor 通过工具调用子 Agent | 工具调用协议统一 |
| **Hierarchical** | 多层中心 | 多层 Supervisor 嵌套 | 大型复杂任务 |
| **Custom** | 部分确定 | 部分 Agent 决定下一步 | 业务流程复杂、有明确路径 |

**核心原语 1：Command**

```python
from langgraph.types import Command

# goto 指定下一个节点，update 携带状态增量
return Command(
    goto="flight_assistant",          # 路由到下一个 Agent
    update={
        "messages": [response],        # 消息流
        "next_step": "booking",        # 自定义状态
    }
)
```

**核心原语 2：Handoffs**

```python
from langchain_core.tools import tool
from langgraph.types import Command

@tool
def transfer_to_specialist(reason: str) -> Command:
    """把任务转交给专员 Agent"""
    return Command(
        goto="specialist",
        update={
            "messages": [
                ToolMessage(
                    content=f"Transferred to specialist: {reason}",
                    tool_call_id=...,
                )
            ],
        },
    )
```

**可借鉴点**：
1. **Command(goto, update) 二元组**：用 `goto` 决定下一个 Agent，用 `update` 携带状态增量。这种"路由 + 状态"的二元表达非常优雅。
2. **Handoffs 即工具**：把"转交"建模成普通工具，可以由 LLM 自主决定何时触发。
3. **Supervisor (tool-calling) 变体**：用工具调用协议统一调度，子 Agent 就是 Supervisor 的工具集合。

---

### 案例 2：SALLMA（佛罗伦萨大学，SATrends 2025）

**出处**：
- 论文：[SALLMA: A Software Architecture for LLM-Based Multi-Agent Systems](https://www.scitepress.org/Papers/2025/...)（搜索 "SALLMA software architecture LLM multi-agent"）
- 参考：[arXiv 预印本 2411.06830](https://arxiv.org/abs/2411.06830)（SALLMA 相关实现）

**双层架构**：

```
┌────────────────────────────────────────────────────┐
│  Knowledge Layer（知识层，配置/不常变）              │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │
│  │  Agent Type   │ │ Relationship  │ │   Scope    │  │
│  │   Catalog     │ │ Type Catalog  │ │   Schema   │  │
│  └──────────────┘ └──────────────┘ └────────────┘  │
└────────────────────────────────────────────────────┘
                          ↓ 启动时加载
┌────────────────────────────────────────────────────┐
│  Operational Layer（操作层，运行时实例化）            │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐            │
│  │Agent1│←→│Agent2│←→│Agent3│←→│Agent4│           │
│  └──────┘  └──────┘  └──────┘  └──────┘            │
└────────────────────────────────────────────────────┘
```

**三大目录（Catalog）**：

1. **Agent Type Catalog（代理类型目录）**
   - 每个 Agent 类型声明：能力、工具、提示、内存
2. **Relationship Type Catalog（关系类型目录）**
   - 关系的形式化定义：`from → to`，含条件、约束
3. **Scope Schema（作用域模式）**
   - 哪些 Agent / 关系在某次任务中可见

**技术栈**：Python + LangChain + Docker + Kubernetes

**可借鉴点**：
1. **知识/操作分离**：配置（knowledge）不与运行时实例（operational）耦合
2. **目录化配置**：把"什么 Agent、什么关系"用目录方式集中管理
3. **支持不改代码重配置**：换 Agent 或换关系只需改 YAML，不动 Python

---

### 案例 3：Accountability 模式（佛罗伦萨大学，BigData 2026）

**出处**：
- 论文：佛罗伦萨大学（University of Florence）关于多 Agent 问责制（Accountability）的研究
- 主题搜索词："multi-agent accountability big data 2026 Florence"

**形式化关系**：

```
Commissioner（委托人）─[commits to]→ Responsible（责任人）
                                  ↓
                              [held to]
                                  ↓
                              Obligation（义务）
```

**强约束**：
1. **能力（Capabilities）**：Responsible 必须具备执行的能力
2. **工具权限（Tool Permissions）**：哪些工具是允许的
3. **可衡量的义务（Measurable Obligations）**：执行结果必须可量化验证

**可借鉴点**：
1. **关系即承诺**：把 Agent 间关系从"松散调用"升级为"带义务的承诺"
2. **可衡量的约束**：每个关系都应能验证是否完成
3. **问责制思想**：出错时知道"谁该负责"，对应到具体 Agent

---

### 案例 4：CrewAI（官方文档 + 教程）

**出处**：
- 官方文档：[CrewAI Documentation](https://docs.crewai.com/)
- 教程：[CrewAI Quickstart](https://docs.crewai.com/quickstart)
- PyPI：[crewai](https://pypi.org/project/crewai/)
- 博客：[Building Multi-Agent Systems with CrewAI](https://blog.langchain.com/crewai-multi-agent-systems)

**YAML 声明式配置**：

`agents.yaml`：
```yaml
researcher:
  role: "{topic} 高级研究员"
  goal: 揭示与 {topic} 相关的前沿进展
  backstory: 你是清华人工智能实验室的首席研究员
  tools:
    - web_search
    - arxiv_search
  memory: true
  allow_delegation: false
  max_iter: 15
  llm: gpt-4o

writer:
  role: 资深技术作家
  goal: 把研究材料写成结构化报告
  backstory: 你是技术写作专家
  tools:
    - file_write
  memory: true
  allow_delegation: true
  max_iter: 10
  llm: gpt-4o
```

`tasks.yaml`：
```yaml
research_task:
  description: 研究 {topic} 的最新进展
  expected_output: 包含 3 篇核心论文的 markdown 报告
  agent: researcher
  context:
    - prior_research
  output_file: research.md

writing_task:
  description: 基于研究材料写一篇 2000 字博客
  expected_output: 完整博客 markdown
  agent: writer
  context:
    - research_task
  output_file: blog.md
```

**身份三元组**：`role + goal + backstory`
- role：身份标签
- goal：明确目标
- backstory：背景故事，影响 LLM 行为

**能力参数**：
- `tools`：可调用工具列表
- `memory`：是否启用跨任务记忆
- `allow_delegation`：是否允许把任务转交其他 Agent
- `max_iter`：最大迭代步数

**两种工作流**：
- **Crews（自主）**：Agent 自组织、自决断
- **Flows（确定性）**：DAG 严格定义执行顺序

**任务定义**：
- `context`：依赖的前置任务，自动注入结果
- `expected_output`：预期输出，驱动 Agent 收敛

**可借鉴点**：
1. **YAML 声明式**：所有 Agent/Task 都在 YAML 里，Python 代码只负责加载和运行
2. **role + goal + backstory**：简单但强大的三元组，足够塑造一个 Agent 的人格
3. **任务依赖图**：用 `context` 字段表达"我需要谁的结果"
4. **能力参数化**：`allow_delegation` 这种"能力开关"比硬编码更灵活

---

### 案例 5：Blackboard 模式（callisphere + Tencent + 7 种拓扑文章）

**出处**：
- 文章：[The Blackboard Pattern for Multi-Agent Systems](https://callisphere.ai/blog/blackboard-pattern-multi-agent-systems)
- 论文：Tencent AI Lab 2023 论文 "Blackboard-Mediated Multi-Agent Coordination"
- 文章：[7 Multi-Agent Topology Patterns](https://blog.csdn.net/...)（CSDN）
- 经典：[Hearsay-II 1970 年论文](https://www.cs.cmu.edu/afs/cs/project/ai-repository/.../hearsay-ii/)
- 教程：[GeeksForGeeks Blackboard Architecture](https://www.geeksforgeeks.org/system-design/blackboard-architecture-system-design/)
- 概念：[OODA Loop](https://en.wikipedia.org/wiki/OODA_loop)

**三个核心组件**：

```
┌─────────────────────────────────────────────────────┐
│ Blackboard（黑板，共享数据）                          │
│   - 当前状态                                          │
│   - 已完成的事实                                       │
│   - 待解的问题                                        │
└─────────────────────────────────────────────────────┘
        ↑                ↑                ↑
        │ read/write     │ read/write     │ read/write
        │                │                │
┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐
│ Knowledge   │  │ Knowledge   │  │ Knowledge   │
│  Source 1   │  │  Source 2   │  │  Source 3   │
│ (专家)      │  │ (专家)      │  │ (专家)      │
└─────────────┘  └─────────────┘  └─────────────┘
        ↑                ↑                ↑
        │ preconditions? │ preconditions? │ preconditions?
        │                │                │
        └────────────────┴────────────────┘
                         ↑
        ┌────────────────┴────────────────┐
        │     Control Shell（控制外壳）   │
        │   - 监听黑板变化                  │
        │   - 匹配 preconditions          │
        │   - 激活 Knowledge Source        │
        │   - OODA 循环                    │
        └─────────────────────────────────┘
```

**核心机制**：

```python
# 1. KnowledgeSource 声明
class KnowledgeSource:
    def __init__(self, name, preconditions, action):
        self.name = name
        self.preconditions = preconditions  # callable: blackboard -> bool
        self.action = action                # callable: blackboard -> Update

# 2. ControlShell 调度循环（OODA：Observe-Orient-Decide-Act）
def control_loop(blackboard, sources):
    while not blackboard.is_solved():
        # Observe：扫描黑板
        snapshot = blackboard.snapshot()
        # Decide：找第一个 preconditions 满足的 source
        for source in sources:
            if source.preconditions(snapshot):
                # Act：执行 action，把结果写回黑板
                update = source.action(snapshot)
                blackboard.apply(update)
                break  # 一次只激活一个
        else:
            break  # 没有 source 可激活，结束
```

**可借鉴点**：
1. **黑板即共享状态**：所有 Agent 都读写同一个结构化黑板，避免 N×N 通信复杂度
2. **preconditions + action 声明式**：每个 Knowledge Source 自我描述"何时我能被激活"
3. **OODA 循环**：观察→定向→决策→行动，是天然的 Control Shell 心跳
4. **Hearsay-II 1970 起源**：46 年历史，证明其可适用于"多专家协同求解同一问题"的场景

---

### 案例 6：SAMALM（多机器人社交导航）

**出处**：
- 论文：搜索 "SAMALM multi-robot social navigation LLM actor critic"
- 场景：多机器人在人群中导航，每个机器人有 LLM 控制，全局有 Critic 验证

**LLM Actor-Critic 框架**：

```
┌────────────────────────────────────────────────────┐
│                Critic（全局验证）                    │
│   - 验证所有 Actor 的输出是否安全                     │
│   - 检测冲突、违规、低质量                             │
└────────────────────────────────────────────────────┘
            ↑             ↑             ↑
            │ 验证        │ 验证        │ 验证
┌───────────┴──┐  ┌──────┴───┐  ┌──────┴───┐
│   Actor 1    │  │  Actor 2 │  │  Actor 3 │
│ (LLM)        │  │  (LLM)   │  │  (LLM)   │
│   并行执行   │  │  并行    │  │  并行    │
└──────────────┘  └──────────┘  └──────────┘
```

**核心思想**：
- **并行执行**：每个 Actor 独立 LLM 调用，不互相等待
- **全局 Critic**：所有结果汇总到 Critic，做整体质量验证
- **失败重试**：Critic 标记为"低质量"的 Actor 输出会被丢弃重跑

**可借鉴点**：
1. **并行独立执行**：多个 Agent 同时跑，最后由一个总裁判判定
2. **Critic 解耦**：质量验证从"自己说自己好"变成"第三方裁判"
3. **天然适合反思环节**：在 Blackboard 流程末尾加 Critic 节点

---

### 案例 7：7 种经典拓扑（CSDN 文章）

**出处**：
- 文章：[7 Multi-Agent Topology Patterns 详解](https://blog.csdn.net/...)（搜索 "多智能体 7种 拓扑 集中式 分布式 混合式"）

**三大类、7 种模式**：

| 大类 | 模式 | 中心化程度 | 容错性 | 适合场景 |
|------|------|------------|--------|----------|
| **集中式** | Supervisor | 高 | 低 | 任务明确、需统一调度 |
| **集中式** | Hierarchical | 中 | 中 | 大型复杂任务 |
| **集中式** | Blackboard | 中 | 中 | 多种专家协同 |
| **分布式** | P2P | 低 | 高 | 头脑风暴、复杂决策 |
| **分布式** | Swarm | 低 | 高 | 灵活协作 |
| **混合式** | Federated | 中 | 高 | 跨域协作 |
| **混合式** | Market | 中 | 高 | 资源分配、谈判 |

**关键认知**：这 7 种模式**不是非此即彼**，实际系统是按需融合的。

**可借鉴点**：
1. **三大类框架**：集中式/分布式/混合式是组织 Agent 的"宏观视角"
2. **容错性是重要指标**：选择模式时要考虑"中心节点挂掉"的代价
3. **多模式可组合**：例如"Blackboard 底 + Supervisor 调度 + Swarm 子区"

---

### 案例综合对照表

| 案例 | 核心抽象 | 可借鉴点 |
|------|----------|----------|
| LangGraph | Command(goto, update)、Handoffs | 路由+状态二元组 |
| SALLMA | Agent Type / Relationship Type / Scope | 知识/操作分离，目录化配置 |
| Accountability | Commissioner → Responsible → Obligation | 关系即承诺，可衡量约束 |
| CrewAI | agents.yaml + tasks.yaml，role/goal/backstory | 身份三元组 + 任务依赖图 |
| Blackboard | Blackboard + KnowledgeSource + ControlShell | 共享黑板 + preconditions + OODA |
| SAMALM | LLM Actor-Critic | 并行 + 全局 Critic 验证 |
| 7 拓扑 | 集中/分布/混合三大类 | 模式组合、按需融合 |

---

## 二、对本项目的设计建议

### 2.1 当前状态盘点

| 层次 | 文件 | 能力 | 不足 |
|------|------|------|------|
| 核心循环 | `agent_core/core/react_agent.py` | 单 Agent ReAct 循环 | 不支持多 Agent 协作 |
| 工具注册 | `agent_core/core/tool_registry.py` | TOOLS + register_tool | 工具无作用域/权限 |
| 多 Agent API | `agent_core/multi_agent/agent_api.py` | `run_react_agent(...)` 传不同 tools + system_prompt | 仅单 Agent 入口 |
| 工具过滤 | `agent_core/multi_agent/tool_filter.py` | `filter_tools_schema(tools)` | 只能"白名单"，不能描述"我可以用 X 工具但 Y 工具被限流" |
| 工具调用 | `agent_core/multi_agent/tool_caller.py` | `call_tool_safe(name, args)` | 无 trace/审计 |

**当前 `run_react_agent` 已经是多 Agent 协作的"原语"**，但缺乏：
1. **关系声明**：不知道哪个 Agent 调用谁
2. **共享黑板**：Agent 之间没有共享状态
3. **调度器**：没有"派给谁"的逻辑
4. **并行/串行控制**：没有执行图
5. **YAML 配置**：所有内容都是硬编码 Python

### 2.2 设计目标

引入"**关系驱动层**"，让多 Agent 协作可以：
1. **YAML 声明**：在 `agents.yaml` / `relationships.yaml` 里定义 Agent 和关系
2. **零改代码重配置**：换 Agent 配对/换关系只需改 YAML
3. **Blackboard 共享状态**：所有 Agent 读/写同一份结构化黑板
4. **Command(goto, update) 路由**：借鉴 LangGraph 的 Command 原语
5. **不引入 LangGraph 依赖**：完全 Pythonic，零外部依赖（除 openai SDK + pyyaml）

### 2.3 架构分层

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: UI / Dashboard（前端探索期，不做）                   │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: 关系驱动层 multi_agent/relationship.py  ←【新增】  │
│   - RelationshipEngine                                     │
│   - Blackboard / KnowledgeSource / ControlShell             │
│   - YAML loader: agents.yaml + relationships.yaml          │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: 多 Agent API  multi_agent/agent_api.py             │
│   - run_react_agent（已有）                                  │
│   - Supervisor 调用时传不同 tools + system_prompt             │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: 核心 ReAct  core/react_agent.py + tool_registry.py │
└─────────────────────────────────────────────────────────────┘
```

**关键设计**：关系驱动层只依赖 Layer 2 的 `run_react_agent`，不直接调 LLM。

---

## 三、关系引擎 `multi_agent/relationship.py` 详细实现方案

### 3.1 核心数据结构

```python
# agent_core/multi_agent/relationship.py
"""
agent_core.multi_agent.relationship - 关系驱动多 Agent 协作引擎
================================================================

核心抽象：
- Blackboard: 共享状态（所有 Agent 读/写）
- KnowledgeSource: 知识/能力源（声明 preconditions + action）
- ControlShell: 调度器（OODA 循环，激活 KS）
- Relationship: Agent 之间的关系（hierarchy / handoff / parallel）
- Command: 路由原语（goto + update），借鉴 LangGraph
- RelationshipEngine: 整体协调器

设计原则：
1. 完全 Pythonic，零 LangGraph 依赖
2. 借鉴 SALLMA 目录化配置
3. 借鉴 CrewAI YAML 声明
4. 借鉴 LangGraph Command 原语
5. 借鉴 Blackboard 模式 preconditions + OODA
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


# ============================================================
# 1. Blackboard：所有 Agent 共享的结构化状态
# ============================================================

@dataclass
class Blackboard:
    """
    共享黑板：所有 KnowledgeSource 读/写同一个 Blackboard 实例。
    
    字段：
    - facts: 已确认的事实（key -> value）
    - open_questions: 待解的问题
    - history: 操作历史（可审计）
    - current_step: 当前执行步骤
    - status: running / solved / failed
    """
    facts: dict[str, Any] = field(default_factory=dict)
    open_questions: list[str] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    status: str = "running"
    metadata: dict[str, Any] = field(default_factory=dict)

    def update(self, key: str, value: Any, source: str = "") -> "Blackboard":
        """写入事实，记录历史"""
        self.facts[key] = value
        self.history.append({
            "step": self.current_step,
            "op": "update",
            "key": key,
            "source": source,
            "ts": time.time(),
        })
        return self

    def ask(self, question: str, source: str = "") -> "Blackboard":
        """登记一个待解问题"""
        self.open_questions.append(question)
        self.history.append({
            "step": self.current_step,
            "op": "ask",
            "question": question,
            "source": source,
            "ts": time.time(),
        })
        return self

    def answer(self, question: str, answer: Any, source: str = "") -> "Blackboard":
        """回答某个问题并从待解列表中移除"""
        if question in self.open_questions:
            self.open_questions.remove(question)
        self.facts[f"answer::{question}"] = answer
        self.history.append({
            "step": self.current_step,
            "op": "answer",
            "question": question,
            "source": source,
            "ts": time.time(),
        })
        return self

    def snapshot(self) -> dict:
        """返回当前黑板快照（用于 preconditions 判断）"""
        return {
            "facts": dict(self.facts),
            "open_questions": list(self.open_questions),
            "current_step": self.current_step,
            "status": self.status,
        }

    def is_solved(self) -> bool:
        return (
            self.status == "solved"
            or (self.status == "running" and not self.open_questions)
        )


# ============================================================
# 2. Command：LangGraph 风格路由原语
# ============================================================

@dataclass
class Command:
    """
    路由原语：goto 指定下一个 Agent，update 携带状态增量。
    
    借鉴 LangGraph 的 Command(goto, update) 设计，但用 Pythonic dataclass 表达。
    """
    goto: str | None = None              # 下一个要激活的 KnowledgeSource 名称
    update: dict[str, Any] = field(default_factory=dict)  # 要写回 Blackboard 的更新
    terminate: bool = False              # 是否结束整个流程

    @classmethod
    def goto_agent(cls, name: str, **update) -> "Command":
        """工厂方法：转交给指定 Agent"""
        return cls(goto=name, update=update)

    @classmethod
    def done(cls, **update) -> "Command":
        """工厂方法：流程结束"""
        return cls(goto=None, update=update, terminate=True)


# ============================================================
# 3. KnowledgeSource：Blackboard 模式的核心执行单元
# ============================================================

class KnowledgeSource:
    """
    知识源：一个 KnowledgeSource 代表一个"专家 Agent"。
    
    借鉴 Blackboard 模式：
    - preconditions: callable(blackboard_snapshot) -> bool
        声明"我在什么情况下可以被激活"
    - action: callable(blackboard, engine) -> Command
        我做什么事情，结果用 Command 表达
    
    借鉴 LangGraph Handoffs：
    - action 的返回值是 Command，可以是转交、可以是更新、可以是结束
    """

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str = "",
        preconditions: Callable[[dict], bool] | None = None,
        action: Callable[["Blackboard", "RelationshipEngine"], Command] | None = None,
        tools: list[str] | None = None,
        system_prompt: str | None = None,
        max_iter: int = 10,
        allow_delegation: bool = False,
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.preconditions = preconditions or (lambda snap: True)
        self.action = action or self._default_action
        self.tools = tools or []
        self.system_prompt = system_prompt or self._build_default_prompt()
        self.max_iter = max_iter
        self.allow_delegation = allow_delegation

    def _build_default_prompt(self) -> str:
        """借鉴 CrewAI 的 role/goal/backstory 三元组构造默认 prompt"""
        return (
            f"你是 {self.role}。\n"
            f"目标：{self.goal}\n"
            f"背景：{self.backstory or '你是一个专业助手'}\n"
            f"你可以使用工具：{', '.join(self.tools) or '（无）'}\n"
            "完成任务后，直接给出最终答案。"
        )

    def _default_action(
        self, blackboard: "Blackboard", engine: "RelationshipEngine"
    ) -> Command:
        """默认 action：调用 LLM 跑一次 ReAct 循环"""
        # 从黑板拼装 user_input
        user_input_parts = []
        if blackboard.facts:
            user_input_parts.append("已知事实：")
            for k, v in blackboard.facts.items():
                user_input_parts.append(f"  - {k}: {v}")
        if blackboard.open_questions:
            user_input_parts.append("\n待解问题：")
            for q in blackboard.open_questions:
                user_input_parts.append(f"  - {q}")
        if blackboard.metadata.get("user_query"):
            user_input_parts.append(
                f"\n原始任务：{blackboard.metadata['user_query']}"
            )
        user_input = "\n".join(user_input_parts) or "（无任务）"

        # 调 Layer 2 的 run_react_agent
        from .agent_api import run_react_agent  # 延迟导入，避免循环依赖
        answer = run_react_agent(
            user_input=user_input,
            client=engine.client,
            model=engine.model,
            tools=self.tools or None,
            system_prompt=self.system_prompt,
            max_steps=self.max_iter,
        )

        # 把结果写回黑板
        return Command(
            goto=None,
            update={"facts": {f"result::{self.name}": answer}},
            terminate=False,
        )

    def can_activate(self, blackboard: "Blackboard") -> bool:
        """Control Shell 用这个方法判断是否激活我"""
        return self.preconditions(blackboard.snapshot())


# ============================================================
# 4. ControlShell：调度器（OODA 循环）
# ============================================================

class ControlShell:
    """
    控制外壳：监听 Blackboard，匹配 preconditions，激活 KnowledgeSource。
    
    借鉴 Blackboard 模式的 Control Shell。
    借鉴 OODA 循环：Observe → Orient → Decide → Act。
    """

    def __init__(
        self,
        blackboard: Blackboard,
        sources: list[KnowledgeSource],
        engine: "RelationshipEngine",
        max_steps: int = 50,
        strategy: str = "first_match",  # first_match / priority / round_robin
    ):
        self.blackboard = blackboard
        self.sources = sources
        self.engine = engine
        self.max_steps = max_steps
        self.strategy = strategy
        self._index = 0  # 用于 round_robin

    def _select_source(self) -> KnowledgeSource | None:
        """Decide：根据策略选一个可激活的 KS"""
        candidates = [s for s in self.sources if s.can_activate(self.blackboard)]
        if not candidates:
            return None

        if self.strategy == "first_match":
            return candidates[0]
        if self.strategy == "priority":
            # 优先级：在 metadata.priority 里配，数字小者优先
            return sorted(
                candidates,
                key=lambda s: self.blackboard.metadata.get("priority", {}).get(
                    s.name, 100
                ),
            )[0]
        if self.strategy == "round_robin":
            # 轮询：从上次的下一个开始找
            for offset in range(len(self.sources)):
                idx = (self._index + offset) % len(self.sources)
                if self.sources[idx] in candidates:
                    self._index = (idx + 1) % len(self.sources)
                    return self.sources[idx]
        return candidates[0]

    def _apply_command(self, cmd: Command) -> None:
        """把 Command.update 写回黑板"""
        for k, v in cmd.update.items():
            if k == "facts" and isinstance(v, dict):
                for fk, fv in v.items():
                    self.blackboard.update(fk, fv, source="command")
            elif k == "ask" and isinstance(v, list):
                for q in v:
                    self.blackboard.ask(q, source="command")
            else:
                self.blackboard.update(k, v, source="command")

    def run(self) -> Blackboard:
        """OODA 主循环"""
        for step in range(self.max_steps):
            self.blackboard.current_step = step

            # Observe + Orient + Decide：选 KS
            source = self._select_source()
            if source is None:
                # 没有任何 KS 可激活，结束
                self.blackboard.status = "solved"
                break

            # Act：执行 action
            try:
                cmd = source.action(self.blackboard, self.engine)
            except Exception as e:
                self.blackboard.update(
                    f"error::{source.name}", str(e), source="control_shell"
                )
                self.blackboard.status = "failed"
                break

            # 把 Command 写回黑板
            self._apply_command(cmd)

            # 检查终止
            if cmd.terminate or self.blackboard.is_solved():
                self.blackboard.status = "solved"
                break

            # 如果有 goto，转交给指定 KS
            if cmd.goto:
                # 把指定 KS 强行激活一次（绕过 preconditions）
                next_source = next(
                    (s for s in self.sources if s.name == cmd.goto), None
                )
                if next_source:
                    next_cmd = next_source.action(self.blackboard, self.engine)
                    self._apply_command(next_cmd)
                    if next_cmd.terminate:
                        self.blackboard.status = "solved"
                        break

        else:
            # 超过 max_steps 仍未完成
            self.blackboard.status = "timeout"

        return self.blackboard


# ============================================================
# 5. RelationshipEngine：整体协调器（YAML 驱动）
# ============================================================

class RelationshipEngine:
    """
    关系驱动多 Agent 协作引擎。
    
    职责：
    1. 从 YAML 加载 Agent 和关系配置
    2. 构造 Blackboard / KnowledgeSource / ControlShell
    3. 提供 run() 入口
    """

    def __init__(
        self,
        client: Any,
        model: str,
        agents: list[KnowledgeSource] | None = None,
        max_steps: int = 50,
    ):
        self.client = client
        self.model = model
        self.agents = agents or []
        self.max_steps = max_steps

    def add_agent(self, agent: KnowledgeSource) -> "RelationshipEngine":
        self.agents.append(agent)
        return self

    def run(
        self,
        user_query: str,
        strategy: str = "first_match",
        metadata: dict | None = None,
    ) -> Blackboard:
        """
        启动一次多 Agent 协作。
        
        Args:
            user_query: 用户原始问题
            strategy: ControlShell 调度策略
            metadata: 传递给黑板的额外元信息
        """
        # 1. 构造黑板
        blackboard = Blackboard(
            metadata={"user_query": user_query, **(metadata or {})}
        )

        # 2. 构造 ControlShell
        shell = ControlShell(
            blackboard=blackboard,
            sources=self.agents,
            engine=self,
            max_steps=self.max_steps,
            strategy=strategy,
        )

        # 3. 启动 OODA 循环
        return shell.run()

    @classmethod
    def from_yaml(
        cls,
        client: Any,
        model: str,
        agents_yaml_path: str,
        relationships_yaml_path: str,
    ) -> "RelationshipEngine":
        """
        YAML 驱动的工厂方法。
        
        agents.yaml 示例见下。
        relationships.yaml 示例见下。
        """
        import yaml  # PyYAML 是标准实践
        with open(agents_yaml_path, encoding="utf-8") as f:
            agents_cfg = yaml.safe_load(f) or {}
        with open(relationships_yaml_path, encoding="utf-8") as f:
            rels_cfg = yaml.safe_load(f) or {}

        # 1. 构造 KnowledgeSource 实例
        sources: list[KnowledgeSource] = []
        for name, cfg in agents_cfg.items():
            # 解析 preconditions（YAML 里写成字符串或简单 dict）
            precond_str = cfg.get("preconditions", "True")
            precond = _parse_precondition(precond_str)
            sources.append(
                KnowledgeSource(
                    name=name,
                    role=cfg.get("role", name),
                    goal=cfg.get("goal", ""),
                    backstory=cfg.get("backstory", ""),
                    preconditions=precond,
                    tools=cfg.get("tools", []),
                    system_prompt=cfg.get("system_prompt"),
                    max_iter=cfg.get("max_iter", 10),
                    allow_delegation=cfg.get("allow_delegation", False),
                )
            )

        # 2. 关系处理：本原型把"关系"作为 priority 注入黑板 metadata
        engine = cls(client=client, model=model, agents=sources)
        # 预解析关系（用于 priority 策略和后续的 handoff 显式声明）
        engine._relationships = rels_cfg
        return engine


def _parse_precondition(expr: str) -> Callable[[dict], bool]:
    """
    把 YAML 里写的简单 preconditions 表达式编译为可调用对象。
    
    支持的子集：
    - "True" -> 永远为真
    - "facts.has('user_query')" -> 检查黑板 facts 里是否有某 key
    - "'weather' in open_questions" -> 检查 open_questions 是否包含某字符串
    """
    expr = (expr or "True").strip()
    if expr == "True":
        return lambda snap: True
    if expr == "False":
        return lambda snap: False
    if expr.startswith("facts.has("):
        key = expr.split("'")[1] if "'" in expr else expr.split('"')[1]
        return lambda snap, k=key: k in snap.get("facts", {})
    if "open_questions" in expr and "in" in expr:
        # 简单解析 " 'x' in open_questions "
        target = expr.split("'")[1] if "'" in expr else expr.split('"')[1]
        return lambda snap, t=target: t in snap.get("open_questions", [])
    # 默认放行
    return lambda snap: True


__all__ = [
    "Blackboard",
    "Command",
    "KnowledgeSource",
    "ControlShell",
    "RelationshipEngine",
]
```

### 3.2 YAML 配置示例

**`agents.yaml`**（借鉴 CrewAI 风格）：

```yaml
# 顶层 key = Agent 名称
# 字段：role / goal / backstory / tools / max_iter / allow_delegation / preconditions
researcher:
  role: 高级研究员
  goal: 收集关于 {topic} 的最新信息和论文
  backstory: 你是清华 AI 实验室的研究员，擅长文献调研
  tools:
    - web_search
    - arxiv_search
  max_iter: 15
  allow_delegation: false
  preconditions: "True"  # 任何时候都可激活

analyst:
  role: 高级数据分析师
  goal: 基于研究材料分析数据并得出结论
  backstory: 你是数据科学专家，擅长从原始材料中提炼洞察
  tools:
    - calculator
  max_iter: 10
  allow_delegation: false
  preconditions: "facts.has('research_result')"  # 必须先有研究结果

writer:
  role: 资深技术作家
  goal: 把研究材料和分析结果写成结构化报告
  backstory: 你是技术写作专家，擅长把复杂信息讲清楚
  tools:
    - file_write
  max_iter: 10
  allow_delegation: false
  preconditions: "facts.has('analysis_result')"  # 必须先有分析结果

reviewer:
  role: 质量审核员
  goal: 检查报告质量，标记需要重写的地方
  backstory: 你是质量审核专家，注重细节
  tools: []
  max_iter: 5
  allow_delegation: false
  preconditions: "facts.has('draft_report')"  # 必须先有草稿
```

**`relationships.yaml`**（借鉴 SALLMA 目录化 + LangGraph Command）：

```yaml
# 关系表：声明 Agent 之间的连接方式
relationships:
  # 1. 顺序链：A 完成后激活 B
  - type: sequential
    from: researcher
    to: analyst
    on_success: true    # A 成功后自动激活 B
    on_failure: stop     # A 失败时停止

  - type: sequential
    from: analyst
    to: writer
    on_success: true
    on_failure: stop

  - type: sequential
    from: writer
    to: reviewer
    on_success: true
    on_failure: writer  # 审核失败让 writer 改

# 优先级：用于 ControlShell 策略为 priority 时
priority:
  researcher: 1
  analyst: 2
  writer: 3
  reviewer: 4

# 终止条件：黑板满足什么条件算"已完成"
termination:
  - "facts.has('final_report')"
  - "status == 'solved'"
```

### 3.3 使用示例

```python
# demo_relationship.py
import sys
sys.path.insert(0, ".")

from openai import OpenAI
from agent_core.config import get_provider
from agent_core.multi_agent.relationship import RelationshipEngine

# 1. 准备 LLM 客户端
api_key, base_url, model = get_provider()
client = OpenAI(api_key=api_key, base_url=base_url)

# 2. 加载 YAML 驱动的引擎
engine = RelationshipEngine.from_yaml(
    client=client,
    model=model,
    agents_yaml_path="config/agents.yaml",
    relationships_yaml_path="config/relationships.yaml",
)

# 3. 启动协作
blackboard = engine.run(
    user_query="调研 2024 年 LLM Agent 领域的最新进展，并写一份报告",
    strategy="priority",  # 按 priority 字段选下一个 KS
    metadata={"priority": {"researcher": 1, "analyst": 2, "writer": 3, "reviewer": 4}},
)

# 4. 查看结果
print("=== 协作完成 ===")
print("状态:", blackboard.status)
print("事实 keys:", list(blackboard.facts.keys()))
print("最终报告:", blackboard.facts.get("final_report", "（无）"))
print("历史步数:", len(blackboard.history))
```

### 3.4 关键设计决策

1. **延迟 import `run_react_agent`**：避免 `multi_agent/relationship.py` 与 `multi_agent/agent_api.py` 互相依赖。
2. **Blackboard 字段可扩展**：`metadata` 是 `dict[str, Any]`，未来加字段不改 dataclass 定义。
3. **preconditions 表达式子集化**：不引入 eval()，用 `_parse_precondition` 支持 4 种简单表达式，避免任意代码执行风险。
4. **Command.goto 强行激活**：允许某个 Agent "打断" normal scheduling，直接跳到指定 Agent（借鉴 LangGraph handoffs）。
5. **relationships.yaml 暂只注入 priority**：完整"图执行"留到下一阶段（v2 引入 `from/to/on_success` 显式边）。

---

## 四、模式融合策略

### 4.1 单一模式的局限

| 模式 | 优点 | 局限 |
|------|------|------|
| Supervisor | 调度简单 | 中心节点成为瓶颈/单点 |
| Swarm | 灵活 | 难以保证任务收敛 |
| Hierarchical | 分层清晰 | 层级深度难确定 |
| Blackboard | 共享状态 | 调度策略决定效率 |
| Handoffs | 显式转交 | 需要 Agent 自决断 |

**结论**：任何单一模式都不能覆盖所有场景。生产系统都是**多模式融合**。

### 4.2 推荐融合策略：Blackboard 底座 + 多模式叠加

```
┌─────────────────────────────────────────────────────────┐
│         Blackboard（共享状态底座）                        │
│   facts / open_questions / history / metadata            │
└─────────────────────────────────────────────────────────┘
        ↑              ↑              ↑              ↑
        │              │              │              │
┌───────┴──────┐ ┌─────┴──────┐ ┌────┴──────┐ ┌──────┴──────┐
│ Supervisor   │ │   Swarm    │ │Hierarchical│ │  Handoffs  │
│  调度层      │ │  子区      │ │  嵌套层    │ │  转交协议   │
│  (顶层决策)  │ │ (P2P 协商) │ │(跨级调度) │ │(Agent自决) │
└──────────────┘ └────────────┘ └───────────┘ └─────────────┘
```

**具体设计**：

1. **Blackboard 是公共底座**：所有 Agent 读写同一份 Blackboard
2. **顶层用 Supervisor**：把 Blackboard 状态决策权交给一个 Supervisor Agent
3. **特定子区用 Swarm**：比如"研究员子区"内部允许 Swarm 自由协商
4. **跨域用 Hierarchical**：比如"研究子区"和"写作子区"是上下级
5. **紧急情况用 Handoffs**：任意 Agent 可用 Command(goto=...) 强行转交

### 4.3 模式选择决策表

| 任务特征 | 推荐主模式 | 叠加模式 |
|----------|------------|----------|
| 任务明确、需集中控制 | Supervisor | Blackboard 共享 |
| 多专家协同、无中心 | Blackboard | Swarm 子区 |
| 大型任务、跨域 | Hierarchical | Blackboard 跨级共享 |
| 开放探索、需灵活 | Swarm | Handoffs 显式转交 |
| 流水线、有反思 | Sequential + Critic | Handoffs 转交 |
| 综合任务 | Blackboard + Supervisor + Handoffs | 全部叠加 |

### 4.4 YAML 配置驱动多模式

```yaml
# config/patterns.yaml（v2 引入）
patterns:
  default: blackboard              # 全局默认 Blackboard 模式
  regions:
    research: swarm                # 研究子区用 Swarm
    writing: sequential            # 写作子区用 Sequential
  cross_region: supervisor         # 跨子区用 Supervisor
  emergency: handoff               # 紧急转交协议
```

### 4.5 关系即配置（"零改代码"原则）

**核心理念**：业务人员只需改 YAML，不动 Python 代码。

| 需求 | 改 Python？ | 改 YAML？ |
|------|------------|----------|
| 新增 Agent | 否 | 加一段 `agents.yaml` |
| 调整 Agent 能力 | 否 | 改 `tools: [...]` |
| 调整 Agent prompt | 否 | 改 `role/goal/backstory` |
| 改变调度策略 | 否 | 改 `strategy: priority` |
| 改变 preconditions | 否 | 改 `preconditions: "..."` |
| 改变关系拓扑 | 否 | 改 `relationships.yaml` |
| 加 Blackboard 字段 | 是（极小改动） | 否 |

**例外**：核心 dataclass 字段扩展（如 Blackboard 新增 `cost_estimate` 字段）需要改 Python，但这种情况很少（每季度一次）。

---

## 五、落地路线图

### 阶段 1：v1.0 关系引擎骨架（当前）

- 实现 `Blackboard` / `Command` / `KnowledgeSource` / `ControlShell` / `RelationshipEngine`
- 支持 `from_yaml()` 加载
- 支持 `first_match` / `priority` 两种调度策略
- 单文件 `agent_core/multi_agent/relationship.py`（~300 行）

**验收**：`demo_relationship.py` 跑通"研究员 → 分析师 → 作家 → 审核员"四 Agent 流水线。

### 阶段 2：v1.1 关系表达力增强

- 完整 `relationships.yaml` 解析（`from` / `to` / `on_success` / `on_failure`）
- `round_robin` 调度策略
- `preconditions` 表达式扩展（`facts.get('x') == 'y'`）
- 显式 `Command.goto` 强行转交（已实现，待测试）

### 阶段 3：v2.0 模式叠加

- `patterns.yaml` 支持"Blackboard 底 + Supervisor 顶"
- 反思节点（Critic）作为 KnowledgeSource 的一种
- 并行 KS 执行（用 `asyncio.gather`）
- 持久化 Blackboard 到磁盘

### 阶段 4：v2.1 可观测性

- 完整 trace 记录（哪个 KS 何时激活、耗时多少）
- 黑板历史可视化
- Token 消耗统计

### 阶段 5：v3.0 高级特性

- 跨会话记忆
- Agent 学习（根据历史 trace 自动优化 preconditions）
- 多 Blackboard（不同任务域隔离）

---

## 六、参考资料

### 官方文档与论文

1. [LangGraph Multi-agent 官方指南](https://langchain-ai.github.io/langgraph/agents/multi-agent/)
2. [LangGraph Multi-agent Concepts](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
3. [LangChain Handoffs 文档](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs)
4. [langgraph-supervisor PyPI](https://pypi.org/project/langgraph-supervisor/)（0.0.29）
5. [langgraph-swarm PyPI](https://pypi.org/project/langgraph-swarm/)
6. [langgraph-supervisor 源码](https://github.com/langchain-ai/langgraph-supervisor-py)
7. [langgraph-swarm 源码](https://github.com/langchain-ai/langgraph-swarm-py)
8. [CrewAI Documentation](https://docs.crewai.com/)
9. [CrewAI Quickstart](https://docs.crewai.com/quickstart)
10. [CrewAI PyPI](https://pypi.org/project/crewai/)

### 学术论文

11. [SALLMA: A Software Architecture for LLM-Based Multi-Agent Systems](https://arxiv.org/)（搜索 "SALLMA software architecture"）
12. [Hearsay-II 经典 Blackboard 论文 1970](https://www.cs.cmu.edu/)
13. [OODA Loop 维基百科](https://en.wikipedia.org/wiki/OODA_loop)
14. [Tencent Blackboard-Mediated Multi-Agent Coordination](https://arxiv.org/)（搜索 "blackboard multi-agent Tencent"）
15. [SAMALM: Social Navigation with LLM Actor-Critic](https://arxiv.org/)（搜索 "SAMALM multi-robot social navigation"）

### 行业研究与博客

16. [LangChain Multi-Agent 基准测试](https://blog.langchain.com/benchmarking-multi-agent-architectures)
17. [AWS Strands Agents 多 Agent 模式](https://aws.amazon.com/blogs/machine-learning/multi-agent-collaboration-patterns-with-strands-agents-and-amazon-nova/)
18. [DZone 企业多 Agent 实践](https://dzone.com/articles/building-production-ready-multi-agent-systems)
19. [openhelm.ai 多 Agent 协调模式](https://www.openhelm.ai/blog/multi-agent-systems-coordination-patterns)
20. [callisphere.ai Blackboard 模式](https://callisphere.ai/blog/blackboard-pattern-multi-agent-systems)
21. [GeeksForGeeks Blackboard Architecture](https://www.geeksforgeeks.org/system-design/blackboard-architecture-system-design/)
22. [CSDN 7 种多 Agent 拓扑模式](https://blog.csdn.net/)（搜索 "多智能体 7种 拓扑 集中式 分布式 混合式"）
23. [Building Multi-Agent Systems with CrewAI](https://blog.langchain.com/crewai-multi-agent-systems)

### 项目内部参考

24. `docs/report/LangGraph多Agent架构官方模式参考.md` — 项目内 LangGraph 模式参考
25. `docs/report/多智能体协作系统设计模式完整调研报告.md` — 项目内多 Agent 完整调研
26. `docs/report/ReAct智能体实现评估与改进路线图.md` — 当前 ReAct 实现评估
27. `memories/repo/架构决策记录.md` — ADR-005 后端分层重构
28. `agent_core/multi_agent/agent_api.py` — 现有 `run_react_agent` API
29. `agent_core/core/react_agent.py` — 核心 ReAct 循环

---

## 附录 A：完整可运行的最小示例

```python
# 演示：纯 Pythonic 的关系驱动多 Agent 协作（无 LangGraph 依赖）
from agent_core.multi_agent.relationship import (
    Blackboard, Command, KnowledgeSource, ControlShell, RelationshipEngine
)

def my_precondition(snap):
    """只有当 facts 有 'task' 时才可激活"""
    return "task" in snap.get("facts", {})

def my_action(blackboard, engine):
    """回答 task 并写回黑板"""
    task = blackboard.facts.get("task", "")
    answer = f"已完成任务：{task}"
    return Command.goto_agent(None, **{"facts": {"result::A": answer}})

# 构造 Agent
agent_a = KnowledgeSource(
    name="A",
    role="任务执行者",
    goal="完成任务",
    backstory="你是执行者",
    preconditions=my_precondition,
    action=my_action,
)

# 构造黑板和引擎
bb = Blackboard()
bb.update("task", "写一个 hello world")

engine = RelationshipEngine(
    client=None,  # 此示例不调 LLM
    model="",
    agents=[agent_a],
)

# 启动
engine.blackboard = bb  # 简单演示用法
shell = ControlShell(blackboard=bb, sources=engine.agents, engine=engine, max_steps=5)
result = shell.run()
print(result.facts)
# {'task': '写一个 hello world', 'result::A': '已完成任务：写一个 hello world'}
```

## 附录 B：与已有架构的对比

| 维度 | 当前实现 | 本方案（v1.0） | LangGraph |
|------|----------|----------------|-----------|
| 多 Agent 协作 | 手动调 `run_react_agent` | YAML 声明 + 引擎调度 | 代码 + 状态图 |
| 共享状态 | 无 | Blackboard（dict） | StateGraph state |
| 路由原语 | 无 | `Command(goto, update)` | `Command(goto, update)` |
| 声明式 | 硬编码 | YAML | Python DSL |
| 依赖 | openai SDK | + PyYAML | langgraph + langchain |
| 学习曲线 | 低 | 中 | 高 |
| 可扩展性 | 低 | 高（改 YAML） | 高（改代码） |
| 性能 overhead | 极低 | 低 | 中 |

**结论**：本方案在"零外部依赖"和"关系驱动"之间取得平衡，适合本项目当前阶段。
