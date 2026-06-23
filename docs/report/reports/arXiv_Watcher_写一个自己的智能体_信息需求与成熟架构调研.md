# arXiv Watcher：写一个自己的智能体——信息需求与成熟架构调研

> 本报告基于 2026 年 5–6 月 arXiv 最新论文调研，系统梳理构建自定义 LLM Agent 所需的信息清单与成熟架构模式。

---

## 一、调研背景与目标

"写一个自己的智能体"（Build Your Own Agent）已从概念验证走向工程实践。当前社区面临的核心问题不再是"能不能做"，而是"需要定义哪些信息"以及"应采用何种架构模式"。本报告旨在从最新 arXiv 论文中提炼可复用的设计清单与架构选型参考。

---

## 二、信息需求清单：构建自定义 Agent 前必须明确的维度

根据近期研究（尤其是 AgentSpec、HIPIF、MAS-PromptBench 等工作），在动手实现前，应系统回答以下七类问题：

### 2.1 能力边界（Capability Boundary）
- **任务类型**：是对话问答、代码生成、科研工作流，还是物理环境交互？
- **领域范围**：开放域通用任务，还是垂直领域（如气候科学、生物信息学）？
- **成功标准**：准确率、完成率、效率（token/时间成本），还是可审计性？
- **输入模态**：纯文本、多模态（图像/音频/视频），还是结构化数据？

### 2.2 工具与接口（Tools & Interfaces）
- **工具清单**：外部 API、数据库查询、代码解释器、文件系统、搜索引擎？
- **接口规范**：JSON Schema、OpenAPI、还是自然语言描述？
- **工具发现策略**：预定义全集注入，还是检索增强式动态发现（如 SING 的意图图）？
- **调用约束**：并发限制、频率限制、幂等性要求？

### 2.3 记忆系统（Memory）
- **记忆粒度**：短期对话历史、长期用户画像、还是可复用的经验/技能库？
- **存储形式**：Markdown 文件、向量数据库、图结构、还是 Git 版本控制（GitOfThoughts）？
- **写入策略**：全量保留还是主动压缩（MemRefine）？
- **跨会话一致性**：是否需要处理记忆偏差传播（Memory Contagion）？

### 2.4 规划与执行（Planning & Execution）
- **规划粒度**：高层任务分解（subgoal），还是细粒度动作序列？
- **规划时机**：执行前一次性规划（Plan-and-Execute），还是边执行边规划（ReAct）？
- **子目标管理**：是否需要显式子目标标记与折叠（HIPIF）？
- **异常恢复**：遇到失败时回溯、重规划，还是降级执行？

### 2.5 反思与自我修正（Reflection & Self-Refinement）
- **反思时机**：在线反思（实时）还是离线反思（执行后回顾）？
- **反思深度**：单步纠错，还是全局过程审查？
- **元认知信号**：是否需要训练进度感知能力（RePro）？
- **技能演化**：是否通过假设-验证循环持续优化技能库（HDSO）？

### 2.6 安全与对齐（Safety & Alignment）
- **输入防护**：Prompt 注入检测、访问控制、信息流控制（GIF）？
- **输出防护**：拒绝策略、内容审核、工具调用白名单？
- **人类介入点**：Human-on-the-Loop 升级阈值（如法律发现场景的 HOTL）？
- **多智能体安全**：线性工作流中的恶意传播风险（Fixer 机制）、上下文漂移同步（SSVP）？

### 2.7 评估与可观测性（Evaluation & Observability）
- **过程指标**：工具调用效率、证据覆盖率、子目标达成率？
- **结果指标**：任务完成率、准确率、生成质量？
- **可追溯性**：是否需要执行溯源（Provenance）与证据链记录？
- **长期监控**：是否监控智能体熵增（Entropy Principle）？

---

## 三、成熟架构模式总结

基于最新论文，当前构建 LLM Agent 的主流架构模式可归纳为以下七类：

### 3.1 ReAct 及其状态化演进

**核心思想**：推理（Reasoning）与行动（Acting）交替进行，以 "Thought → Action → Observation" 循环驱动任务求解。

**最新进展**：
- **状态化 ReAct**：传统 ReAct 是纯函数式、无状态的，每轮需重新读取完整历史，导致 $O(n^2)$ token 消耗。Jabbarvaziri（2026）将其重构为基于 LangGraph 的**状态化 ReAct Agent**，通过持久化类型化状态携带实验历史，在超参优化和代码优化任务中分别节省 90% 和 52% 的 token。
- **不确定性感知 ReAct**：Matsnev（2026）提出不确定性分解，将行动置信度与请求不确定性解耦，使 Agent 能在任务模糊时主动发起澄清，比 ReAct+UE 在澄清 F1 上提升 73%。
- **ReAct 的局限**：Wang & Vemuri（2026）发现 ReAct Agent 会盲目信任工具输出（如 GNN），模型越强反而越可能盲目依赖工具，提示必须显式设计选择性调用机制。

