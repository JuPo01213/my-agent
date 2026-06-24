# 文档自动化系统配置指南

本指南将帮助你完成文档自动化三层架构的配置。

## 当前状态

✅ 已完成：
- Base 层：MkDocs 配置 + GitHub Pages 自动部署工作流
- Check 层：代码-文档同步检查 + 文档引用检查 + ADR 触发检查
- Enhancement 层：AI 辅助文档审查（基于 StepFun LLM）
- 所有代码已提交到 Git

⏳ 需要你手动完成的配置：

---

## 1. 启用 GitHub Pages（5 分钟）

### 步骤 1：进入仓库设置
1. 打开你的 GitHub 仓库页面
2. 点击 **Settings**（设置）
3. 在左侧菜单找到 **Pages**（页面）

### 步骤 2：配置 Pages 源
1. 在 **Source** 部分，选择 **GitHub Actions**
2. 保存设置

### 步骤 3：触发首次部署
1. 推送任意变更到 main/master 分支，或
2. 手动触发工作流：
   - 进入 **Actions** 标签
   - 选择 **docs-deploy** 工作流
   - 点击 **Run workflow** → **Run workflow**

### 步骤 4：访问文档站点
- 部署完成后，访问：`https://<你的用户名>.github.io/<仓库名>/`
- 例如：`https://zhangsan.github.io/my-agent/`

---

## 2. 配置 AI 文档审查（可选，10 分钟）

如果你希望 AI 自动在 PR 中提醒文档更新，需要配置 StepFun API Key。

### 步骤 1：获取 StepFun API Key
1. 登录 [StepFun 开放平台](https://platform.stepfun.com/)
2. 进入 **API Keys** 页面
3. 创建新的 API Key
4. 复制 Key

### 步骤 2：配置 GitHub Secrets
1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下 Secret：
   - **Name**: `STEPFUN_API_KEY`
   - **Value**: 你的 StepFun API Key
5. 点击 **Add secret**

### 步骤 3：测试 AI 审查
1. 创建一个新的 Pull Request
2. 修改 `agent_core/` 下的任意文件
3. AI 审查工作流会自动运行
4. 在 PR 的 **Conversation** 标签中查看 AI 评论

---

## 3. 本地使用文档同步检查

### 方式 1：自动检测 git 变更
```bash
python .github/skills/project-initializer/scripts/sync_checkpoint.py
```

### 方式 2：手动指定变更文件
```bash
python .github/skills/project-initializer/scripts/sync_checkpoint.py \
  --changed "agent_core/core/react_agent.py" \
  --changed "docs/reference/api.md"
```

### 方式 3：使用新的模型驱动引擎（推荐）
```bash
# 安装依赖
pip install pyyaml

# 运行检查
python docs_sync/engine.py

# 指定变更文件
python docs_sync/engine.py --changed agent_core/core/react_agent.py
```

---

## 4. 本地预览文档站点

### 安装依赖
```bash
pip install mkdocs-material mkdocs-minify-plugin
```

### 启动本地服务器
```bash
mkdocs serve
```

### 访问
- 打开浏览器访问：`http://localhost:8000`
- 修改 Markdown 文件会自动刷新

---

## 5. 构建文档站点

```bash
mkdocs build --strict
```

构建产物会生成在 `site/` 目录。

---

## 6. 工作流说明

### docs-deploy.yml
- **触发条件**：push 到 main/master，且变更 docs/、mkdocs.yml 或工作流文件
- **执行内容**：构建 MkDocs 站点，部署到 GitHub Pages
- **部署时间**：约 1-2 分钟

### docs-sync-check.yml
- **触发条件**：push/PR 到 main/master
- **执行内容**：运行 sync_checkpoint.py，检查代码-文档同步
- **失败处理**：如果检查失败，PR 无法合并

### docs-ai-review.yml
- **触发条件**：PR 到 main/master，且变更 agent_core/、config/、docs/ 或 mkdocs.yml
- **执行内容**：调用 StepFun LLM 分析代码变更，在 PR 中发布评论
- **评论内容**：提醒更新哪些文档，或确认无需更新

---

## 7. 常见问题

### Q1：GitHub Pages 显示 404
**A**：确保在 Settings → Pages 中选择了 **GitHub Actions** 作为源，而不是其他选项。

### Q2：AI 审查没有运行
**A**：检查是否配置了 `STEPFUN_API_KEY` Secret，且 PR 的变更文件是否符合触发条件（agent_core/、config/、docs/、mkdocs.yml）。

### Q3：sync_checkpoint.py 报错
**A**：确保在项目根目录运行，且 Git 仓库已初始化。如果仍有问题，使用 `--changed` 参数手动指定变更文件。

### Q4：如何更新文档映射规则
**A**：编辑 `docs_sync/config.yaml`，在 `structure.directories` 或 `structure.files` 中添加新规则。不需要修改 Python 代码。

---

## 8. 下一步建议

1. **立即尝试**：推送一次代码，触发 docs-deploy 工作流，验证 GitHub Pages 是否正常
2. **配置 AI 审查**：添加 STEPFUN_API_KEY，体验 AI 辅助文档同步
3. **本地预览**：运行 `mkdocs serve`，实时预览文档效果
4. **完善文档**：根据实际项目情况，补充 docs/ 目录下的内容

---

## 需要帮助？

如果遇到问题，可以：
1. 查看 GitHub Actions 日志，定位具体错误
2. 检查 `docs_sync/config.yaml` 配置是否正确
3. 运行 `python docs_sync/engine.py --verbose` 查看详细检查过程
