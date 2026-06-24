"""
sync_checkpoint.py

用途：
  在任意文件实际变更后，立即执行本检查点，确认关联文档已同步更新。
  这是项目规则的硬性要求，违反视为未完成该轮任务。

检查项：
  1. 代码-文档映射检查：核心代码变更后，对应文档是否已更新
  2. 文档引用有效性检查：Markdown 链接是否有效
  3. ADR 触发检查：架构相关代码变更是否触发 ADR 更新

用法：
  # 手动指定变更文件
  python .github/skills/project-initializer/scripts/sync_checkpoint.py \
    --changed "agent_core/core/react_agent.py" \
    --changed "docs/reference/api.md"
  
  # 自动检测git变更文件（无需手动传参）
  python .github/skills/project-initializer/scripts/sync_checkpoint.py
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[4]
DOCS_DIR = WORKSPACE / "docs"
ADR_DIR = DOCS_DIR / "adr"

# 代码 -> 文档映射表
# 键：核心代码文件路径（相对于 WORKSPACE）
# 值：对应的文档路径列表（相对于 WORKSPACE）
CODE_TO_DOC_MAP = {
    # 核心 ReAct 引擎
    "agent_core/core/react_agent.py": [
        "docs/reference/api.md",
        "docs/report/ReAct智能体实现评估与改进路线图.md",
    ],
    "agent_core/core/tool_registry.py": [
        "docs/reference/api.md",
    ],
    # 配置
    "agent_core/config.py": [
        "docs/reference/configuration.md",
    ],
    # 多 Agent 层
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
    # 服务端
    "agent_core/server/server.py": [
        "docs/reference/api.md",
    ],
    # 前端适配层
    "agent_core/frontend/adapter.py": [
        "docs/reference/api.md",
    ],
    "agent_core/frontend/bus.py": [
        "docs/reference/api.md",
    ],
    "agent_core/frontend/events.py": [
        "docs/reference/api.md",
    ],
    # 配置文件
    "config/agents.yaml": [
        "docs/reference/configuration.md",
    ],
    "config/relationships.yaml": [
        "docs/reference/configuration.md",
    ],
}

# 架构决策相关文件模式
# 这些文件变更时，应检查是否需要更新 ADR
ARCHITECTURE_FILE_PATTERNS = [
    "agent_core/core/",
    "agent_core/multi_agent/",
    "agent_core/server/",
    "agent_core/frontend/",
    "config/agents.yaml",
    "config/relationships.yaml",
]

# 文档引用有效性检查：需要验证的链接模式
DOC_REFERENCE_PATTERNS = [
    r"\[.*?\]\((.*?)\)",  # Markdown 链接
    r"`([^`]*\.(py|md|yaml|yml|json|html|js|ts))`",  # 代码块中的文件引用
]

# 外部链接前缀，不检查存在性
EXTERNAL_LINK_PREFIXES = (
    "http://",
    "https://",
    "ftp://",
    "mailto:",
    "#",
)


def get_git_changed_files() -> list[Path]:
    """自动获取git工作区中变更的文件。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            check=True,
        )
        files = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                full_path = WORKSPACE / line.strip()
                if full_path.exists():
                    files.append(full_path.resolve())
        return files
    except Exception:
        return []


def resolve_doc_path(relative_path: str) -> Path | None:
    """将相对路径转换为绝对路径，如果存在则返回。"""
    if relative_path.startswith("./"):
        relative_path = relative_path[2:]
    if relative_path.startswith("/"):
        relative_path = relative_path[1:]
    doc_path = WORKSPACE / relative_path
    return doc_path if doc_path.exists() else None


def is_external_link(link: str) -> bool:
    """判断是否为外部链接。"""
    return any(link.startswith(prefix) for prefix in EXTERNAL_LINK_PREFIXES)


