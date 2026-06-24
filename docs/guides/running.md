# 运行指南

本文档描述如何运行 my-agent 项目的各个组件。

## 运行测试

```bash
python -m unittest discover -s tests -v
```

## 运行 Demo

```bash
# 多 Agent 架构演示
python agent_core/demos/multi_agent_demo.py

# 关系驱动演示
python agent_core/demos/relationship_demo.py

# 场景实验
python experiments/2026-06-24-scenario.py
```

## 运行同步检查点

```bash
# 自动检测 git 变更
python .github/skills/project-initializer/scripts/sync_checkpoint.py

# 手动指定变更文件
python .github/skills/project-initializer/scripts/sync_checkpoint.py --changed "file1.py" --changed "file2.md"
```

## 前端预览

当前阶段属于前端样式探索期，所有静态前端文件通过以下方式预览：

- 双击 HTML 文件直接打开
- 使用 IDE 内置预览器
- 不需要启动本地端口服务，不需要与后端联通

## 实验日志

实验日志规范、路径约定和真实性要求，统一见 `docs/guides/development.md`。
