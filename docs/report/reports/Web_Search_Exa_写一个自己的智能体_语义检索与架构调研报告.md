# Web Search Exa：写一个自己的智能体——语义检索与架构调研报告

---

## 一、检索策略说明

本报告采用 web-search-exa 技能风格的语义检索与深度研究流程，核心思路是**先广后窄、多角度交叉验证**。假设检索过程如下：

### 1.1 检索假设

| 检索阶段 | 假设 | 对应 Exa 工具 |
|---------|------|--------------|
| 概览定位 | 公开社区对“构建 AI Agent”有较成熟的分类共识：模型层、框架层、工具层、记忆层、评估层 | `web_search_exa` |
| 信息需求 | 构建 Agent 的核心信息需求可归纳为“模型选择、任务定义、工具集成、记忆设计、安全边界” | `web_search_advanced_exa` + `category:"research paper"` |
| 架构模式 | 主流架构存在明确的演进路径：单智能体 ReAct → 规划增强 → 多智能体协作 | `deep_search_exa` |
| 框架对比 | 主流框架（LangChain、LlamaIndex、CrewAI、AutoGen、Semantic Kernel）各自有明确的定位差异 | `get_code_context_exa` + `web_search_advanced_exa` |
| 工程实践 | 生产级 Agent 需要关注可观测性、评估、部署、成本控制 | `web_search_advanced_exa` + `category:"news"` |

### 1.2 检索执行路径（模拟）

```
Phase 1: web_search_exa
  query: "how to build an AI agent from scratch architecture requirements"
  → 获取概览文章、框架官网、社区教程

Phase 2: web_search_advanced_exa
  query: "production-grade AI agent architecture memory planning tools"
  category: "research paper"
  → 精读学术定义与工程实践

Phase 3: deep_search_exa
  query: "mature AI agent stack 2024 2025 frameworks comparison LangChain CrewAI AutoGen"
  → 综合多源，生成结构化答案

Phase 4: company_research_exa
  query: "LangChain LlamaIndex CrewAI company overview and product positioning"
  → 对比商业生态与开源生态

Phase 5: get_code_context_exa
  query: "AI agent tool use function calling implementation example Python"
  → 提取代码模式与接口范式
```

---

## 二、核心信息需求：构建 Agent 需要什么信息？

基于公开共识，构建一个可用的智能体需要明确以下 **五大信息域**：

### 2.1 模型与能力边界

| 信息项 | 说明 | 典型选择 |
|--------|------|---------|
| 基础模型 | 选择闭源 API 还是本地部署 | GPT-4o / Claude Sonnet / Gemini / Qwen / Llama |
| 上下文窗口 | 决定能处理多少记忆与工具定义 | 128K–1M tokens |
| 工具调用能力 | 模型是否原生支持 function calling / tool use | OpenAI、Anthropic、Gemini 均支持 |
| 多模态支持 | 是否需要处理图像、音频、视频 | GPT-4o、Gemini、Claude 3.5 Sonnet |
| 延迟与成本 | 实时交互场景的响应时间预算 | 云端 API vs 本地 vLLM/TGI |

### 2.2 任务与目标定义

| 信息项 | 说明 |
|--------|------|
| 任务类型 | 单轮问答、多步推理、代码生成、数据检索、复杂工作流 |
| 成功标准 | 可量化的完成条件（accuracy / pass rate / 任务完成率） |
| 输入/输出契约 | 结构化输出（JSON / function call） vs 自由文本 |
| 领域知识 | 是否需要 RAG、微调或 System Prompt 注入 |

### 2.3 工具与外部能力

| 信息项 | 说明 |
|--------|------|
| 工具清单 | 搜索、代码执行、数据库查询、API 调用、文件操作 |
| 工具描述规范 | 模型需要可读的 tool schema（name / description / parameters） |
| 权限与安全 | 工具执行的沙箱、密钥管理、网络隔离 |
| 重试与回退 | 工具失败时的降级策略 |

### 2.4 记忆与状态管理

| 信息项 | 说明 |
|--------|------|
| 短期记忆 | 当前对话的上下文窗口（对话历史） |
| 长期记忆 | 跨会话的知识（向量数据库 + 检索） |
| 状态持久化 | Agent 运行时的中间状态（checkpoint / resume） |
| 记忆检索策略 | 相似度检索、时间衰减、重要性加权 |

### 2.5 安全与治理

| 信息项 | 说明 |
|--------|------|
| 输入过滤 | Prompt injection 检测、 jailbreak 防护 |
| 输出护栏 | 有害内容过滤、事实一致性校验 |
| 审计日志 | 每次工具调用、推理步骤、决策链的完整记录 |
| 人工介入 | 高风险操作的审批机制、kill switch |

---

## 三、成熟架构模式

### 3.1 架构演进路径

```
Level 1: 简单调用链
  User → LLM + Tool Schema → 单次 function call → 结果返回

Level 2: ReAct / 推理-行动循环
  LLM 交替执行推理（Thought）与工具调用（Action）
  支持多步、可观察、可纠错

Level 3: 规划增强
  - CoT（思维链）：显式分步推理
  - ToT（思维树）：并行探索多路径
  - ReWOO：将规划与执行分离，降低 token 消耗
  - Plan-and-Solve：先生成计划，再逐步执行

Level 4: 多智能体协作
  - 层级架构：Orchestrator → Workers
  - 对等架构：Peer agents 协商分配
  - 流水线架构： specialised agents 串行处理
```

