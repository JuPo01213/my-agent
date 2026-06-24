"""
docs_sync/ai_reviewer.py

用途：
  基于大模型自动分析代码变更，判断是否需要更新文档，
  并在 PR 中自动评论提醒。

工作流：
  1. 获取 PR 的代码变更文件列表
  2. 基于 CODE_TO_DOC_MAP 和目录约定，推断受影响的文档
  3. 调用 LLM 分析变更内容，判断文档是否需要更新
  4. 在 PR 中发布评论，提醒更新文档

环境变量：
  - STEPFUN_API_KEY：StepFun API 密钥
  - STEPFUN_BASE_URL：StepFun API 地址
  - STEPFUN_MODEL：模型名称，默认 step-3.7-flash
  - GITHUB_TOKEN：GitHub Actions 自动提供
  - PR_NUMBER：PR 编号，GitHub Actions 自动提供
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("[错误] 缺少 openai 依赖，请运行: pip install openai")
    sys.exit(1)


WORKSPACE = Path(__file__).resolve().parents[1]
DOCS_DIR = WORKSPACE / "docs"

# 代码 -> 文档映射表
CODE_TO_DOC_MAP = {
    "agent_core/core/react_agent.py": [
        "docs/reference/api.md",
        "docs/report/ReAct智能体实现评估与改进路线图.md",
    ],
    "agent_core/core/tool_registry.py": [
        "docs/reference/api.md",
    ],
    "agent_core/config.py": [
        "docs/reference/configuration.md",
    ],
    "agent_core/multi_agent/agent_api.py": [
        "docs/reference/api.md",
    ],
    "agent_core/multi_agent/tool_caller.py": [
        "docs/reference/api.md",
    ],
    "agent_core/multi_agent/tool_filter.py": [
        "docs/reference/api.md",
    ],
    "agent_core/multi_agent/relationship.py": [
        "docs/reference/api.md",
        "docs/report/关系驱动多Agent协作架构实现方案.md",
        "docs/adr/006-relationship-engine.md",
    ],
    "agent_core/server/server.py": [
        "docs/reference/api.md",
    ],
    "agent_core/frontend/adapter.py": [
        "docs/reference/api.md",
    ],
    "agent_core/frontend/bus.py": [
        "docs/reference/api.md",
    ],
    "agent_core/frontend/events.py": [
        "docs/reference/api.md",
    ],
    "config/agents.yaml": [
        "docs/reference/configuration.md",
    ],
    "config/relationships.yaml": [
        "docs/reference/configuration.md",
    ],
}

# 目录职责约定：即使文件不在映射表中，也能根据目录推断文档
DIRECTORY_DOC_RULES = {
    "agent_core/core/": ["docs/reference/api.md"],
    "agent_core/multi_agent/": ["docs/reference/api.md", "docs/adr/"],
    "agent_core/server/": ["docs/reference/api.md"],
    "agent_core/frontend/": ["docs/reference/api.md"],
    "agent_core/config.py": ["docs/reference/configuration.md"],
    "config/": ["docs/reference/configuration.md"],
}

# 架构相关目录，变更时需要检查 ADR
ARCHITECTURE_DIRS = [
    "agent_core/core/",
    "agent_core/multi_agent/",
    "agent_core/server/",
    "agent_core/frontend/",
]


def get_changed_files() -> list[str]:
    """获取当前 PR 的变更文件列表。"""
    # 在 GitHub Actions 环境中，使用 github.event.pull_request.changed_files
    # 这里通过 git diff 获取
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=True,
        )
        files = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                files.append(line.strip())
        return files
    except Exception:
        return []


def infer_affected_docs(changed_files: list[str]) -> tuple[list[str], list[str]]:
    """
    根据变更文件推断受影响的文档。
    返回：(affected_docs, architecture_changed)
    """
    affected_docs = set()
    architecture_changed = False
    
    for file_path in changed_files:
        rel_path = file_path.replace("\\", "/")
        
        # 1. 精确匹配映射表
        if rel_path in CODE_TO_DOC_MAP:
            affected_docs.update(CODE_TO_DOC_MAP[rel_path])
        
        # 2. 目录约定匹配
        for dir_pattern, docs in DIRECTORY_DOC_RULES.items():
            if rel_path.startswith(dir_pattern):
                affected_docs.update(docs)
        
        # 3. 检查是否是架构相关变更
        for arch_dir in ARCHITECTURE_DIRS:
            if rel_path.startswith(arch_dir):
                architecture_changed = True
                break
    
    # 过滤不存在的文档
    valid_docs = []
    for doc in affected_docs:
        if (WORKSPACE / doc).exists():
            valid_docs.append(doc)
    
    return sorted(valid_docs), architecture_changed


def get_file_diff(file_path: str) -> str:
    """获取文件的 diff 内容。"""
    try:
        result = subprocess.run(
            ["git", "diff", "origin/main...HEAD", "--", file_path],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout[:2000]  # 限制长度
    except Exception:
        return ""


def analyze_with_llm(changed_files: list[str], affected_docs: list[str]) -> str:
    """
    使用 LLM 分析代码变更，判断文档是否需要更新。
    返回 AI 的分析结果。
    """
    api_key = os.getenv("STEPFUN_API_KEY")
    base_url = os.getenv("STEPFUN_BASE_URL", "https://api.stepfun.com/step_plan/v1")
    model = os.getenv("STEPFUN_MODEL", "step-3.7-flash")
    
    if not api_key:
        return "[跳过] 未配置 STEPFUN_API_KEY，跳过 AI 分析"
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 构建 prompt
    prompt_parts = [
        "你是文档同步审查助手。请分析以下代码变更，判断是否需要更新文档。",
        "",
        "## 变更文件",
    ]
    
    for file_path in changed_files[:10]:  # 限制数量
        diff = get_file_diff(file_path)
        prompt_parts.append(f"### {file_path}")
        prompt_parts.append(f"```diff\n{diff[:500]}\n```")
        prompt_parts.append("")
    
    prompt_parts.extend([
        "## 受影响的文档",
        ", ".join(affected_docs) if affected_docs else "未检测到直接关联文档",
        "",
        "## 任务",
        "1. 分析代码变更的性质（新增功能/修复 bug/重构/文档更新等）",
        "2. 判断是否需要更新文档",
        "3. 如果需要，说明具体要更新哪些部分",
        "4. 给出简洁的提醒，格式：",
        "   - 📝 文档更新提醒：<具体说明>",
        "   - 或 ✅ 无需更新文档",
        "",
        "请用中文回复，保持简洁。",
    ])
    
    prompt = "\n".join(prompt_parts)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是文档同步审查助手，帮助开发者确保代码变更后文档及时更新。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content or "未获得有效回答"
    except Exception as e:
        return f"[错误] LLM 调用失败：{str(e)}"


def post_pr_comment(comment: str) -> None:
    """在 PR 中发布评论。"""
    pr_number = os.getenv("PR_NUMBER")
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    
    if not pr_number or not github_token or not repo:
        print("[跳过] 未检测到 PR 环境，跳过评论发布")
        return
    
    # 使用 GitHub CLI 或 API 发布评论
    try:
        import urllib.request
        import urllib.error
        
        url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
        data = json.dumps({"body": comment}).encode("utf-8")
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        
        with urllib.request.urlopen(req) as resp:
            print(f"[通过] PR 评论已发布 (status: {resp.status})")
    except Exception as e:
        print(f"[警告] 发布 PR 评论失败：{str(e)}")


def main():
    print("=" * 60)
    print("[AI] AI 文档同步审查")
    print("=" * 60)
    
    # 1. 获取变更文件
    changed_files = get_changed_files()
    if not changed_files:
        print("[跳过] 未检测到变更文件")
        sys.exit(0)
    
    print(f"变更文件: {len(changed_files)} 个")
    for f in changed_files[:5]:
        print(f"  - {f}")
    if len(changed_files) > 5:
        print(f"  ... 还有 {len(changed_files) - 5} 个文件")
    print()
    
    # 2. 推断受影响的文档
    affected_docs, arch_changed = infer_affected_docs(changed_files)
    
    print(f"受影响的文档: {len(affected_docs)} 个")
    for doc in affected_docs:
        print(f"  - {doc}")
    print()
    
    if arch_changed:
        print("⚠️  检测到架构相关文件变更，建议检查 ADR 是否需要更新")
        print()
    
    # 3. AI 分析
    print("[AI] 正在分析代码变更...")
    analysis = analyze_with_llm(changed_files, affected_docs)
    print()
    print(analysis)
    print()
    
    # 4. 构建 PR 评论
    comment_parts = [
        "## 🤖 AI 文档同步审查",
        "",
        "### 受影响的文档",
    ]
    
    if affected_docs:
        for doc in affected_docs:
            comment_parts.append(f"- `{doc}`")
    else:
        comment_parts.append("- 未检测到直接关联的文档")
    
    comment_parts.extend([
        "",
        "### AI 分析结果",
        "",
        analysis,
        "",
        "---",
        "",
        "💡 **提示**：如果文档需要更新，请在提交中包含文档变更，或在此 PR 中补充说明。",
    ])
    
    comment = "\n".join(comment_parts)
    
    # 5. 发布评论
    post_pr_comment(comment)
    
    print("=" * 60)
    print("[通过] AI 文档审查完成")
    sys.exit(0)


if __name__ == "__main__":
    main()