def check_code_doc_sync(changed_files: list[Path]) -> list[str]:
    """
    检查代码-文档映射：
    对于每个变更的核心代码文件，检查其对应的文档是否在合理时间内更新。
    """
    if not CODE_TO_DOC_MAP:
        return ["[跳过] 代码-文档映射表为空"]
    
    issues = []
    checked_mappings = 0
    
    for code_file in changed_files:
        rel_code = code_file.relative_to(WORKSPACE)
        rel_code_str = str(rel_code).replace("\\", "/")
        
        if rel_code_str not in CODE_TO_DOC_MAP:
            continue
        
        doc_paths = CODE_TO_DOC_MAP[rel_code_str]
        code_mtime = code_file.stat().st_mtime
        now = datetime.now().timestamp()
        
        for doc_rel in doc_paths:
            doc_path = WORKSPACE / doc_rel
            checked_mappings += 1
            
            if not doc_path.exists():
                issues.append(f"[错误] 代码 {rel_code} 已变更，但对应文档 {doc_rel} 不存在")
                continue
            
            doc_mtime = doc_path.stat().st_mtime
            time_diff = now - doc_mtime
            
            if code_mtime > doc_mtime and time_diff > 7 * 24 * 3600:
                issues.append(
                    f"[警告] 代码 {rel_code} 在 {datetime.fromtimestamp(code_mtime).strftime('%Y-%m-%d')} 变更，"
                    f"但文档 {doc_rel} 最后更新于 {datetime.fromtimestamp(doc_mtime).strftime('%Y-%m-%d')}，"
                    f"已超过 7 天未同步"
                )
    
    if checked_mappings == 0:
        return ["[跳过] 本次变更不涉及核心代码文件"]
    
    if not issues:
        return [f"[通过] 代码-文档同步检查通过 ({checked_mappings} 个映射)"]
    
    return issues


def check_document_references(changed_files: list[Path]) -> list[str]:
    """检查文档中的引用是否有效。"""
    issues = []
    
    md_files = [f for f in changed_files if f.suffix == ".md" and f.exists()]
    
    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = file_path.relative_to(WORKSPACE)
            
            for pattern in DOC_REFERENCE_PATTERNS:
                matches = re.findall(pattern, content)
                for match in matches:
                    if is_external_link(match):
                        continue
                    
                    ref_path = resolve_doc_path(match)
                    if ref_path is None:
                        issues.append(f"[警告] 无效引用: {rel_path} -> {match}")
        except Exception as e:
            issues.append(f"[错误] 读取文件失败: {file_path} ({e})")
    
    if not issues:
        return ["[通过] 文档引用检查通过"]
    return issues


def check_adr_trigger(changed_files: list[Path]) -> list[str]:
    """
    检查架构相关代码变更是否触发 ADR 更新。
    """
    arch_changed = False
    for code_file in changed_files:
        rel_code = str(code_file.relative_to(WORKSPACE)).replace("\\", "/")
        for pattern in ARCHITECTURE_FILE_PATTERNS:
            if rel_code.startswith(pattern):
                arch_changed = True
                break
        if arch_changed:
            break
    
    if not arch_changed:
        return ["[跳过] 本次变更不涉及架构相关文件"]
    
    if not ADR_DIR.exists():
        return ["[警告] 架构文件已变更，但 docs/adr/ 目录不存在"]
    
    now = datetime.now()
    recent_adr_count = 0
    
    for adr_file in ADR_DIR.glob("*.md"):
        if adr_file.stat().st_mtime > (now - timedelta(days=30)).timestamp():
            recent_adr_count += 1
    
    if recent_adr_count == 0:
        return [
            "[警告] 架构相关文件已变更，但最近 30 天内没有 ADR 更新",
            "        建议评估是否需要创建新的架构决策记录"
        ]
    
    return [f"[通过] 架构文件已变更，最近 30 天内有 {recent_adr_count} 个 ADR 更新"]


def main():
    parser = argparse.ArgumentParser(description="同步更新检查点")
    parser.add_argument("--changed", action="append", help="变更文件路径（可多次指定，不填则自动检测git变更）")
    args = parser.parse_args()
    
    if args.changed:
        changed_files = [Path(p).resolve() for p in args.changed]
    else:
        changed_files = get_git_changed_files()
        if not changed_files:
            print("[警告] 未检测到任何变更文件，可通过 --changed 参数手动指定")
            sys.exit(0)
    
    print("=" * 60)
    print("[同步] 同步更新检查点")
    print("=" * 60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"变更文件: {len(changed_files)} 个")
    for f in changed_files:
        print(f"  - {f.relative_to(WORKSPACE)}")
    print()
    
    all_issues = []
    
    print("[检查 1/3] 代码-文档映射同步")
    issues = check_code_doc_sync(changed_files)
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    print("[检查 2/3] 文档引用有效性")
    issues = check_document_references(changed_files)
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    print("[检查 3/3] ADR 触发检查")
    issues = check_adr_trigger(changed_files)
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    print("=" * 60)
    if all_issues:
        print(f"[错误] 检查失败：发现 {len(all_issues)} 个错误")
        for issue in all_issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("[通过] 所有检查通过，同步更新完整")
        sys.exit(0)


if __name__ == "__main__":
    main()
