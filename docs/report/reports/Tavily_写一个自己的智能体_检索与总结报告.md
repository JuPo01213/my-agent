# Tavily：写一个自己的智能体——检索与总结报告

## 检索策略说明

本报告采用 Tavily 风格的多轮检索策略，覆盖基础信息与深度内容：

| 阶段 | 检索方式 | 目标 |
|------|----------|------|
| **Round 1 – Basic + General** | 向权威来源发起宽泛查询（Anthropic、LangChain、CrewAI、MCP） | 获取“写智能体需要什么信息”“成熟架构是什么”的公开共识 |
| **Round 2 – Advanced + Domain Filtering** | 针对核心框架官方文档（LangChain agents、LangSmith、LangGraph）做深入抓取 | 提取框架级架构模式、Middleware 能力、生产化组件 |
| **Round 3 – Answer Summary + Synthesize** | 对 Anthropic、LangChain 两篇核心长文做结构化提炼 | 整合工作流模式、Agent 循环、工具工程、多智能体设计 |
| **Round 4 – GitHub 交叉验证** | 检索 langchain-ai org 下多智能体项目代码 | 验证 supervisor/subagent 模式在真实开源项目中的落地方式 |

---

## 1. 信息需求：启动一个智能体项目前，你需要准备什么？

### 1.1 核心决策信息

- **任务边界**：明确是“封闭式工作流”还是“开放式 Agent”。Anthropic 区分得很清楚：Workflows 是预定义代码路径，Agents 是 LLM 动态控制过程。先判断你的问题是否需要自主决策，再决定是否用 Agent。
- **成功标准**：能否量化？编码任务可用自动化测试验证，客服可用“解决率”衡量。没有清晰评估标准，不建议上 Agent。
- **复杂度预算**：从最简单的 Prompt 开始，用 single LLM call + 检索 + few-shot 先做 baseline。只有简单方案证明不够时，再升级到多步 Agentic 系统。

### 1.2 技术栈信息

- **模型选择**：你需要知道目标模型的工具调用能力、上下文窗口、成本与延迟。LangChain 已支持 OpenAI、Anthropic、Google、OpenRouter、Ollama 等，模型切换只需改一行字符串。
- **工具与数据接入**：需要哪些外部系统？搜索、数据库、文件系统、代码执行器？Anthropic 推荐用 Model Context Protocol（MCP）作为标准化接入层。
- **记忆与状态**：短期对话历史用 thread_id + checkpointer；长期记忆、知识库、技能注入用 Deep Agents 的 MemoryMiddleware、SkillsMiddleware、SummarizationMiddleware。
- **可观测性**：生产环境必须追踪 tool call 轨迹、延迟、token 消耗、错误率。LangSmith 提供了从 tracing → monitoring → insights 的完整链路。

### 1.3 工程与合规信息

- **安全与合规**：PII 检测、内容策略、人工审批节点。LangChain 提供了 PIIMiddleware 和 HumanInTheLoopMiddleware。
- **容错设计**：rate limit、模型超时、API 错误需要重试与回退。LangChain 的 ModelRetryMiddleware 和 ToolRetryMiddleware 是现成方案。
- **数据驻留**：若敏感数据不能出域，需考虑自托管或 BYOC 方案（LangSmith 支持 VPC/K8s 自托管）。

---

## 2. 成熟架构模式

### 2.1 增强型 LLM（Augmented LLM）

这是所有 Agentic 系统的基石。一个增强型 LLM = 基础模型 + 检索（RAG）+ 工具（Tools）+ 记忆（Memory）。  
关键原则：**工具定义本身就是一种 prompt engineering**。Anthropic 在 SWE-bench 编码 Agent 中发现，优化工具接口（如把相对路径改为绝对路径）比优化整体 prompt 投入产出比更高。

### 2.2 五种主流工作流模式（来自 Anthropic 公开共识）

| 模式 | 适用场景 | 核心机制 |
|------|----------|----------|
| **Prompt Chaining** | 任务可拆成固定子步骤 | 顺序调用，中间加 gate 校验 |
| **Routing** | 输入类型差异大，需要专门处理 | 先分类，再分发给下游处理 |
| **Parallelization** | 子任务独立或需要多视角 | Sectioning（分块并行）或 Voting（多数表决） |
| **Orchestrator-Workers** | 子任务不可预测 | 中心 LLM 动态拆解、委派、汇总 |
| **Evaluator-Optimizer** | 有明确评估标准，可迭代优化 | 生成 → 评估 → 反馈循环 |

### 2.3 自主 Agent 循环

当工作流无法覆盖时，使用自主 Agent：
1. **接收任务**：用户指令或对话澄清
2. **规划**：生成计划或 todo（LangChain TodoListMiddleware）
3. **行动循环**：调用工具 → 获得环境反馈 → 评估进度
4. **停止条件**：任务完成、达到最大轮次、遇到人工介入点

