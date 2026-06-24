# ADR-011: max_steps 触发条件 + 多模块单元测试基线完成

- **日期**：2026-06-24
- **状态**：已采纳，被 ADR-012 修订

## 背景

第 11 轮任务"补充单元测试 + 修复附带问题"，按 ADR-010 后续任务清单执行：

- P0：`Blackboard.update/ask/answer/snapshot/is_solved` 行为测试
- P0：`ControlShell._select_source` 三种 strategy 测试
- P1：`Command.goto_agent/done` 工厂方法测试

## 决策

新增 3 个测试文件 + 真跑验证 + 修复两处附带问题：

- `tests/test_blackboard.py`：19 个测试，覆盖 Blackboard 共享状态所有方法
- `tests/test_command.py`：14 个测试，覆盖 Command dataclass 行为 + 工厂方法 + Blackboard 联动
- `tests/test_control_shell.py`：19 个测试，覆盖 `_select_source` 三种 strategy + `run()` 端到端 6 个场景

## 附带问题 1：max_steps 触发条件

- 现象：初版 `test_max_steps_timeout` 期望"agent 永不 terminate → status=timeout"，但实际得到 `status=solved`
- 根因：单 Agent 在 first_match 下被激活后下一轮 0 候选 → 早退 solved；2 Agent 跑 2 步同样 0 候选
- 真实触发条件：`for-else` 走 timeout 分支要求 `_select_source()` 永远能返回非 None
- 解：用 **6 个 Agent + max_steps=5**（Agent 数 ≥ max_steps 才能耗尽循环）
- 守护测试：`tests/test_control_shell.py::TestControlShellRun::test_max_steps_timeout`

## 附带问题 2：sync_checkpoint.py 内 emoji 违反 AGENTS.md "任何时候不要使用 emoji" 规则

- 现象：脚本 16 处使用 ❌ ✅ ⚠️ 📋 🔄 ⏭️ 等 Unicode 符号，PowerShell 默认 GBK 编码下触发 `UnicodeEncodeError`
- 决策：替换为中文文本标签（`[通过]` / `[错误]` / `[警告]` / `[跳过]` / `[同步]`）
- 验证：emoji 残留 0 处；脚本现在无需环境变量即可在任意编码下跑通

## 关联教训

1. **测试设计需要尊重被测系统的"实际触发条件"**：单 Agent + first_match 不可能触发 max_steps，这是 ControlShell 的本质设计；用 6 Agent 才能让 for 循环正常耗尽
2. **附带问题的修复优先级**：发现 emoji 违反规则是顺手的事；不修会一直有 `UnicodeEncodeError` 兜底代码到处贴
3. **PowerShell + GBK 编码 + emoji 是经典踩坑**：脚本侧合规（用纯文本）比环境侧兜底（设 PYTHONIOENCODING）更稳

## 当前测试统计（2026-06-24 第 11 轮完成时）

- 总数：**84 个测试**
- 全部通过：true
- 覆盖模块：`_parse_precondition` + `run_loop` + `Blackboard` + `Command` + `ControlShell._select_source` + `ControlShell.run`
- 平均执行时间：0.010s

## 后果

- 核心模块入口 + 关键分支 100% 有测试守护
- 后续 PR 改 Blackboard / Command / ControlShell 时 0.01s 跑 84 个测试确认未破坏
- sync_checkpoint.py 现在的 emoji 修复让脚本可在任何编码环境直接运行

## 修订说明

本 ADR 的"84 个测试"结论被 ADR-012 修订为"8 个真风险点守护测试"。详见 ADR-012。
