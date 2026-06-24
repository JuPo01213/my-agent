# 变更日志

本文档记录 my-agent 项目的版本级变更。所有真实实验和代码变更都会记录在此。

## [未发布]

### 新增
- 新增 `README.md` 作为人类可读的顶层入口
- 新增 `docs/overview/` 目录，包含项目总览、架构概览、术语表
- 新增 `docs/guides/` 目录，包含开发指南、运行指南、前端探索期说明
- 新增 `docs/reference/` 目录，包含配置参考、API 速查
- 新增 `docs/adr/` 目录，将架构决策记录按文件拆分（ADR-001 至 ADR-017）
- 新增 `CONTRIBUTING.md` 贡献指南
- 新增 `CHANGELOG.md` 变更日志

### 改进
- 升级 `docs/` 为分层文档体系（overview / guides / reference / report / adr）
- 强化 `docs/structure.md` 的导航能力，增加按主题索引和文档健康度
- 扩展现有 `sync_checkpoint.py`，增加文档完整性检查

### 修复
- 修复 `sync_checkpoint.py` 中 emoji 违反 AGENTS.md 规则的问题

## [2026-06-24]

### 新增
- 初始化项目结构，包含 agent_core、config、docs、experiments、memories、tests 等目录
- 实现 ReAct 内核（`agent_core/core/react_agent.py`）
- 实现工具注册表（`agent_core/core/tool_registry.py`）
- 实现多 Agent 协作引擎（`agent_core/multi_agent/relationship.py`）
- 实现前端探索期静态文件（`agent_core/static/`）
- 实现多 Agent 架构演示（`agent_core/demos/`）
- 实现单元测试体系（`tests/`，8 个风险点守护测试）
- 实现同步检查点脚本（`.github/skills/project-initializer/scripts/sync_checkpoint.py`）

### 改进
- 完成 ADR-001 至 ADR-017 架构决策记录
- 完成调研报告（`docs/report/` 下 7 份报告）
- 完成实验日志体系（`experiments/` 下多份实验记录）

### 修复
- 修复 `_parse_precondition` 三 key and 表达式分支顺序 bug（ADR-009）
- 修复 YAML 缺省 tools 字段的隐性陷阱（ADR-008）
- 修复推理模型 reasoning_content fallback（ADR-007）
