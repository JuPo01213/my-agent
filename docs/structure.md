# 项目文件结构索引

本文档用于快速定位具体文件的内容行号，并在开头提供完整目录树，方便快速浏览整体结构。

## 目录树

```text
my-agent/
├── AGENTS.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── _check_structure.py
├── agent_core/
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── react_agent.py
│   │   └── tool_registry.py
│   ├── demos/
│   │   ├── README.md
│   │   ├── langgraph_demo.py
│   │   ├── langgraph_official.py
│   │   ├── multi_agent_demo.py
│   │   ├── relationship_demo.py
│   │   └── stategraph_demo.py
│   ├── frontend/
│   │   ├── __init__.py
│   │   ├── adapter.py
│   │   ├── bus.py
│   │   └── events.py
│   ├── multi_agent/
│   │   ├── __init__.py
│   │   ├── agent_api.py
│   │   ├── relationship.py
│   │   ├── tool_caller.py
│   │   └── tool_filter.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── run.py
│   │   └── server.py
│   └── static/
│       ├── bubble-adapter.js
│       ├── bubble-sample.js
│       ├── bubble.html
│       ├── index.html
│       └── vue.html
├── config/
│   ├── agents.yaml
│   └── relationships.yaml
├── docs/
│   ├── structure.md
│   ├── adr/
│   ├── explain/
│   │   ├── README.md
│   │   └── 代码走读-relationship.py-2026-06-24.md
│   ├── guides/
│   │   ├── development.md
│   │   ├── frontend-exploration.md
│   │   └── running.md
│   ├── overview/
│   │   ├── README.md
│   │   ├── architecture.md
│   │   └── glossary.md
│   ├── reference/
│   │   ├── api.md
│   │   └── configuration.md
│   └── report/
│       ├── Skill_Engineering_Technical_Details.md
│       ├── 写一个自己的智能体_完整调研与最佳实践报告.md
│       ├── 关系驱动多Agent协作架构实现方案.md
│       ├── 多智能体协作系统设计模式完整调研报告.md
│       ├── 气泡卡片样式参考.md
│       ├── LangGraph多Agent架构官方模式参考.md
│       ├── ReAct智能体实现评估与改进路线图.md
│       ├── GCMP_400_input_invalid_排查与修复报告.md
│       └── reports/
├── docs_sync/
├── experiments/
│   ├── run_log.py
│   ├── outputs/
│   └── ...
├── memories/
│   ├── repo/
│   │   ├── 项目约定.md
│   │   └── 架构决策记录.md
│   └── session/
│       ├── _TEMPLATE.md
│       └── ...
├── mkdocs.yml
├── research/
├── setup_documentation.py
├── site/
└── tests/
    ├── __init__.py
    ├── test_control_shell.py
    ├── test_parse_precondition.py
    └── test_run_loop.py
```

---

本文档用于快速定位具体文件的内容行号。整体目录可直接通过目录浏览查看，此处仅记录需要按行号精确定位的核心文件。

---

## 根目录文件

### README.md

- **总行数**：约 50 行
- **作用**：人类可读的项目总览，包含项目定位、快速开始、目录说明、架构概览、文档地图、贡献方式。
- **关键内容**：
  - 1-10：项目定位与简介
  - 11-20：快速开始指南
  - 21-30：目录说明
  - 31-40：架构概览
  - 41-50：文档地图与贡献方式

### CONTRIBUTING.md

- **总行数**：约 80 行
- **作用**：贡献指南，包含项目规则、开发流程、文档规范、测试原则、诚实记录原则、实验日志规范、重构原则。
- **关键内容**：
  - 1-20：项目规则
  - 21-40：开发流程
  - 41-60：文档规范与测试原则
  - 61-80：诚实记录原则与实验日志规范

### CHANGELOG.md

- **总行数**：约 60 行
- **作用**：变更日志，记录版本级变更，与 `experiments/` 日志形成互补。
- **关键内容**：
  - 1-30：未发布版本变更
  - 31-60：2026-06-24 版本变更

### .vscode/mcp.json

- **总行数**：约 20 行
- **作用**：VS Code MCP 服务器配置，当前已配置 StepSearch 搜索服务。
- **关键内容**：
  - 1-20：StepSearch MCP 服务器定义（HTTP 类型、URL、Bearer 认证头）

