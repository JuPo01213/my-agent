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

This skill provides a methodology for initializing project conventions, organizing directory structure, archiving conversations, and turning established rules/processes into reusable skills. It is project-agnostic and adapts to any codebase.

## Capabilities

- **规则初始化**：定义并固化项目规则
- **结构整理**：删除冗余目录/文件，建立清晰的目录结构
- **对话归档**：按日期+轮次保存对话摘要
- **技能化**：把重复出现的工作流封装成技能

## How to Use

1. 明确项目类型与技术栈
2. 定义项目规则（语言、提交规范、工作流偏好等）
3. 整理目录结构，删除冗余，建立索引
4. 建立对话归档机制
5. 将重复工作流封装为技能

---

## 1. Project Rules Definition

### Steps

1. **识别约束**：确定项目的技术栈、语言、框架、平台
2. **定义工作流规则**：
   - 代码变更前是否需要提交
   - 提交信息格式
   - 代码注释要求
   - 是否允许使用特定工具/命令
3. **定义沟通规则**：
   - 对话语言
   - 回答风格
   - 是否需要定期总结
4. **写入 always-on 指令文件**：
   - VS Code 项目：写入 `AGENTS.md`
   - 其他环境：写入项目根目录的 always-on 配置文件
5. **验证生效**：在新会话中测试规则是否被正确加载

### Template

```markdown
## 项目规则

- **对话语言**：中文 / English（选择一项作为主要语言）
- **技术栈**：Python / JavaScript / Go / 其他
- **子代理**：适合子代理处理的任务应优先并行执行
- **工作流**：代码变更前须先提交；提交时必须附上说明
- **注释**：编写代码必须包含详细注释
- **结构文档**：文件发生实际变更时，必须同步更新结构索引文档
- **对话归档**：每次对话结束后，总结用户问题与回答，保存到指定目录
```

---

## 2. Directory Structure Cleanup

### Principles

- **单一职责**：每个目录/文件只承担一个明确职责
- **避免过深嵌套**：目录深度建议不超过 3-4 层
- **扁平化优先**：同级文件尽量放在同一目录，不要为单个文件建目录
- **命名一致性**：目录和文件命名遵循同一规范（kebab-case / snake_case / PascalCase）
- **索引先行**：先建立结构索引文档，再整理具体文件

### Steps

1. **盘点现有结构**：列出所有文件和目录
2. **识别冗余**：
   - 重复文件：用哈希校验，保留一份
   - 空目录：清理
   - 散落文件：移动到规范位置
3. **建立规范位置**：
   - 报告类：`docs/report/` 或 `reports/`
   - 技能类：`.github/skills/` 或 `.agents/skills/`
   - 配置类：项目根目录或 `.config/`
4. **更新索引**：建立或更新结构索引文档

### Structure Index Template

创建 `docs/structure.md`（或项目约定的其他路径），内容应包含：

```markdown
# 项目文件结构索引

本文档用于快速定位具体文件的内容行号。

## 核心文件

| 文件 | 路径 | 总行数 | 用途 |
|------|------|--------|------|
| always-on 指令 | `AGENTS.md` | N 行 | 项目规则与约定 |
| 结构索引 | `docs/structure.md` | N 行 | 文件行号索引 |

## 内容文件索引

| 文件 | 路径 | 段落 | 行号 | 内容 |
|------|------|------|------|------|
| 主要报告 | `docs/report/main.md` | 摘要 | 1-30 | 项目概述 |
| | | 架构 | 31-100 | 架构设计 |
```

---

## 3. Conversation Archival

### Steps

1. **确定存储位置**：建议 `memories/session/` 或项目约定的其他目录
2. **确定命名规则**：建议 `YYYY-MM-DD-NN.md`
3. **提取摘要**：
   - 用户的核心问题
   - 模型的主要回答
   - 关键决策和结论
4. **写入文件**

### Output Format

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

---

## 4. Skill Creation

### When to Create a Skill

- 某个工作流在对话中重复出现 3 次以上
- 规则需要固化并在多个会话中复用
- 团队协作需要标准化流程

### Skill Structure

```
.github/skills/
└── <skill-name>/
    ├── SKILL.md       # 必需：技能定义
    ├── scripts/       # 可选：辅助脚本
    ├── templates/     # 可选：输出模板
    └── references/    # 可选：参考资料
```

### SKILL.md Template

```yaml
---
name: <skill-name>
description: "<技能描述>。Use when <触发条件英文>。"
display_name: "<显示名称>"
description_zh: "<中文描述>"
description_en: "<英文描述>"
version: 1.0.0
visibility: "public"
---

# <技能标题>

## Capabilities

- **能力1**：说明
- **能力2**：说明

## Workflow

1. 步骤一
2. 步骤二
3. 步骤三

## Output Format

```markdown
# 输出示例
```

## Examples

- "触发词1"
- "触发词2"

## Resources

- 相关工具/文档/链接
```

### Skill Naming Convention

- 使用 kebab-case：`project-initializer`、`session-summarizer`
- 名称应反映技能的核心能力
- 避免通用名称：`helper`、`utils`、`tools`

---

## 5. Validation Checklist

完成项目初始化后，验证以下项目：

- [ ] always-on 指令文件已创建并生效
- [ ] 项目规则已明确写入指令文件
- [ ] 目录结构已清理，无冗余文件
- [ ] 结构索引文档已建立
- [ ] 对话归档机制已建立
- [ ] 重复工作流已封装为技能
- [ ] 所有变更已提交并附带说明

---

## Examples

- "初始化项目规则"
- "整理项目结构"
- "把报告文件按 docs/report 结构存放"
- "总结一下刚才的对话并保存"
- "把这次的工作流封装成一个技能"
- "创建项目结构索引文档"

## Resources

- `AGENTS.md` / always-on 指令：项目规则与约定
- `docs/structure.md` / 结构索引：文件行号索引
- `memory` tool：读取/写入记忆文件
- `git`：版本控制与提交
