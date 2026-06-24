---
name: session-summarizer
description: "自动记录对话中的问题、报错、解决过程和结论。Use when 对话结束、问题已解决、需要沉淀会话经验、总结本轮工作、或用户要求保存对话记录时自动触发。"
display_name: "Session Summarizer"
display_name_en: "Session Summarizer"
description_zh: "自动记录对话中的问题、报错、解决过程和结论"
description_en: "Automatically record problems, errors, solutions, and outcomes from conversations"
version: 1.0.0
visibility: "public"
---

# Session Summarizer

自动把每轮对话沉淀为结构化摘要，重点记录：**什么问题 → 做了什么 → 遇到什么错 → 怎么解决的 → 最终结果**。

## Capabilities

- **问题追踪**：识别用户提出的问题或遇到的障碍
- **动作记录**：记录模型执行的关键操作（读文件、改代码、运行命令等）
- **错误捕获**：记录执行过程中出现的错误和异常
- **解决链路**：记录问题是如何被解决的
- **结论沉淀**：提取最终交付物和可复用的经验

## When to Trigger

- 用户问题已解决，对话自然结束时
- 用户明确要求"保存对话记录"时
- 完成一个子任务并准备进入下一阶段时
- 遇到并解决了一个错误后

## Workflow

### Step 1: 回顾对话内容

快速扫描当前对话，提取以下信息：

1. **用户问题**：用户最初想解决什么问题？中间有没有改变方向？
2. **模型动作**：执行了哪些具体操作？（读文件、修改文件、运行命令、调用工具等）
3. **遇到的错误**：有没有报错？错误信息是什么？
4. **解决过程**：是如何定位问题、尝试方案、最终解决的？
5. **最终结果**：交付了什么？用户是否满意？

### Step 2: 结构化摘要

按照以下格式组织内容：

```markdown
# 对话摘要

**日期**：YYYY-MM-DD
**轮次**：NN（从 01 开始递增）

## 用户问题
- 核心问题1
- 核心问题2（如果有分支）

## 模型动作
1. 动作1（例如：读取文件 X）
2. 动作2（例如：修改文件 Y 的 Z 行）
3. 动作3（例如：运行命令验证）

## 遇到的错误
- 错误1：错误描述 → 解决方法
- 错误2：错误描述 → 解决方法

## 最终结果
- 交付物1
- 交付物2
- 后续步骤（如果有）
```

### Step 3: 写入文件

1. **确定文件路径**：`memories/session/YYYY-MM-DD-NN.md`
2. **检查是否已存在**：
   - 如果不存在，创建新文件
   - 如果存在且内容不同，覆盖更新
3. **写入内容**：使用 `memory` 工具的 `create` 或 `str_replace` 命令

### Step 4: 验证与同步

1. 如果是项目文件变更触发的总结，运行：
   ```bash
   python .github/skills/project-initializer/scripts/sync_checkpoint.py --changed "<变更文件1>" --changed "<变更文件2>"
   ```
2. 检查同步结果，确保 `docs/structure.md` 已更新

## Output Format

最终输出给用户的确认消息：

```
对话记录已保存到 `memories/session/YYYY-MM-DD-NN.md`。

记录内容：
- 用户问题：...
- 模型动作：...
- 遇到的错误：...
- 最终结果：...
```

## Principles

- **简洁**：只记录关键信息，不要事无巨细
- **可追溯**：文件路径、命令、错误信息要具体
- **可复用**：记录解决思路，方便后续类似问题时参考
- **自动触发**：每轮对话结束后主动执行，不需要用户提醒