---

## docs/

- **路径**：docs/
- **说明**：分层文档体系，包含概念架构、操作指南、配置参考、调研报告和架构决策。

### overview/（概念与架构）

- **路径**：docs/overview/
- **作用**：项目总览、架构概览、术语表、项目进度，帮助快速理解项目定位和核心概念。
- **关键文件**：
  - `README.md`：项目总览，包含核心能力、文档地图、快速导航
  - `architecture.md`：架构概览，包含分层结构、核心模块、关键抽象、演进路线
  - `glossary.md`：术语表，定义项目中常用的术语和概念
  - `progress.md`：项目进度，记录里程碑、当前状态和下一步计划

### guides/（操作与最佳实践）

- **路径**：docs/guides/
- **作用**：开发指南、运行指南、前端探索期说明，提供操作层面的指导。
- **关键文件**：
  - `development.md`：开发指南，包含开发环境、代码规范、开发流程、重构原则、测试原则、实验规范
  - `running.md`：运行指南，包含运行测试、运行 Demo、运行同步检查点、前端预览、实验日志
  - `frontend-exploration.md`：前端探索期说明，包含阶段定义、约束、当前文件、后续演进

### reference/（配置与 API）

- **路径**：docs/reference/
- **作用**：配置说明、YAML 示例、API 速查，提供参考层面的文档。
- **关键文件**：
  - `configuration.md`：配置参考，包含配置文件列表、YAML 结构、关键字段说明、注意事项
  - `api.md`：API 速查，包含核心层 API、多 Agent 层 API、事件 API

### report/（调研报告）

- **路径**：docs/report/
- **作用**：调研报告与最佳实践文档，包含完整调研、架构方案、样式参考等。

- **路径**：docs/report/

### GCMP_400_input_invalid_排查与修复报告.md

- **总行数**：约 200 行
- **作用**：记录 2026-06-24 GCMP 扩展 400 input_invalid 问题的排查与修复过程，包含根因分析、补丁内容和后续建议。
- **关键内容**：
  - 1-30：问题背景与报错现象
  - 31-60：排查过程（日志读取、代码定位）
  - 61-100：根因分析（reasoningEffort 数组未归一化）
  - 101-140：修复方案（补丁内容与验证）
  - 141-180：后续建议与关联问题
  - 181-末：技术细节补充与参考链接

### GCMP_400_input_invalid_原始日志_2026-06-24T173409.log

- **总行数**：约 1378 行
- **作用**：本次问题的原始参考资料，保留完整日志以便后续复现比对或继续排查。
- **来源**：`C:\Users\Administrator\AppData\Roaming\Code\logs\20260624T173409\window1\exthost\vicanent.gcmp\GitHub Copilot Models Provider (GCMP).log`
- **注意**：原始路径在 VS Code 日志目录中，属于易失文件；如需长期保留，可手动复制到本仓库 docs 或 experiments 目录。

### 写一个自己的智能体_完整调研与最佳实践报告.md

- **总行数**：778 行

| 段落 | 行号 | 内容 |
|------|------|------|
| 标题与元信息 | 1-5 | 版本 v1.0、日期 2026-06-24、来源、技能覆盖 |
| 目录 | 6-19 | 9 个章节导航 |
| 一、执行摘要 | 20-30 | 信息需求与成熟最佳实践概述 |
| 二、信息需求全景图 | 31-90 | 7 大信息域、5 大商业输入、12 个必答问题、优先级矩阵 |
| 三、成熟架构模式 | 91-175 | Level 1-4 演进路径、五层架构、四种架构速查、框架对比表 |
| 四、代码实现与工具选型 | 176-407 | ReAct 单文件示例、状态化智能体、RAG chunking、成本估算 |
| 五、安全护栏与合规落地 | 408-518 | 纵深防御体系、输入防护 YAML、RBAC、沙箱配置 |
| 六、评测体系与部署运维 | 519-610 | Golden Case 设计、CI 流水线、Docker 多阶段构建 |
| 七、真实案例与团队选型 | 611-692 | 1/5/10+ 人团队案例、框架决策树、行业模板、18 个常见陷阱 |
| 八、最佳实践总结 | 693-724 | 技术/工程/组织三条线要点 |
| 九、附录 | 725-762 | 4 组必答问题 + 6 周学习路径 |
| 参考来源 | 763-774 | 7 项参考文献 |
| 结尾声明 | 775-778 | 声明 |
### Skill_Engineering_Technical_Details.md