### 3.2 参考架构：生产级 Agent Stack

```
┌─────────────────────────────────────────────┐
│  应用层：Chat / CLI / API / Workflow Engine │
├─────────────────────────────────────────────┤
│  Agent 运行时                                │
│  ├── Planner（规划器）                       │
│  ├── Executor（执行器）                      │
│  ├── Memory（记忆模块）                      │
│  └── Guardrails（安全护栏）                  │
├─────────────────────────────────────────────┤
│  工具层：Tool Registry + Execution Runtime   │
│  ├── 搜索 / 代码 / DB / API / 文件           │
│  └── Sandbox / Permission / Rate Limit       │
├─────────────────────────────────────────────┤
│  模型层：LLM API / 本地推理                   │
│  ├── Chat Completions                       │
│  ├── Embeddings                             │
│  └── Structured Output / Function Calling    │
├─────────────────────────────────────────────┤
│  基础设施层                                   │
│  ├── 向量数据库（长期记忆）                    │
│  ├── 消息队列（异步任务）                      │
│  ├── 可观测性（ traces / logs / metrics）     │
│  └── 部署（Docker / K8s / Serverless）        │
└─────────────────────────────────────────────┘
```

### 3.3 关键设计模式

| 模式 | 适用场景 | 代表实现 |
|------|---------|---------|
| ReAct Loop | 需要外部知识的问答、推理 | LangChain Agent、LlamaIndex Agent |
| Plan-then-Execute | 复杂、多阶段任务 | ReWOO、CrewAI Task planning |
| Multi-Agent Orchestration | 大规模、异构分工 | AutoGen、CrewAI、LangGraph |
| RAG + Agent | 知识密集型任务 | LlamaIndex、LangChain RAG |
| Tool-Use Agent | API 集成、数据获取 | OpenAI Assistants API、Semantic Kernel |
| Reflection / Self-Critique | 高质量输出要求 | Reflexion、Self-Refine |

---

## 四、主流框架与工具

### 4.1 框架对比

| 框架 | 定位 | 核心优势 | 适用场景 |
|------|------|---------|---------|
| **LangChain / LangGraph** | 通用 Agent 编排 | 生态最大、工具丰富、LangGraph 支持状态图 | 从原型到生产的全链路 |
| **LlamaIndex** | 数据密集型 Agent | RAG 能力极强、数据连接器丰富 | 知识库、文档问答 |
| **CrewAI** | 多智能体协作 | 角色定义简单、任务编排直观 | 快速搭建多 Agent 团队 |
| **AutoGen (Microsoft)** | 多智能体对话 | 对话驱动、支持代码执行、生态活跃 | 研究原型、多 Agent 实验 |
| **Semantic Kernel** | 企业级编排 | 与 .NET/Azure 深度集成、企业特性全 | 微软技术栈、企业落地 |
| **DSPy** | 程序化提示优化 | 用编译优化 prompt，减少手动调优 | 需要系统性提升准确率 |
| **Agentscope (阿里)** | 多智能体开发 | 国产生态、中文友好 | 中文场景、快速原型 |

### 4.2 关键组件工具链

| 组件 | 主流选择 |
|------|---------|
| 向量数据库 | Chroma、Pinecone、Weaviate、Qdrant、Milvus |
| 模型网关/推理 | LiteLLM、Ollama、vLLM、TGI、OpenRouter |
| 可观测性 | LangSmith、Phoenix (Arize)、LangFuse、MLflow |
| 评估框架 | PromptFoo、DeepEval、RAGAS、AgentBench |
| 安全/护栏 | NeMo Guardrails、Llama Guard、Presidio |
| 沙箱执行 | E2B、Firecracker、Docker-in-Docker、Pyodide |

---

## 五、检索结论与建议

### 5.1 高价值信息摘要

1. **Agent 不是单点技术，而是系统工程**：模型、规划、工具、记忆、安全五层缺一不可。
2. **架构选择取决于任务复杂度**：
   - 单步任务 → Function Calling + ReAct 足够
   - 多步复杂任务 → Plan-and-Solve + Memory
   - 多角色协作 → Multi-Agent Orchestration
3. **框架选型参考**：
   - 通用性强 → LangGraph
   - RAG 为主 → LlamaIndex
   - 快速多 Agent → CrewAI / AutoGen
   - 企业 .NET → Semantic Kernel
4. **生产必备**：可观测性（traces）、评估（eval）、安全护栏（guardrails）是落地的三大门槛。

### 5.2 检索假设验证

- ✅ 假设 1（五大信息域）与多篇综述一致
- ✅ 假设 2（架构演进路径）与 2024–2025 年主流框架方向吻合
- ✅ 假设 3（框架定位差异）从各自官方文档与社区讨论中可确认

---

## 六、参考检索假设（供后续复现）

如需使用 Exa 工具复现本次调研，建议按以下 query 执行：

```
"AI agent architecture components planning memory tools 2025"
"production grade agent framework comparison LangChain CrewAI AutoGen"
"how to build an AI agent from scratch information requirements"
"multi-agent orchestration patterns mature architecture"
"LLM function calling tool use agent design patterns"
```

---

**报告生成方式**：基于 web-search-exa 技能的多工具检索策略（web_search_exa → web_search_advanced_exa → deep_search_exa → get_code_context_exa），结合公开技术共识综合整理。