### 3.2 Plan-and-Execute / Plan-then-Execute

**核心思想**：先制定完整或局部的计划，再按计划执行，适合需要结构化并行或严格顺序约束的场景。

**最新进展**：
- **DAG Plan-and-Execute**：Dhanyamraju（2026）在企业级多智能体编排中对比 DAG Plan-and-Execute 与 ReAct。DAG 模式在小规模（<20 agents）下精度更高、支持结构化并行；但随规模增长，Agent 发现噪声成为主要瓶颈，而 ReAct 因增量处理失败更具鲁棒性。
- **Plan-then-Execute（工业场景）**：Kushwaha 等（2026）提出 DynAMO，采用 Plan-then-Execute 架构生成可验证的工作流图，支持顺序与依赖感知并行执行。结构化上下文裁剪可降低约 30% 推理延迟。

### 3.3 层次化规划与信息折叠（Hierarchical Planning + Information Folding）

**核心思想**：将长 horizon 任务分解为显式子目标，并在完成子目标后"折叠"历史，以缓解长上下文干扰。

**最新进展**：
- **HIPIF**：Diao 等（2026）提出 Hierarchical Planning and Information Folding，端到端训练 Agent 围绕子目标组织执行，同时折叠已完成的子目标历史。结合分层反思与子目标导向的过程奖励，在三个公开 Agent 基准上验证有效性。
- **应用启示**：对于多轮、长对话或复杂科研工作流，显式子目标分解 + 历史压缩是当前最直接的可工程化方案。

### 3.4 Reflection 与自我改进（Self-Refinement）

**核心思想**：Agent 在执行后对自身行为进行审视、诊断和改进，形成闭环。

**最新进展**：
- **回顾性进度感知训练（RePro）**：Ma 等（2026）发现在线进度提示会损害性能，而回顾性演示有帮助。提出 forward-then-reflect 范式：先在线执行，再基于已知结果回顾性评估步骤进度。通过 RePro-PO 训练，Qwen 系列在 WebShop、ALFWorld 和 Sokoban 上最高提升 12% 绝对成功率。
- **假设驱动技能优化（HDSO）**：Shang & Yang（2026）提出冻结 Agent + 冻结策展人的双冻结框架。策展人观察执行轨迹，提出可证伪假设，实例化为候选技能，通过配对对照实验验证后纳入技能库。在 ALFWorld 上对 Qwen3-8B 提升 +6.9 Avg. SR。
- **多智能体自我修正**：AdsMind（Zhang 等，2026）展示闭环多智能体框架，通过 MLFF 松弛反馈实现自主错误修正，在吸附构型发现任务中将能量符号错误率降至零。

### 3.5 多智能体编排（Multi-Agent Orchestration）

**核心思想**：将复杂任务分解给多个专业化 Agent，通过协调机制实现协作。

**最新进展**：
- **LLM 编排层**：Aueawatthanaphisut 等（2026）提出 LLM 编排的多智能体 BDaaS 框架，中央 LLM 层负责协调 Agent 执行、验证中间产物、管理流程上下文、支持动态工作流组合。
- **角色感知协作**：Yu 等（2026）的 DynaHMRC 中，每个机器人作为角色感知 LLM Agent，通过自描述、任务分配、领导选举和反思执行四阶段闭环协作，避免中央调度器的长上下文瓶颈。
- **技能组合式多智能体**：SIGMA（Zeng 等，2026）将 Agent 构建为可复用技能的任务条件化组合，而非预定义角色。技能-智能体关联矩阵 + 技能专用邮箱路由，使系统能动态组合能力以应对未见过的任务组合。
- **规模与安全**：McAllister 等（2026）在线性多智能体工作流中验证：大模型确实更易忠实执行恶意指令，但增加轻量级终端 Fixer 阶段可将控制-恶意性能差距从 53.7pp 压缩到 0.6pp。

### 3.6 记忆增强架构（Memory-Augmented Architectures）

**核心思想**：将记忆从上下文窗口中解耦，通过外部存储实现长期信息保留与高效检索。

