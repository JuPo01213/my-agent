# 贡献指南

感谢你对 my-agent 项目的关注。当前阶段以个人探索和实验为主，以下指南帮助你理解项目约定和协作方式。

## 项目规则

项目规则由 `AGENTS.md` 统一约束，核心原则包括：中文优先、禁止 emoji、仅使用 Python、变更前先提交、详细注释、诚实记录、实验日志规范、文件编码规范等。

## 开发流程

1. 修改代码前先提交当前状态
2. 实现功能或修复问题
3. 更新相关文档（`docs/structure.md`、README 等）
4. 运行测试：`python -m unittest discover -s tests -v`
5. 运行同步检查点：`python .github/skills/project-initializer/scripts/sync_checkpoint.py`
6. 提交变更，附上中文说明

## 文档规范

- 文件发生实际变更时，必须同步更新文件结构文档 `docs/structure.md`
- 会话中产生的可复用知识、架构决策、踩坑经验，必须同步沉淀到 `memories/repo/` 对应文件中
- 架构决策必须同步 ADR 和 `docs/adr/` 目录

## 详细规范

完整开发规范、代码规范、测试原则、实验规范、重构原则，统一见 `docs/guides/development.md`。
