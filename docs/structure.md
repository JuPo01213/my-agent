# 项目文件结构索引

本文档用于快速定位具体文件的内容行号。整体目录可直接通过目录浏览查看，此处仅记录需要按行号精确定位的核心文件。

---

## docs/report/

- **路径**：docs/report/

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

- **总行数**：约 60 行
- **作用**：记录关键架构决策（ADR），包含选型背景、决策内容、多维度对比、选型依据和演进路线。
- **关键行号**：
  - 1-7：ADR-001（Function Calling 替代正则解析）
  - 9-53：ADR-002（核心 Agent 内核自主实现），含与 LangGraph/AutoGen 等框架的 5 维度详细对比
  - 55-60：ADR-003（无安全护栏设计）

### repo/项目约定.md

- **路径**：memories/repo/项目约定.md
- **作用**：项目开发规范与约定，包含技术选型、开发流程、代码风格等。

### session/

- **路径**：memories/session/
- **说明**：对话归档目录，按日期+轮次命名。模板见 `_TEMPLATE.md`。

---

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
- **作用**：核心层，**只做一件事**：跑一次 ReAct 循环 + 工具注册表。
- **公开 API**（从 `agent_core.core` 导入）：
  - `run_loop(user_input, client, model, system_prompt, openai_tools, max_steps) -> str`
  - `TOOLS` / `register_tool` / `build_openai_tools_schema` / `validate_tool_args`
- **关键文件**：
  - `react_agent.py`：纯 ReAct 循环（~100 行），无任何 dashboard 事件协议
  - `tool_registry.py`：工具注册表 + 3 个内置工具（calculator / search / get_time）

### multi_agent/

- **路径**：agent_core/multi_agent/
- **作用**：多 Agent 协作的公开 API 层，**Supervisor 唯一入口**。
- **公开 API**（从 `agent_core.multi_agent` 导入）：
  - `run_react_agent(user_input, client, model, tools, system_prompt, max_steps) -> str`
  - `filter_tools_schema(tools)`：根据工具名列表过滤 OpenAI Schema
  - `call_tool_safe(tool_name, tool_args)`：安全调用工具
- **关键文件**：
  - `agent_api.py`：统一 API，包装 core.run_loop
  - `tool_filter.py`：工具过滤
  - `tool_caller.py`：安全工具调用包装

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
- **作用**：前端样式探索期静态文件（index.html / vue.html / bubble.html），**当前不与后端联通**，纯静态预览。

### demos/

- **路径**：agent_core/demos/
- **作用**：存放多 Agent 架构的演示代码，**不参与主项目运行**，避免污染主项目稳定性。
- **关键文件**：
  - `multi_agent_demo.py`：简单 Supervisor 模式演示（函数调用链）
  - `stategraph_demo.py`：自定义状态图模式演示（自实现图引擎）
  - `langgraph_demo.py`：LangGraph 框架模式演示
  - `langgraph_official.py`：LangGraph 官方代码示例
  - `README.md`：演示目录说明
- **运行方式**：`python agent_core/demos/<文件名>.py`

---

## 说明

- 技能文件（.github/skills/*/SKILL.md）已按渐进式披露组织，可直接按技能名查阅，不在此重复索引。
- AGENTS.md 是第一入口，此处不重复索引。
- `project-initializer`：初始化项目规则、整理目录结构、对话归档与知识沉淀
- `session-summarizer`：自动记录对话中的问题、报错、解决过程和结论
- 如需了解目录结构，使用目录浏览即可。


