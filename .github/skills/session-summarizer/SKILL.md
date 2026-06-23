---
name: session-summarizer
description: "定期总结对话内容并保存到 memories/session/。Use when the user asks for conversation summary, dialog recap, session summary, 对话总结, 总结对话, 保存对话摘要, 或需要定期整理对话记录时。"
display_name: "session-summarizer"
display_name_en: "session-summarizer"
description_zh: "定期总结对话内容并保存到 memories/session/"
description_en: "Summarize conversations and save to memories/session/"
version: 1.0.0
visibility: "public"
---

# Session Summarizer

This skill provides a structured workflow to summarize user-agent conversations and store them for future reference.

## Capabilities

- **对话总结**：提取用户问题与模型回答的关键内容
- **摘要生成**：生成简明扼要的对话摘要
- **归档保存**：按日期+轮次命名，保存到 `memories/session/` 目录
- **定期回顾**：支持定期回顾历史对话摘要

## Workflow

1. **读取对话内容**：获取当前对话的完整内容
2. **提取关键信息**：
   - 用户的核心问题
   - 模型的主要回答
   - 关键决策和结论
3. **生成摘要**：
   - 使用中文总结
   - 保持简洁、可执行
   - 突出重要信息
4. **保存文件**：
   - 路径：`memories/session/`
   - 命名格式：`YYYY-MM-DD-NN.md`
   - 例如：`2026-06-24-01.md`

## Output Format

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

## Examples

- "总结一下刚才的对话"
- "把这次的对话内容保存一下"
- "对话总结"
- "定期整理对话记录"

## Resources

- `memory` tool: 用于读取和写入记忆文件
- `docs/structure.md`: 文件结构索引