Anthropic 强调：Agent 实现通常很简洁——"LLM + tools in a loop"。复杂度应体现在工具集设计和文档上，而不是循环逻辑本身。

### 2.4 多智能体架构

真实项目中的多智能体模式正在成熟：
- **Supervisor 模式**：中心调度器（supervisor）根据上下文决定调用哪个专业 Agent（LangGraph Supervisor 开源项目已落地）
- **SubAgent 委派**：LangChain 的 SubAgentMiddleware 允许主 Agent 把子任务交给隔离上下文的子 Agent，支持并行与异步
- **CrewAI 模式**：Agents（角色）→ Crews（协作流程）→ Flows（事件驱动编排），并提供企业级触发器（Gmail、Slack、Salesforce）

### 2.5 执行环境（Execution Environment）

成熟的 Agent 需要“工作台”：
- **文件系统**：跨轮次读写文件（LangChain Deep Agents FilesystemMiddleware）
- **代码执行**：运行脚本或 shell 命令（Sandboxes / Interpreters）
- **状态持久化**：用 LangGraph checkpointer（如 InMemorySaver、Postgres）保存对话历史

---

## 3. 主流框架与工具

### 3.1 LangChain / LangGraph / Deep Agents

| 组件 | 定位 | 关键能力 |
|------|------|----------|
| **LangChain** | 应用层框架 | `create_agent` 提供最小可配置 harness；多模型统一接口 |
| **LangGraph** | 低层编排 | 图结构工作流、持久化、断点调试、时间旅行、多智能体 |
| **Deep Agents** | 开箱即用 | 文件系统、上下文压缩、子 Agent 生成、prompt caching 默认集成 |
| **LangSmith** | 可观测性 | Tracing、Monitoring、在线 Eval、LangSmith Engine 自动检测问题 |

**成熟架构建议**：从 `create_agent` 起步，按需加 middleware；复杂编排用 LangGraph；需要长期运行或文件操作时用 Deep Agents；生产环境必接 LangSmith。

### 3.2 CrewAI

- 定位：低代码/配置驱动的多 Agent 生产平台
- 特点：Agents（角色定义）+ Tasks（任务）+ Processes（顺序/层次/混合流程）+ Flows（事件驱动）
- 企业能力：自动化部署、触发器集成（Gmail、Slack 等）、RBAC 团队管理
- 适用场景：希望快速搭建多角色协作、且需要企业运维能力的团队

### 3.3 AutoGen（Microsoft）

- 定位：多 Agent 对话框架
- 特点：Agent 之间通过对话协作，支持人类介入、代码执行、工具调用
- 虽然本次抓取遇到技术问题，但公开资料显示其核心是“对话驱动的多智能体编排”

### 3.4 MCP（Model Context Protocol）

- 定位：AI 应用与外部系统的“USB-C 接口”
- 能力：统一接入数据源、工具、工作流
- 生态：Claude、ChatGPT、VS Code、Cursor 等已支持
- 价值：减少重复集成成本，一次构建到处运行

---

## 4. 成熟架构的最佳实践总结

1. **保持简单**：从单 LLM call + 检索开始，证明不够再升级。
2. **工具优先**：投入与 HCI 同等精力设计 Agent-Computer Interface（ACI）。工具名、参数、描述、示例要像写给 junior 开发者的 docstring。
3. **透明可观测**：每一步 tool call、状态转换、延迟都要可追踪。LangSmith 是目前生态中最成熟的方案。
4. **上下文工程**：Summarization 压缩历史、Memory 跨会话记忆、Skills 按需加载、Prompt caching 降本。
5. **容错与安全**：重试、退避、PII 过滤、人工审批、最大迭代次数——这些不是可选项，是生产必要项。
6. **框架选型原则**：
   - 快速原型/简单流程 → LangChain `create_agent`
   - 复杂有向图/多智能体 → LangGraph
   - 低代码企业部署 → CrewAI
   - 统一工具接入 → MCP
7. **不要框架成瘾**：Anthropic 和 LangChain 都建议——先理解底层，再决定是否用框架。框架是加速器，不是拐杖。

---

## 5. 可立即复用的架构清单

```
一个成熟智能体 = 
  ├── Model（LLM 选型 + 提供商抽象）
  ├── Tools（外部能力接入，推荐 MCP）
  ├── Memory（短期 thread + 长期 persistent）
  ├── Execution Environment（文件系统 / 代码执行 / 沙箱）
  ├── Orchestration（单 Agent 循环 or 多 Agent 路由/委派）
  ├── Observability（Tracing / Monitoring / Eval）
  ├── Safety（PII / 内容策略 / 人工介入点）
  └── Fault Tolerance（重试 / 退避 / 熔断）
```

---

**数据来源**：Anthropic Engineering、LangChain 官方文档、CrewAI 官网、Model Context Protocol 官方文档、LangGraph 开源项目代码。
