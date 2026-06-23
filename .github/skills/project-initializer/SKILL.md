---
name: project-initializer
description: "初始化项目规则、整理目录结构、对话归档与知识沉淀。Use when the user asks for organize project, cleanup structure, archive conversation, init project rules, 整理项目, 整理结构, 保存对话, 总结规则, 对话归档, 初始化项目, 自定义规则, 或需要把规则和过程固化成技能时。"
display_name: "project-initializer"
display_name_en: "project-initializer"
description_zh: "初始化项目规则、整理目录结构、对话归档与知识沉淀"
description_en: "Initialize project rules, organize structure, archive conversations, and capture knowledge"
version: 1.0.0
visibility: "public"
---

# Project Initializer

This skill manages project conventions, directory cleanup, conversation archiving, and turning established rules/processes into reusable skills.

## Capabilities

- **规则初始化**：定义并固化项目规则
- **结构整理**：删除冗余目录/文件，建立清晰的目录结构
- **对话归档**：按日期+轮次保存对话摘要到 `memories/session/`
- **技能化**：把重复出现的工作流封装成技能

## Project Rules

These rules are established from prior conversations and must be followed:

1. **中文最高优先级**：对话内容均须使用中文
2. **Python 限定**：本项目仅使用 Python
3. **子代理优先**：适合子代理处理的任务应优先并行执行
4. **Python 命令**：模型执行工作时仅使用 Python 命令
5. **先提交**：代码变更前须先提交
6. **中文说明**：提交时必须附上中文说明
7. **详细注释**：编写代码必须包含详细注释
8. **结构文档同步**：文件发生实际变更时，必须同步更新 `docs/structure.md`
9. **渐进式披露**：文件结构文档采用"主参考 + 分文件夹渐进式披露"
10. **对话总结**：每次对话结束后，总结用户问题与回答，保存到 `memories/session/` 目录

## Directory Structure

```
my-agent/
├── AGENTS.md                      # always-on 指令，第一入口
├── .github/skills/                # 全部技能资产
│   ├── arxiv-watcher/
│   ├── autoresearch/
│   ├── deep-research/
│   ├── market-researcher/
│   ├── project-initializer/       # 本技能
│   ├── tavily/
│   ├── web-search-exa/
│   └── xurl/
├── docs/
│   ├── structure.md               # 文件结构索引（按文件+行号索引）
│   └── report/
│       ├── 写一个自己的智能体_完整调研与最佳实践报告.md
│       └── reports/               # 分技能调研报告
└── memories/
    └── session/                   # 对话总结存储目录
```

## Cleanup Workflow

When organizing project structure:

1. 识别重复/冗余文件（用哈希校验）
2. 删除重复文件
3. 扁平化目录结构（避免过深嵌套）
4. 移动散落文件到规范位置
5. 清理空目录
6. 更新 `docs/structure.md`

## Conversation Archival

After each conversation:

1. 提取用户核心问题
2. 提取模型主要回答
3. 生成中文摘要
4. 保存到 `memories/session/YYYY-MM-DD-NN.md`

Format:
```markdown
# 对话摘要

**日期**：YYYY-MM-DD
**轮次**：NN

## 用户问题
- 问题1
- 问题2

## 模型回答
- 回答1
- 回答2

## 关键结论
- 结论1
- 结论2
```

## Skill Creation Workflow

When turning a workflow into a skill:

1. 提取对话中的工作流模式
2. 明确触发条件（中文 + 英文）
3. 定义输入/输出格式
4. 编写 SKILL.md 包含：
   - frontmatter（name、description、description_zh、description_en、version、visibility）
   - Capabilities
   - Workflow（步骤化）
   - Output Format（示例）
   - Examples（触发词）
   - Resources（相关工具/文档）

## Indexing Guidelines

`docs/structure.md` 是文件结构索引，用于快速定位具体文件的内容行号。

- 不索引 `AGENTS.md`（它是第一入口）
- 技能文件（`.github/skills/*/SKILL.md`）已按渐进式披露组织，不在此重复索引
- 只索引需要按行号精确定位的核心文件
- 使用表格形式：段落 | 行号 | 内容

## Examples

- "整理项目结构"
- "把报告文件按 docs/report 结构存放"
- "总结一下刚才的对话"
- "把这次的对话内容保存一下"
- "创建一个技能来总结对话"
- "初始化项目规则"

## Resources

- `AGENTS.md`: 项目规则与约定
- `docs/structure.md`: 文件结构索引
- `memory` tool: 读取/写入记忆文件