- **路径**：docs/report/reports/Skill_Engineering_Technical_Details.md
- **总行数**：待补充
- **内容**：技能体注册发现协议、MCP 技术规范、记忆系统工程实现、安全护栏技术实现、技能体工程化框架、关键代码片段、审计日志格式
### 多智能体协作系统设计模式完整调研报告.md

- **路径**：docs/report/多智能体协作系统设计模式完整调研报告.md
- **总行数**：约 500 行
- **作用**：多智能体协作系统完整调研报告，包含基础概念、四种架构、四种调度、AWS Strands 四种模式、模式融合、基准测试、具体场景案例和本项目演进建议。
- **关键内容**：
  - 1-50：单 Agent 局限性 + 多 Agent 收益 + 企业案例
  - 50-80：核心概念厘清（子代理、代理团、多 Agent 协作）
  - 80-160：LangGraph 官方四种架构
  - 160-180：四种调度模式
  - 180-380：六个具体场景案例（算汇率、写代码、客服、写日报、翻译、旅行规划）
  - 380-420：AWS Strands 四种模式
  - 420-460：模式选择决策框架
  - 460-500：常见误区、演进建议、参考资料

### LangGraph多Agent架构官方模式参考.md

- **路径**：docs/report/LangGraph多Agent架构官方模式参考.md
- **总行数**：约 300 行
- **作用**：LangGraph 官方多 Agent 架构模式参考，包含 Supervisor、Swarm、Hierarchical 三种模式及代码示例。
- **关键内容**：
  - 1-50：两种核心模式概述（Supervisor vs Swarm）
  - 50-150：Supervisor 模式详解 + 官方代码
  - 150-250：Swarm 模式详解 + 官方代码
  - 250-300：分层架构 + 成熟案例

### 关系驱动多Agent协作架构实现方案.md

- **路径**：docs/report/关系驱动多Agent协作架构实现方案.md
- **总行数**：约 600 行
- **作用**：基于 LangGraph / SALLMA / Accountability / CrewAI / Blackboard / SAMALM 等业界成熟实践，给出本项目"关系驱动多 Agent 协作层"的完整实现方案。包含 7 个业界案例、关系引擎 Python 代码、YAML 配置示例、模式融合策略和落地路线图。
- **关键内容**：
  - 1-150：7 个业界案例（LangGraph / SALLMA / Accountability / CrewAI / Blackboard / SAMALM / 7 拓扑），每个都有出处链接
  - 150-250：项目当前状态盘点 + 设计目标 + 架构分层
  - 250-450：关系引擎 `multi_agent/relationship.py` 完整实现（Blackboard / Command / KnowledgeSource / ControlShell / RelationshipEngine）
  - 450-550：YAML 配置示例（agents.yaml / relationships.yaml）+ 使用 demo
  - 550-650：模式融合策略（Blackboard 底 + Supervisor 顶）+ 关系即配置原则
  - 650-750：5 阶段落地路线图（v1.0 骨架 → v3.0 高级特性）
  - 750-末：参考资料（29 项）+ 完整可运行最小示例 + 与 LangGraph 对比表

### ReAct智能体实现评估与改进路线图.md

- **路径**：docs/report/ReAct智能体实现评估与改进路线图.md
- **总行数**：约 130 行
- **作用**：当前 ReAct 自主循环实现的评估报告，包含优缺点分析、已修复问题、现存问题分级、改进路线图、适用场景判断和参考论文依据。
- **关键行号**：
  - 1-30：当前实现评估（核心优点、已修复 P0 问题）
  - 32-60：现存问题分级（P1 严重缺陷、P2 体验问题）
  - 62-100：改进路线图（P1 近期迭代、P2 中长期升级）
  - 102-115：适用场景判断矩阵
  - 117-130：参考论文依据

