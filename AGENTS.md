---
name: my-agent
description: "Use when: working in my-agent workspace, building or extending AI agent features, creating skills, prompts, instructions, agents, hooks, or tools for coding assistants; 适用于 my-agent 工作区、构建或扩展 AI agent 功能、创建技能、提示词、指令、agent、hooks 或编码助手工具。"
---

# Agent Workspace

此工作区用于存放 AI agent 定制文件及相关代码。

## 文件布局

- `.github/instructions/` — 通过 `applyTo` 定义文件级指令
- `.github/prompts/` — 参数化斜杠命令提示
- `.github/agents/` — 自定义 agent 定义
- `.github/hooks/` — 生命周期钩子 JSON 配置
- `.github/skills/` — 打包的工作流资产
- `AGENTS.md` — 本工作区默认的 always-on agent 指令

## 约定

- 指令保持简洁、可执行
- 优先链接文档，不要重复内嵌大段内容
- 相关处使用 YAML frontmatter：`name`、`description`、`applyTo`
- 校验 YAML 语法：使用空格而非 tab；description 含冒号时加引号

## 项目规则

- 本项目使用 Python 语言。
- 对话时，包括推理、思考、回答内容，都必须使用中文沟通。
- 模型在工作过程中也只能使用 Python 命令。
- 代码变更前须先提交。

## 开发建议

- 使用 VS Code agent 定制文件辅助 AI 工作流
- 如需验证是否生效，可在一个干净的 agent 会话里测试定制文件是否能被正确发现