**最新进展**：
- **分布式主动记忆（ActiveMem）**：Jiang 等（2026）受海马体-前额叶功能互补启发，提出将 Agent 记忆从核心推理中解耦。高层规划器使用语义要点执行推理，轻量级分布式记忆系统并行主动积累和整合要点。在 BrowseComp-Plus 和 GAIA 上达到 SOTA。
- **自适应记忆（AdaMem）**：Chen 等（2026）提出记忆不应"记住一切"，而应学习"记住什么"。通过角色特定的记忆策略和基于每周 QA 反馈的轻量级自反思，在保持记忆量减少 9% 的同时提升 QA 准确率 +9.0%。
- **记忆压缩（MemRefine）**：Kim 等（2026）在存储预算约束下，用 LLM 判断器决定删除/合并/保留条目，而非依赖表面相似度。
- **记忆溯源（GitOfThoughts）**：Shekar 等（2026）发现记忆只在新问题与记忆中的问题高度相似（余弦相似度 >0.8）时才有效；否则记忆的主要价值是审计性而非准确性。

### 3.7 从 Chatbot 到 Digital Colleague 的工作空间范式

**核心思想**：Agent 不应只是一次性的工具调用者，而应是具有持久工作空间、可复用技能、验证循环和治理机制的"数字同事"。

**最新进展**：
- **Workspace + Skill 范式**：Zhang 等（2606.14502v1）系统阐述了这一转变：
  - 认知核心：从 next-token prediction 进化为支持推理时计算、CoT、反思、过程监督和 RL 的 Thinking LLM。
  - 任务执行：从临时工具调用进化为带持久工作空间、技能、验证循环和治理的 OpenClaw 式工作站系统。
  - 数据构建：从指令-响应对转变为 State-Action-Observation 轨迹。
  - 评估：从静态基准进化为沙盒化、可审计、自演化的 AI 生态。

---

## 四、架构选型决策树（简化版）

```
任务复杂度
├── 低复杂度、短 horizon、单步决策
│   └── 推荐：ReAct 或状态化 ReAct（需要 token 效率时）
├── 中等复杂度、可分解为子目标、有明确验收标准
│   └── 推荐：Plan-and-Execute 或 HIPIF 层次规划
├── 高复杂度、长 horizon、需要持续反思
│   └── 推荐：Plan-then-Execute + Reflection 循环（RePro / HDSO）
├── 多角色、协作性任务
│   └── 推荐：LLM 编排多智能体（角色定义 + 通信拓扑 + 可选 Fixer 阶段）
└── 需要长期记忆、跨会话个性化
    └── 推荐：分布式主动记忆（ActiveMem）或 Git 版本化记忆
```

---

## 五、关键风险与工程反模式

1. **盲目信任工具**：Agent 在强模型下反而更可能不加判断地采纳工具输出，必须显式设计选择性调用与验证门。
2. **记忆偏差传播**：即使完美压缩，受污染的记忆也会跨时间传播偏差，需定期审计记忆来源。
3. **上下文漂移（多智能体）**：多 Agent 间的全量广播反而会因传播错误信念而加剧幻觉，应采用压缩状态同步（SSVP）。
4. **熵增驱动的静默失败**：Agent 系统在长时期运行后会出现输出一致性下降、任务准确率降低，需设计确定性治理机制（PIG Engine）。
5. **规划-执行错位**：在线进度提示可能损害性能，应将反思与执行解耦为"先执行、后回顾"的两阶段。

---

## 六、结语与展望

构建一个"自己的智能体"本质上是在定义一组信息边界与交互协议。当前最成熟的工程实践是：

- **架构**：状态化 ReAct + 显式子目标规划 + 过程级反思。
- **记忆**：分层记忆（短期上下文 + 长期压缩存储） + 可审计格式。
- **工具**：自适应工具调用 + 选择性验证门，而非无条件信任。
- **多智能体**：LLM 编排 + 角色/技能组合 + 轻量级纠错阶段。

未来方向包括：可微分 token 预算、动态多智能体市场、物理感知数字孪生集成，以及面向科学工作流的自主研究管道。

---

## 参考文献

