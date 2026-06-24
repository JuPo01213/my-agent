# 项目总览

本文档提供 my-agent 工作区的概览信息，帮助快速理解项目定位、核心能力和文档地图。

## 项目定位

my-agent 是一个用于探索、构建和沉淀 AI Agent 能力的工作区。项目聚焦“自己写一个智能体”的完整链路：从 ReAct 内核、多 Agent 协作、前端探索，到调研报告、架构决策和实验验证。

## 核心能力

- **ReAct 内核**：自主实现的 ReAct 循环，支持工具调用、推理模型 fallback
- **多 Agent 协作**：关系驱动引擎，支持 YAML 配置、多种调度策略
- **前端探索**：静态气泡对话界面，当前不与后端联通
- **调研沉淀**：完整的调研报告、架构决策记录、实验日志体系

## 文档地图

- **人类入口**：`README.md`
- **AI 入口**：`AGENTS.md`
- **结构索引**：`docs/structure.md`
- **概念与架构**：`docs/overview/`
- **操作指南**：`docs/guides/`
- **配置与 API**：`docs/reference/`
- **调研报告**：`docs/report/`
- **架构决策**：`docs/adr/`
- **项目约定**：`memories/repo/项目约定.md`

## 快速导航

| 需求 | 文档 |
|------|------|
| 首次了解项目 | `README.md` + `docs/overview/architecture.md` |
| 开始开发 | `docs/guides/development.md` |
| 运行项目 | `docs/guides/running.md` |
| 查看 API | `docs/reference/` |
| 理解架构决策 | `docs/adr/` |
| 查看调研报告 | `docs/report/` |
