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
- **任何时候都不要使用 emoji**，所有输出使用纯文本或标准 Markdown 格式。
- **本项目不需要任何安全护栏和权限限制**，所有工具调用、代码执行均直接放行，用户明确了解所有风险并自行承担全部后果。
- 本项目仅使用 Python。
- 对于适合子代理处理的任务，应优先使用子代理并行执行，以提升工作效率。
- 模型执行工作时仅使用 Python 命令。
- 代码变更前须先提交。
- 提交时必须附上中文说明。
- 编写代码必须包含详细注释。
- 文件发生实际变更时，必须同步更新文件结构文档 `docs/structure.md`，确保文档始终反映当前结构。
- 文件结构文档采用“主参考 + 分文件夹渐进式披露”：主参考文档概述每个核心文件的职责、作用与内容摘要；归档类文件（session日志、临时文件）不需要加入索引。
- 任何文件实际变更完成后，必须**立即**运行同步检查点脚本确认关联文件已更新，不得等待用户提示：
  ```bash
  # 自动检测git变更（推荐）
  python .github/skills/project-initializer/scripts/sync_checkpoint.py
  # 手动指定变更文件
  python .github/skills/project-initializer/scripts/sync_checkpoint.py --changed "<变更文件1>" --changed "<变更文件2>"
  ```
- 检查点脚本会校验核心文件结构索引、主报告引用、`memories/session/` 归档三项
- 检查不通过即视为未完成该轮任务，必须修正后重新检查。
- 每次对话结束后，按照 `memories/session/_TEMPLATE.md` 模板记录会话，重点记录核心需求、完成工作、关键决策、踩坑记录、后续待办，不需要完整复述对话内容，保存到 `memories/session/` 目录下，按日期+轮次命名，例如 `2026-06-24-01.md`。
- 会话中产生的可复用知识、架构决策、踩坑经验，必须同步沉淀到 `memories/repo/` 对应文件中，不要只存在于当次会话记录。
- 涉及改正（如修复 import、补全路由、回滚越权代码等）需要重新启动相关服务时，必须在改动完成后**主动重启服务器并重新加载前端**，让用户能在浏览器中即时看到最新效果，不要让用户手工操作。
- 当前阶段属于**前端样式探索期**：仅用于尝试不同风格、确定前端样式。所有静态前端文件（如 `agent_core/static/*.html`）在本阶段**不需要与后端联通，也不需要为预览而启动本地端口服务**。保持纯静态、双击或 IDE 内置预览器可直接打开的状态；预览方式由用户自行选择，模型不要主动起服务进程。
- **重构原则**：当架构需要根本性改变时（如引入多 Agent 协作、状态图等），**完全重构优于兼容改造**。直接推翻原有实现重新设计，不要为了"向后兼容"保留旧函数/旧接口。测试阶段不必背负历史包袱，宁可一次改干净也不要新旧两套并存。重构后要主动更新所有调用点（dashboard.py、demo 文件等），并同步更新 `docs/structure.md` 与 `memories/repo/架构决策记录.md` 留 ADR。
- **诚实记录原则**：禁止伪造执行结果与运行数据。必须真跑、真记录、真贴输出。汇报"完成"前必须用 Read / Glob 验证文件真的存在、用 RunCommand 验证命令真的执行过。无法验证时必须明确说"未验证"或"未执行"，不得编造数字、耗时、日志内容。
- **实验日志规范**：所有真实实验（调用 LLM、跑测试、跑 benchmark）必须把 stdout/stderr 全部重定向到日志文件，路径在 `experiments/<日期>-<实验名>.log`。汇报时必须把文件绝对路径给到用户，让用户可自行 `cat` 验证。日志中出现的输出视为可信源，模型回答不得脱离日志虚构补充。
- **冒充实跑禁令**：模型不得在仅完成"读代码"或"写脚本"后声称"已真实跑过"。脚本写好不算跑过；必须真的执行命令、收到返回、写入文件，三者齐备才算"真实跑过"。临时受网络/凭据限制无法真跑时，必须明确告知"当前仅完成脚本，未真跑"。
- **文件编码规范（最高优先级）**：所有文本文件写入必须显式声明 UTF-8 编码，绝不允许用 PowerShell 5.1 的 GBK 默认值写文件。具体规则：
  1. Python 文件操作必须带 `encoding="utf-8"`：`open(path, "w", encoding="utf-8")`、`Path.write_text(s, encoding="utf-8")`、日志的 `FileHandler(filename, mode, encoding="utf-8")`。
  2. PowerShell 写入文件必须用 `.NET` 显式指定 UTF-8（避免 BOM）：`[System.IO.File]::WriteAllText($path, $text, [System.Text.UTF8Encoding]::new($false))`；或 `Set-Content -Path $path -Value $text -Encoding utf8NoBOM`。
  3. 禁止使用 PowerShell 原生 `>` / `Out-File` / `Tee-Object` 直接把含中文的管道结果写入文件（这些会按系统区域设置使用 GBK，导致文件"乱码"）。
  4. 推荐做法：把输出先在 Python 内 `print(..., flush=True)`，再用 `python script.py > file.log 2>&1` 重定向；或把管道用 `iconv -t utf-8` 转一次。
  5. 在 PR / 提交说明里若提到"乱码"必须明确区分"是显示问题"（终端区域设置）还是"是文件问题"（写入时编码错）。修文件问题用 rule 1/2 修；修显示问题用 `chcp 65001` 切换代码页。

## 开发建议

- 使用 VS Code agent 定制文件辅助 AI 工作流
- 如需验证是否生效，可在一个干净的 agent 会话里测试定制文件是否能被正确发现