### 气泡卡片样式参考.md

- **路径**：docs/report/气泡卡片样式参考.md
- **总行数**：约 450 行
- **作用**：沉浸式气泡对话界面样式参考，包含设计令牌、核心气泡样式、背景效果、输入区样式、响应式适配、JavaScript 交互逻辑等完整前端样式代码。
- **关键行号**：
  - 1-20：设计令牌（CSS Variables）
  - 22-80：核心气泡样式（基础样式、类型样式、发光装饰）
  - 82-120：气泡内部元素（元信息、代码块、强调文本）
  - 122-200：背景效果（流体渐变、浮动粒子、AI脉动环）
  - 202-280：输入区样式（容器、输入框、发送按钮）
  - 282-290：响应式适配
  - 292-380：核心设计特点（毛玻璃、弹出动画、悬停交互、色彩体系）
  - 382-450：JavaScript 交互逻辑与完整 HTML 结构

### 分技能报告

- **路径**：docs/report/reports/
- **说明**：各分技能调研报告的文件名即索引，按技能名可直接定位。技能文件本身已采用渐进式披露，无需在此重复记录。

---

## memories/

- **路径**：memories/
- **说明**：知识沉淀目录，包含仓库级经验（repo/）和会话归档（session/）。

### repo/架构决策记录.md

- **总行数**：约 450 行（含 12 个 ADR）
- **作用**：记录关键架构决策（ADR），包含选型背景、决策内容、多维度对比、选型依据和演进路线。
- **关键 ADR 索引**：
  - ADR-001：Function Calling 替代正则解析
  - ADR-002：核心 Agent 内核自主实现（与 LangGraph 5 维度对比）
  - ADR-003：无安全护栏设计
  - ADR-004：路由决策使用搜索而非记忆
  - ADR-005：后端核心分层重构（core/ 与 multi_agent/ 分离）
  - ADR-006：关系驱动多 Agent 协作引擎
  - ADR-007：ReAct 兼容推理模型（reasoning_content fallback）
  - ADR-008：YAML 缺省 tools 字段陷阱
  - ADR-009：_parse_precondition 三 key and 修复
  - ADR-010：引入单元测试体系
  - ADR-011：max_steps 触发条件
  - ADR-012：测试用例设计原则（风险点优先，不追覆盖率）— **本轮新增**

### repo/项目约定.md

- **路径**：memories/repo/项目约定.md
- **作用**：项目开发规范与约定，包含技术选型、开发流程、代码风格等。

### session/

- **路径**：memories/session/
- **说明**：对话归档目录，按日期+轮次命名。模板见 `_TEMPLATE.md`。
- **当前归档**：
  - 01~05：项目早期（功能开发 + 调研）
  - 06：reAct 推理模型问题首次暴露
  - 07：绕过 ReAct 循环的尝试（被用户回退）
  - 08：修核心不绕核心（ADR-007 落地）
  - 09：工具调用场景 + 完整日志机制 + ADR-008 + 文档结构优化

---

## tests/

- **路径**：tests/
- **作用**：单元测试目录，**标准库 unittest，零外部依赖**。
  - 命名约定：`test_<模块名>.py`
  - 设计原则（参见 ADR-012）：**风险点优先，不是覆盖率优先**。每个测试都对应一个明确的"风险 N"注释。
  - 当前覆盖范围（2026-06-24 第 12 轮精简后）：
    - `test_parse_precondition.py`：1 个表驱动测试方法覆盖 4 类真风险（未知表达式放行 / 三 key and 真"全部满足" / malformed 不崩 / snapshot 缺字段不崩）
    - `test_run_loop.py`：3 个测试（推理模型 fallback / 未知工具不崩 / max_steps 占位符）
    - `test_control_shell.py`：4 个测试（priority 排序 / 3 Agent 串行链 / 异常 failed / max_steps timeout 设计语义）
  - **删除**：`test_command.py`（整体）+ `test_blackboard.py`（整体），原因参见 ADR-012
  - 关联 ADR：
    - ADR-007（推理模型 fallback）由 `test_reasoning_model_fallback_works` 守护
    - ADR-009（_parse_precondition 三 key and 修复）由 `test_risk_table` 守护
    - ADR-011（max_steps 触发条件）由 `test_max_steps_timeout_design_semantics` 守护
  - 运行方式（在项目根目录）：
    ```bash
    python -m unittest discover -s tests -v
    ```
  - 当前测试统计：**8 个测试**，0.002s 全过，**不追求覆盖率**