1. Harsh Rao Dhanyamraju, et al. "Autonomous Event-Driven Multi-Agent Orchestration for Enterprise AI at Scale." arXiv:2606.20058v1 (2026).
2. Yuchen Xia. "Integrating Large Language Model Agents with Digital Twins for Industrial Autonomous Systems." arXiv:2606.20761v1 (2026).
3. Juncheng Diao, et al. "HIPIF: Hierarchical Planning and Information Folding for Long-Horizon LLM Agent Learning." arXiv:2606.10507v1 (2026).
4. Gregory Matsnev. "Uncertainty Decomposition for Clarification Seeking in LLM Agents." arXiv:2606.19559v1 (2026).
5. Faramarz Jabbarvaziri. "Remember, Don't Re-read: Stateful ReAct Agents for Token-Efficient Autonomous Experimentation." arXiv:2606.14945v1 (2026).
6. Zhongyuan Wang, Pratyusha Vemuri. "When the Tool Decides: LLM Agents Defer Blindly to Graph Neural Network Tools, and Stronger Backbones Defer More." arXiv:2606.14476v1 (2026).
7. Dat Tien Nguyen, et al. "TerraBench: Can Agents Reason Over Heterogeneous Earth-System Data?" arXiv:2606.13148v1 (2026).
8. Safia Baloch, Rahemeen Khan. "Toward Human-Centered Multi-Agent Systems: Integrating Cognition, Culture, Values, and Cooperation in AI Agents." arXiv:2606.08274v1 (2026).
9. Dexing Liu. "Silent Failure in LLM Agent Systems: The Entropy Principle and the Inevitable Disorder of Autonomous Agents." arXiv:2606.08162v1 (2026).
10. Yiqi Wang, et al. "From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents." arXiv:2606.04990v3 (2026).
11. Zewen Liu. "Memory Contagion: Cross-Temporal Propagation of Evaluator Bias via Agent Memory." arXiv:2606.23195v1 (2026).
12. Pavan C Shekar, et al. "GitOfThoughts: Version-Controlled Reasoning and Agent Memory You Can Replay, Diff, and Merge." arXiv:2606.14470v2 (2026).
13. Minjae Kim, et al. "MemRefine: LLM-Guided Compression for Long-Term Agent Memory." arXiv:2606.13177v1 (2026).
14. Yunhan Jiang, et al. "ActiveMem: Distributed Active Memory for Long-Horizon LLM Reasoning." arXiv:2606.10532v1 (2026).
15. Fangxin Shang, Yehui Yang. "Hypothesis-Driven Skill Optimization for LLM Agents." arXiv:2606.22330v1 (2026).
16. Jixuan Chen, et al. "AgentSpec: Understanding Embodied Agent Scaffolds Through Controlled Composition." arXiv:2606.14674v1 (2026).
17. Xinbei Ma, et al. "Retrospective Progress-Aware Self-Refinement for LLM Agent Training." arXiv:2606.14302v1 (2026).
18. Carson Rodrigues. "Hallucination as Context Drift: Synchronization Protocols for Multi-Agent LLM Systems." arXiv:2606.21666v1 (2026).
19. Cong Han, et al. "AIR: Adaptive Interleaved Reasoning with Code in MLLMs." arXiv:2606.23678v1 (2026).
20. Juyang Bai, Laixi Shi. "MAS-PromptBench: When Does Prompt Optimization Improve Multi-Agent LLM Systems?" arXiv:2606.23664v1 (2026).
21. Yongheng Zhang, et al. "From Chatbot to Digital Colleague: The Paradigm Shift Toward Persistent Autonomous AI." arXiv:2606.14502v1 (2026).

---

## 附录：检索与总结策略说明

**检索策略**：
- 以 arxiv-watcher 技能提供的 `search_arxiv.sh` 逻辑为基准，直接调用 arXiv API (`export.arxiv.org/api/query`)。
- 分六轮并行检索，覆盖以下主题组：
  1. `LLM agent architecture + tool use + memory + planning`（宽泛基础）
  2. `ReAct + large language model`（经典模式变体）
  3. `multi-agent system + orchestration`（多智能体）
  4. `LLM agent + survey`（综述与分类）
  5. `plan and execute + agent`（规划架构）
  6. `agent memory + large language model`（记忆机制）
  7. `reflection + LLM agent`（反思机制）
  8. `tool use + large language model`（工具使用）
  9. `multi-agent + collaboration`（多智能体协作）

**筛选策略**：
- 优先选择 arXiv 类别为 `cs.AI`、`cs.MA`、`cs.CL`、`cs.LG` 的论文。
- 优先选择摘要中明确讨论 Agent 架构、规划、记忆、反思、工具使用或多智能体协作的论文。
- 排除与主题无关的论文（如纯机器人控制、数学理论、图像生成等）。

**总结策略**：
- 对每篇入选论文提取：标题、作者、核心方法、关键发现/指标、与"构建自定义 Agent"的关联。
- 将论文按主题聚类为七类架构模式，提炼共性特征与工程启示。
- 输出结构化信息清单，按设计阶段（定义→实现→部署）组织。
