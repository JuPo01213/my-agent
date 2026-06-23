---
name: my-agent
description: "Use when: working in my-agent workspace, building or extending AI agent features, creating skills, prompts, instructions, agents, hooks, or tools for coding assistants; 适用于 my-agent 工作区、构建或扩展 AI agent 功能、创建技能、提示词、指令、agent、hooks 或编码助手工具。"
---

# Agent Workspace

此工作区用于存放 AI agent 定制文件及相关代码。

## 文件布局

- `AGENTS.md` — 本工作区 always-on agent 指令，为第一入口。
- `.github/skills/` — 全部技能资产。
- `docs/report/` — 调研报告与最佳实践文档。
- `docs/structure.md` — 文件结构文档，用于快速定位代码。

详细结构说明见 `docs/structure.md`。

## 约定

- 指令保持简洁、可执行
- 优先链接文档，不要重复内嵌大段内容
- 相关处使用 YAML frontmatter：`name`、`description`、`applyTo`
- 校验 YAML 语法：使用空格而非 tab；description 含冒号时加引号

## 项目规则

- **对话内容均须使用中文**，这是最高优先级规则。
- 本项目仅使用 Python。
- 对于适合子代理处理的任务，应优先使用子代理并行执行，以提升工作效率。
- 模型执行工作时仅使用 Python 命令。
- 代码变更前须先提交。
- 提交时必须附上中文说明。
- 编写代码必须包含详细注释。
- 文件发生实际变更时，必须同步更新文件结构文档，确保文档始终反映当前结构。
- 文件结构文档采用“主参考 + 分文件夹渐进式披露”：主参考文档概述每个文件的职责、作用与内容摘要；各分文件夹内进一步披露具体代码及关键行号的作用。
- 每次对话结束后，都需要总结这一轮对话用户的问题和自己的回答，保存到 `memories/session/` 目录下，按日期+轮次命名，例如 `2026-06-24-01.md`。

## 开发建议

- 使用 VS Code agent 定制文件辅助 AI 工作流
- 如需验证是否生效，可在一个干净的 agent 会话里测试定制文件是否能被正确发现