## agent_core/

- **路径**：agent_core/
- **说明**：智能体核心代码，按"core + multi_agent"分层组织，关注点分离。
- **架构原则**：
  - `core/`：最底层的 ReAct 循环 + 工具注册表，**不暴露任何 dashboard 相关参数**
  - `multi_agent/`：多 Agent 协作的公开 API，Supervisor 唯一入口
  - `static/`：前端探索期静态文件（**当前不与后端联通**）
  - `demos/`：多 Agent 架构演示代码，**不参与主项目运行**

### core/

- **路径**：agent_core/core/
- **作用**：核心层，**只做一件事**：跑一次 ReAct 循环 + 工具注册表 + 搜索后端抽象。
- **公开 API**（从 `agent_core.core` 导入）：
  - `run_loop(user_input, client, model, system_prompt, openai_tools, max_steps) -> str`
  - `TOOLS` / `register_tool` / `build_openai_tools_schema` / `validate_tool_args`
  - `SearchBackend` / `SearchResult` / `register_backend` / `get_backend` / `set_default_backend` / `list_backends`
- **关键文件**：
  - `react_agent.py`：纯 ReAct 循环（~100 行），无任何 dashboard 事件协议
  - `tool_registry.py`：工具注册表 + 3 个内置工具（calculator / search / get_time）
  - `search_backends.py`：搜索后端抽象层，定义 SearchBackend 接口与注册表
  - `search_mcp_backends.py`：MCP 搜索后端实现，当前包含 StepSearchMCPBackend
  - `search_init.py`：搜索后端默认初始化，包导入时自动注册 StepSearch 或占位后端

### multi_agent/

- **路径**：agent_core/multi_agent/
- **作用**：多 Agent 协作的公开 API 层，**Supervisor 唯一入口**。
- **公开 API**（从 `agent_core.multi_agent` 导入）：
  - `run_react_agent(user_input, client, model, tools, system_prompt, max_steps) -> str`
  - `filter_tools_schema(tools)`：根据工具名列表过滤 OpenAI Schema
  - `call_tool_safe(tool_name, tool_args)`：安全调用工具
  - `Blackboard` / `Command` / `KnowledgeSource` / `ControlShell` / `RelationshipEngine`：关系驱动协作 API
- **关键文件**：
  - `agent_api.py`：统一 API，包装 core.run_loop
  - `tool_filter.py`：工具过滤
  - `tool_caller.py`：安全工具调用包装
  - `relationship.py`：**关系驱动多 Agent 协作引擎**（~330 行）
    - `Blackboard`：共享状态（facts / open_questions / history）
    - `Command`：LangGraph 风格路由原语（goto + update + terminate）
    - `KnowledgeSource`：Agent 单元（preconditions + action + role/goal/backstory）
    - `ControlShell`：OODA 调度器（first_match / priority / round_robin）
    - `RelationshipEngine`：YAML 驱动的协作引擎，含 `from_yaml()` 工厂
    - `_parse_precondition()`：安全子集表达式解析（避免 eval）
  - `__init__.py`：暴露基础 ReAct API + 关系驱动 API

### frontend/

- **路径**：agent_core/frontend/
- **作用**：前端事件契约层，**与 Vue/HTML 0 耦合**，仅定义中性事件格式 + 聚合 + 翻译。
- **关键文件**：
  - `events.py`：8 类前端事件工厂函数，ISO-8601 时间戳，snake_case 字段
  - `bus.py`：`EventBus` 收集事件，同时兼容 `type` 与 `kind` 字段统计
  - `adapter.py`：`wrap_trace_to_events()` 将核心中性 trace 翻译为前端事件；`aggregate_run_events()` 聚合 Agent 级 trace
  - `__init__.py`：导出 `EventBus`、事件工厂、适配器
