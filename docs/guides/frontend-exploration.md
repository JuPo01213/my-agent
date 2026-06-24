# 前端探索期说明

本文档说明当前前端样式探索期的约束和规范。

## 阶段定义

当前阶段属于**前端样式探索期**：仅用于尝试不同风格、确定前端样式。

## 约束

- 所有静态前端文件（如 `agent_core/static/*.html`）**不需要与后端联通**
- **不需要为预览而启动本地端口服务**
- 保持纯静态，双击或 IDE 内置预览器可直接打开
- 预览方式由用户自行选择，模型不要主动起服务进程

## 当前文件

- `agent_core/static/bubble.html`：气泡对话界面
- `agent_core/static/bubble-adapter.js`：气泡适配脚本
- `agent_core/static/index.html`：基础页面
- `agent_core/static/vue.html`：Vue 示例页面

## 后续演进

当前阶段结束后，如需前后端联通，应在 `multi_agent/` 上层新建 `ui/` 层，而不是修改 core/。
