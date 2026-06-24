---
name: project-initializer
description: "初始化项目规则、整理目录结构、对话归档与知识沉淀。Use when the user asks for organize project, cleanup structure, archive conversation, init project rules, 整理项目, 整理结构, 保存对话, 总结规则, 对话归档, 初始化项目, 自定义规则, 新建项目, 或需要把规则和过程固化成技能时。"
display_name: "project-initializer"
display_name_en: "project-initializer"
description_zh: "初始化项目规则、整理目录结构、对话归档与知识沉淀，支持跨项目复用"
description_en: "Initialize project rules, organize structure, archive conversations, and capture knowledge, reusable across projects"
version: 2.0.0
visibility: "public"
---

# Project Initializer

This skill provides a complete, production-ready methodology for initializing project conventions, organizing directory structure, archiving conversations, and turning established rules/processes into reusable assets. It is project-agnostic and can be applied to any codebase across different programming languages.

## Capabilities

- **一键初始化新项目**：基于模板自动生成标准项目结构、规则文件、记忆目录
- **规则初始化**：定义并固化项目规则，支持自定义语言、安全策略、工作流
- **结构整理**：删除冗余目录/文件，建立清晰的目录结构和索引文档
- **对话归档**：按日期+轮次保存结构化对话摘要，支持关键词检索
- **知识沉淀**：自动将可复用经验、架构决策、踩坑记录沉淀到持久化记忆
- **同步检查**：内置检查点脚本，自动验证文档同步、引用完整性、归档状态
- **跨项目复用**：所有模板和脚本通用，换项目直接复制技能目录即可使用

## 跨项目复用方法

在新项目中使用本技能非常简单：
1. 将 `.github/skills/project-initializer/` 整个目录复制到新项目的对应位置
2. 运行初始化流程，自动生成标准目录结构和模板文件
3. 根据项目需求调整模板中的变量（编程语言、安全策略等）
4. 所有脚本和模板无需修改即可直接使用

## How to Use

### 新项目初始化流程
1. 明确项目类型、技术栈、编程语言
2. 基于模板生成标准目录结构：
   - `docs/`：文档目录，包含 `structure.md` 结构索引
   - `memories/session/`：会话归档目录，包含会话模板
   - `memories/repo/`：项目级持久记忆目录，包含项目约定、架构决策记录
   - `.github/skills/project-initializer/`：本技能目录
3. 基于 `AGENTS.md.template` 生成项目根目录的 `AGENTS.md`，配置项目规则
4. 基于 `structure.md.template` 生成 `docs/structure.md` 结构索引
5. 复制 `sync_checkpoint.py` 脚本到技能的 `scripts/` 目录
6. 验证检查点脚本可正常运行

### 日常使用流程
1. 代码/文档变更后，直接运行 `python .github/skills/project-initializer/scripts/sync_checkpoint.py` 自动检查同步状态
2. 每轮对话结束后，基于 `session_TEMPLATE.md` 记录会话
3. 重要决策和踩坑经验同步沉淀到 `memories/repo/` 对应文件
4. 定期整理结构索引，保持文档与代码一致

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

## 3. Conversation Archival & Knowledge Precipitation

### 记忆分层架构
采用三层记忆架构，确保知识不丢失且易于检索：
1. **会话记忆（`memories/session/`）**：按日期+轮次归档的会话记录，结构化存储核心信息
2. **仓库记忆（`memories/repo/`）**：项目级持久知识，包含项目约定、架构决策、踩坑记录、最佳实践
3. **用户记忆（`/memories/`）**：跨项目通用经验、用户偏好、通用模式

### 会话记录规范
1. **存储位置**：`memories/session/`
2. **命名规则**：`YYYY-MM-DD-NN.md`（NN为当天轮次，从01开始）
3. **记录模板**：使用 `templates/session_TEMPLATE.md`，包含：
   - 核心信息（关键词、涉及文件、变更类型）
   - 用户需求（仅核心问题，不完整复述对话）
   - 完成工作（实际变更和结论，不重复解释内容）
   - 关键决策与结论（选型、规则调整及原因）
   - 踩坑记录（问题、根因、解决方案）
   - 后续待办（明确行动项）
4. **记录原则**：重点记录决策、变更、踩坑、待办，不需要完整复述对话内容，降低记录成本

### 知识沉淀规范
1. 会话中产生的可复用知识必须同步沉淀到 `memories/repo/`：
   - 项目规则、约定 → `项目约定.md`
   - 架构选型、技术决策 → `架构决策记录.md`（ADR格式）
   - 踩坑经验、解决方案 → `踩坑记录.md`
   - 最佳实践、编码规范 → `最佳实践.md`
2. 跨项目通用的经验沉淀到用户记忆 `/memories/` 对应文件
3. 沉淀原则：只记录可复用的结论和方法，不记录单次对话的临时内容

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

## 5. Sync Checkpoint

### 检查点脚本
技能内置 `scripts/sync_checkpoint.py` 脚本，每次变更后自动验证同步状态：
- **自动检测变更**：默认自动识别git工作区的变更文件，无需手动传参
- **排除归档文件**：自动排除session日志、临时文件等不需要索引的文件
- **三项核心检查**：
  1. 核心文件是否已在 `docs/structure.md` 中建立索引
  2. 新增报告是否已在主报告中引用
  3. 最近会话是否已归档
- **使用方法**：
  ```bash
  # 自动检测git变更（推荐）
  python .github/skills/project-initializer/scripts/sync_checkpoint.py
  # 手动指定变更文件
  python .github/skills/project-initializer/scripts/sync_checkpoint.py --changed "file1" --changed "file2"
  ```

## 6. Validation Checklist

完成项目初始化后，验证以下项目：

- [ ] 标准目录结构已创建（docs/、memories/session/、memories/repo/、.github/skills/）
- [ ] AGENTS.md 已基于模板生成，规则符合项目需求
- [ ] docs/structure.md 已创建，核心文件已建立索引
- [ ] memories/session/_TEMPLATE.md 会话模板已就位
- [ ] memories/repo/ 下已初始化项目约定和架构决策记录文件
- [ ] sync_checkpoint.py 脚本可正常运行，检查通过
- [ ] 所有模板文件已复制到 templates/ 目录
- [ ] 结构索引文档已建立
- [ ] 对话归档机制已建立
- [ ] 重复工作流已封装为技能
- [ ] 所有变更已提交并附带说明
- [ ] **同步检查点已通过**：运行 `python scripts/sync_checkpoint.py --changed "<变更文件>"` 验证关联文件已更新

### 同步检查点规则

任何文件实际变更完成后，必须**立即**运行检查点脚本：

```bash
python .github/skills/project-initializer/scripts/sync_checkpoint.py \
  --changed "<变更文件1>" \
  --changed "<变更文件2>"
```

检查点会校验：
1. `docs/structure.md` 是否包含新增/修改文件的索引
2. 若变更涉及报告内容，主报告参考来源是否已更新
3. 当前对话是否已创建 session 归档

检查不通过即视为未完成该轮任务，必须修正后重新检查。

---

## Examples

- "初始化项目规则"
- "整理项目结构"
- "把报告文件按 docs/report 结构存放"
- "总结一下刚才的对话并保存"
- "把这次的工作流封装成一个技能"
- "创建项目结构索引文档"
- "运行同步检查点验证关联文件已更新"

## Resources

- `AGENTS.md` / always-on 指令：项目规则与约定
- `docs/structure.md` / 结构索引：文件行号索引
- `scripts/sync_checkpoint.py` / 同步检查点：变更后自动校验关联文件
- `memory` tool：读取/写入记忆文件
- `git`：版本控制与提交