- **关联 ADR**：ADR-013（异步事件流 / 前端解耦）
- **说明**：部分静态页面（例如 `bubble.html`）已与后端服务联通用于演示。

### server/

- **路径**：agent_core/server/
- **作用**：FastAPI 服务层，提供静态页面访问、配置 API、运行接口和 SSE 事件流。
- **关键文件**：
  - `run.py`：入口脚本，通过 `uvicorn` 启动 `agent_core.server.server:app`。
  - `server.py`：FastAPI 应用，实现 `/api/config/*`、`/api/run`、`/api/runs/{run_id}/events` 和首页渲染。
- **说明**：`bubble.html` 已与 `/api/run` 和 SSE 事件流联动，支持多 Agent 协作实时可视化。

### config.py

- **总行数**：约 70 行
- **作用**：集中管理模型与 API 配置，支持 StepFun / Ark(豆包) / OpenAI 三种 Provider，默认值来自用户提供的配置，环境变量可覆盖。
- **关键行号**：
  - 1-20：StepFun 默认配置
  - 22-28：OpenAI 兼容配置（fallback）
  - 30-38：Ark / 豆包配置（第二模型）
  - 40-55：`get_provider()` 解析当前生效的 (api_key, base_url, model)，优先级 StepFun > OpenAI
  - 57-70：`get_provider_config(name)` 按名称返回指定 Provider 配置，支持 stepfun/ark/doubao/openai

### static/

- **路径**：agent_core/static/
- **作用**：前端样式探索期静态文件，部分页面已与后端服务联通用于演示，仍可双击静态打开预览。
- **关键文件**：
  - `index.html`：早期静态演示页
  - `vue.html`：Vue 版本演示页
  - `bubble.html`：气泡对话界面，已对接 `/api/run` 与 SSE 事件流
  - `bubble-adapter.js`：将后端标准事件映射为气泡组件所需的数据结构

### demos/

- **路径**：agent_core/demos/
- **作用**：存放多 Agent 架构的演示代码，**不参与主项目运行**，避免污染主项目稳定性。
- **关键文件**：
  - `multi_agent_demo.py`：简单 Supervisor 模式演示（函数调用链）
  - `stategraph_demo.py`：自定义状态图模式演示（自实现图引擎）
  - `langgraph_demo.py`：LangGraph 框架模式演示
  - `langgraph_official.py`：LangGraph 官方代码示例
  - `relationship_demo.py`：关系驱动协作演示（3 个 demo：Python API / YAML 驱动 / 自定义 action）
  - `README.md`：演示目录说明
- **运行方式**：`python agent_core/demos/<文件名>.py`

### config/（项目根目录）

- **路径**：config/
- **作用**：YAML 配置文件目录，**关系驱动协作引擎**加载这些文件来定义多 Agent 协作行为。
- **关键文件**：
  - `agents.yaml`：Agent 定义（role / goal / backstory / tools / preconditions / max_iter）
  - `relationships.yaml`：关系定义（priority / termination）
- **修改这些 YAML 文件即可改变多 Agent 协作流程，无需改任何 Python 代码**。

---

## tests/

- **路径**：tests/
- **作用**：单元测试目录，**标准库 unittest，零外部依赖**。
  - 命名约定：`test_<模块名>.py`
  - 设计原则（参见 ADR-012）：**风险点优先，不是覆盖率优先**。每个测试都对应一个明确的"风险 N"注释。
  - 当前覆盖范围（2026-06-24 第 12 轮精简后）：
    - `test_parse_precondition.py`：1 个表驱动测试方法覆盖 4 类真风险（未知表达式放行 / 三 key and 真"全部满足" / malformed 不崩 / snapshot 缺字段不崩）
    - `test_run_loop.py`：3 个测试（推理模型 fallback / 未知工具不崩 / max_steps 占位符）
    - `test_control_shell.py`：4 个测试（priority 排序 / 3 Agent 串行链 / 异常 failed / max_steps timeout 设计语义）
  - **删除**：`test_command.py`（整体）+ `test_blackboard.py`（整体），原因参见 ADR-012
  - 关联 ADR：
    - ADR-007（推理模型 fallback）由 `test_reasoning_model_fallback_works` 守护
    - ADR-009（_parse_precondition 三 key and 修复）由 `test_risk_table` 守护
    - ADR-011（max_steps 触发条件）由 `test_max_steps_timeout_design_semantics` 守护
  - 运行方式（在项目根目录）：
    ```bash
    python -m unittest discover -s tests -v
    ```
  - 当前测试统计：**8 个测试**，0.002s 全过，**不追求覆盖率**

