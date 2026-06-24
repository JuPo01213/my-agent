# my-agent

一个用于探索、构建和沉淀 AI Agent 能力的工作区。项目聚焦“自己写一个智能体”的完整链路：从 ReAct 内核、多 Agent 协作、前端探索，到调研报告、架构决策和实验验证。

## 快速开始

- 阅读 `AGENTS.md`：这是本工作区的 always-on 规则入口，优先约束 AI 行为。
- 阅读 `docs/structure.md`：快速定位核心文件、报告和实验记录。
- 运行测试：`python -m unittest discover -s tests -v`
- 查看 demo：`agent_core/demos/` 下有多 Agent 架构演示。

## 目录说明

- `agent_core/`：智能体核心代码，包含 ReAct 循环、工具注册表、多 Agent 协作 API。
- `config/`：Agent 与关系配置，使用 YAML 描述。
- `docs/`：分层文档体系，包含概念架构、操作指南、配置参考、调研报告和架构决策。
- `experiments/`：真实实验与日志。
- `memories/`：会话归档和仓库级经验沉淀。
- `tests/`：单元测试，标准库 unittest，零外部依赖。
- `.github/skills/`：可复用的技能资产。

## 架构概览

项目采用“core + multi_agent”分层：

- `agent_core/core/`：最底层，只做 ReAct 循环和工具注册表。
- `agent_core/multi_agent/`：多 Agent 协作公开 API，Supervisor 唯一入口。
- `agent_core/frontend/` 与 `agent_core/static/`：前端事件协议与样式探索期静态文件。

详细架构说明见 `docs/overview/architecture.md`。

## 文档地图

- 人类入口：本文件 `README.md`
- AI 入口：`AGENTS.md`
- 结构索引：`docs/structure.md`
- 概念与架构：`docs/overview/`
- 操作指南：`docs/guides/`
- 配置与 API：`docs/reference/`
- 调研报告：`docs/report/`
- 架构决策：`docs/adr/`
- 项目约定：`memories/repo/项目约定.md`

## 贡献方式

当前阶段以个人探索和实验为主。若需协作，请先阅读 `CONTRIBUTING.md`。

## 许可与声明

本项目仅用于学习和研究。用户明确了解所有风险并自行承担全部后果。