## experiments/

- **路径**：experiments/
- **作用**：所有真实实验（调用 LLM、跑测试、跑 benchmark）的脚本与日志归档目录。
  - 按 `experiments/<日期>-<实验名>.py` 命名脚本
  - 同名 `.log` 存放执行输出（stdout + stderr 全部重定向）
  - 任何实验汇报必须给出日志的绝对路径供用户 `cat` 验真
- **当前归档**：
  - `2026-06-24-relationship-real.py`：用 StepFun 真实 API 跑 relationship.py 的 3 Agent 协作
  - `2026-06-24-relationship-real.log`：上述脚本的完整执行输出（含 KPI 校验）
  - `2026-06-24-relationship-real-kpi.py`：从 log 反推顺序的辅助 KPI 校验脚本
  - `2026-06-24-scenario.yaml`：纯 LLM 场景的 Agent 配置（advisor/strategist/writer，**未显式列 tools → 0 工具调用**，见 ADR-008）
  - `2026-06-24-scenario-relationships.yaml`：纯 LLM 场景的关系配置（priority + termination）
  - `2026-06-24-scenario.py`：跑"6 个月 AI 转型路线图"场景的主脚本（保留默认 ReAct 循环，175.08s）
  - `2026-06-24-scenario.log`：场景实验完整日志（3 段产出实测 19750 字，6/6 KPI 全过）
  - `2026-06-24-scenario-kpi.py`：从 log 反推 KPI 的辅助脚本（解决主脚本 KPI 段被 PowerShell 截断的问题）
  - `2026-06-24-tool-scenario.yaml`：工具调用场景 Agent 配置（analyst 显式 `[calculator, get_time]`，writer `[get_time]`，见 ADR-008）
  - `2026-06-24-tool-scenario-relationships.yaml`：工具调用场景关系配置（priority analyst=1, writer=2）
  - `2026-06-24-tool-scenario.py`：工具调用场景主脚本（包装 OpenAI client + TOOLS，35.03s 跑出 8 LLM + 10 工具）
  - `2026-06-24-tool-scenario.log`：工具调用场景完整日志（**65515 字符，含每次 LLM 调用的完整 request/response JSON**）
  - `2026-06-24-test-parse-precondition.log`：A2 任务单元测试日志（20/20 OK）
  - `2026-06-24-test-run-loop.log`：A3 任务单元测试日志（12/12 OK）
  - `2026-06-24-test-all.log`：全量测试日志（32/32 OK，A1-A4 完成后）
  - `2026-06-24-sync-checkpoint.log`：sync_checkpoint.py 执行日志（结构索引 + 主报告 + session 三项检查全过）
- **outputs/**（子目录）：
  - **作用**：所有实验的"干净交付物"——完整原文 + 代码 + 配置 + 索引，按需打开可独立验证
  - `README.md`：双场景完整索引（含流程图、KPI、再跑命令） + **三场演进对比表**（ADR × KPI × 踩坑 一图速查，导航索引）
  - 第一场（无工具）：advisor-output.md (5043字) / strategist-output.md (5873字) / writer-output.md (8834字) / scenario-script.py / 两个 yaml
  - 第二场（有工具）：tool-analyst-output.md (498字) / tool-writer-output.md (963字) / tool-scenario-script.py / 两个 yaml
  - **原则**：产物非代码，手工归档保证零修改，**不做自动生成脚本**

---

## docs_sync/

- **路径**：docs_sync/
- **说明**：文档同步增强层，包含 AI 辅助审查脚本。

### ai_reviewer.py

- **总行数**：约 280 行
- **作用**：基于大模型自动分析代码变更，判断是否需要更新文档，并在 PR 中自动评论提醒
- **关键功能**：
  - 获取 PR 的代码变更文件列表
  - 基于 CODE_TO_DOC_MAP 和目录约定推断受影响的文档
  - 调用 StepFun LLM 分析变更内容，判断文档是否需要更新
  - 在 PR 中发布评论，提醒更新文档
- **环境变量**：
  - STEPFUN_API_KEY：StepFun API 密钥
  - STEPFUN_BASE_URL：StepFun API 地址
  - STEPFUN_MODEL：模型名称，默认 step-3.7-flash
  - GITHUB_TOKEN：GitHub Actions 自动提供
  - PR_NUMBER：PR 编号，GitHub Actions 自动提供

### config.yaml

- **总行数**：约 80 行
- **作用**：文档同步模型配置，定义项目结构模型、检查策略和站点生成配置
- **关键内容**：
  - structure.directories：目录职责约定，定义每个目录的角色和文档义务
  - structure.files：单文件特殊规则，覆盖目录规则
  - policies：检查策略配置，包括代码-文档同步、引用检查、ADR 触发、结构变更检测
  - site：文档站点生成配置，支持 MkDocs 构建和 GitHub Pages 部署

### engine.py

- **总行数**：约 400 行
- **作用**：文档同步检查引擎，实现模型驱动的同步检查
- **关键功能**：
  - 加载 docs_sync/config.yaml 配置
  - StructureScanner：扫描实际项目结构
  - StructureChangeCheck：检测项目结构变化
  - CodeDocSyncCheck：检查代码-文档同步
  - ReferenceCheck：检查文档引用有效性
  - AdrTriggerCheck：检查 ADR 触发条件
  - 支持 --changed 参数指定变更文件，或自动检测 git 变更

---

## docs/explain/

- **路径**：docs/explain/
- **作用**：代码走读 / 讲解类文档，按主题+日期命名。
- **当前归档**：
  - `README.md`：目录说明
  - `代码走读-relationship.py-2026-06-24.md`：relationship.py 的 6 步走读

### adr/（架构决策记录）

- **路径**：docs/adr/
- **作用**：架构决策记录（ADR），按文件拆分，便于检索和版本化。
- **关键文件**：
  - `001-function-calling.md`：采用原生 Function Calling 替代正则解析工具调用
  - `002-self-hosted-core.md`：核心 Agent 内核自主实现，不直接依赖重型框架
  - `003-no-safety-guardrails.md`：无安全护栏设计
  - `004-search-over-memory.md`：路由决策使用搜索而非记忆
  - `005-core-multi-agent-split.md`：后端核心分层重构 - core/ 与 multi_agent/ 分离
  - `006-relationship-engine.md`：引入关系驱动多 Agent 协作引擎
  - `007-reasoning-content-fallback.md`：ReAct 循环兼容推理模型
  - `008-yaml-tools-default.md`：YAML 缺省 tools 字段的隐性陷阱
  - `009-parse-precondition-bug.md`：修复 _parse_precondition 三 key and 表达式分支顺序 bug
  - `010-unit-test-foundation.md`：引入单元测试体系（unittest 标准库）
  - `011-max-steps-and-test-baseline.md`：max_steps 触发条件 + 多模块单元测试基线完成
  - `012-risk-based-testing.md`：测试用例设计原则 — 风险点优先，不是覆盖率优先
  - `013-async-event-interface.md`：后续方向 A — 异步/流式事件接口
  - `014-tool-whitelist.md`：后续方向 B — 工具白名单让 LLM 真用工具
  - `015-gatekeeper-pattern.md`：后续方向 C — first_match 看门人模式
  - `016-langgraph-adapter.md`：后续方向 D — LangGraph 兼容适配层
  - `017-ci-integration.md`：后续方向 E — 单元测试 + CI 接入
- **说明**：每个 ADR 文件包含状态、背景、决策、后果、关联教训等完整信息。

---

## 说明

- 技能文件（.github/skills/*/SKILL.md）已按渐进式披露组织，可直接按技能名查阅，不在此重复索引。
- AGENTS.md 是第一入口，此处不重复索引。
- `project-initializer`：初始化项目规则、整理目录结构、对话归档与知识沉淀
- `session-summarizer`：自动记录对话中的问题、报错、解决过程和结论
- 如需了解目录结构，使用目录浏览即可。


