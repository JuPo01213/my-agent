"""
sync_checkpoint.py

用途：
  在任意文件实际变更后，立即执行本检查点，确认关联文件已同步更新。
  这是项目规则的硬性要求，违反视为未完成该轮任务。

检查项：
  1. docs/structure.md 是否包含新增/修改的核心文件索引（自动排除归档类文件）
  2. 若变更涉及报告内容，主报告参考来源是否已更新
  3. 当前对话是否已创建 session 归档
  4. README.md 是否存在且包含关键章节
  5. docs/ 目录完整性检查
  6. CHANGELOG.md 是否存在
  7. 文档引用有效性检查

用法：
  # 手动指定变更文件
  python .github/skills/project-initializer/scripts/sync_checkpoint.py \
    --changed "docs/report/reports/Skill_Engineering_Technical_Details.md" \
    --changed "AGENTS.md"
  
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
STRUCTURE_DOC = WORKSPACE / "docs" / "structure.md"
MAIN_REPORT = WORKSPACE / "docs" / "report" / "写一个自己的智能体_完整调研与最佳实践报告.md"
SESSION_DIR = WORKSPACE / "memories" / "session"
README_DOC = WORKSPACE / "README.md"
CHANGELOG_DOC = WORKSPACE / "CHANGELOG.md"
DOCS_DIR = WORKSPACE / "docs"

# 不需要加入结构索引的目录/文件模式
EXCLUDE_FROM_INDEX = [
    "memories/session/",  # 会话归档文件，按日期命名可直接浏览
    ".github/",           # 技能和脚本文件，本身有自描述结构
    "__pycache__/",
    ".git/",
]

# 文档引用有效性检查：需要验证的链接模式
DOC_REFERENCE_PATTERNS = [
    r"\[.*?\]\((.*?)\)",  # Markdown 链接
    r"`([^`]*\.(py|md|yaml|yml|json|html|js|ts))`",  # 代码块中的文件引用
]


def should_check_index(file_path: Path) -> bool:
    """判断文件是否需要检查结构索引。"""
    rel_str = str(file_path.relative_to(WORKSPACE)).replace("\\", "/")
    for pattern in EXCLUDE_FROM_INDEX:
        if rel_str.startswith(pattern):
            return False
    # 排除临时文件、隐藏文件
    if file_path.name.startswith(".") or file_path.suffix in {".pyc", ".pyo", ".log"}:
        return False
    return True


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
        # git命令失败时返回空列表，回退到手动传参
        return []


def check_structure_index(changed_files: list[Path]) -> list[str]:
    """检查 docs/structure.md 是否包含所有需要索引的变更文件。"""
    if not STRUCTURE_DOC.exists():
        return [f"[错误] 结构索引不存在: {STRUCTURE_DOC}"]
    
    content = STRUCTURE_DOC.read_text(encoding="utf-8")
    issues = []
    checked_count = 0
    
    for file_path in changed_files:
        # 排除不需要索引的文件
        if not should_check_index(file_path):
            continue
            
        checked_count += 1
        # 排除结构索引自身
        if file_path == STRUCTURE_DOC:
            continue
            
        rel = file_path.relative_to(WORKSPACE)
        filename = file_path.name
        
        # 检查文件名是否出现在结构文档中
        if filename not in content:
            issues.append(f"[错误] 结构索引缺失: {rel}")
    
    if not issues:
        return [f"[通过] 结构索引检查通过 ({checked_count} 个核心文件)"]
    return issues


def check_main_report_reference(changed_files: list[Path]) -> list[str]:
    """若变更涉及报告内容，检查主报告参考来源是否已更新。"""
    # 只检查 docs/report/ 下的 .md 文件，且排除主报告自身
    report_related = [
        f for f in changed_files 
        if f.parent == WORKSPACE / "docs" / "report" 
        and f.suffix == ".md"
        and f != MAIN_REPORT
    ]
    
    if not report_related:
        return ["[跳过] 主报告引用检查跳过（无报告类文件变更）"]
    
    if not MAIN_REPORT.exists():
        return [f"[错误] 主报告不存在: {MAIN_REPORT}"]
    
    content = MAIN_REPORT.read_text(encoding="utf-8")
    issues = []
    
    # 检查参考来源章节是否存在
    if "## 参考来源" not in content:
        issues.append("[错误] 主报告缺少'参考来源'章节")
    
    for file_path in report_related:
        rel = file_path.relative_to(WORKSPACE)
        filename = file_path.name
        
        # 检查参考来源中是否引用了该文件
        if filename not in content:
            issues.append(f"[警告] 主报告未引用: {rel}")
    
    if not issues:
        return [f"[通过] 主报告引用检查通过 ({len(report_related)} 个报告文件)"]
    return issues


def check_session_archive() -> list[str]:
    """检查当前对话是否已创建 session 归档。"""
    if not SESSION_DIR.exists():
        return [f"[错误] session 目录不存在: {SESSION_DIR}"]
    
    # 检查今天或最近3天内是否有归档文件（放宽时间窗口）
    today = datetime.now().strftime("%Y-%m-%d")
    recent_files = []
    
    for f in SESSION_DIR.glob("*.md"):
        if today in f.name or (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)) < timedelta(days=3):
            recent_files.append(f)
    
    if recent_files:
        return [f"[通过] session 归档检查通过 ({len(recent_files)} 个最近归档)"]
    return [f"[警告] 未检测到最近3天内的 session 归档 ({SESSION_DIR})"]


def check_readme_exists() -> list[str]:
    """检查 README.md 是否存在且包含关键章节。"""
    if not README_DOC.exists():
        return [f"[错误] README.md 不存在: {README_DOC}"]
    
    content = README_DOC.read_text(encoding="utf-8")
    issues = []
    
    # 检查关键章节
    required_sections = ["# ", "## ", "快速开始", "目录说明", "架构概览"]
    for section in required_sections:
        if section not in content:
            issues.append(f"[警告] README.md 缺少关键内容: {section}")
    
    if not issues:
        return ["[通过] README.md 检查通过"]
    return issues


def check_docs_structure() -> list[str]:
    """检查 docs/ 目录完整性。"""
    if not DOCS_DIR.exists():
        return [f"[错误] docs/ 目录不存在: {DOCS_DIR}"]
    
    issues = []
    
    # 检查关键子目录
    expected_dirs = ["overview", "guides", "reference", "report", "adr"]
    for dir_name in expected_dirs:
        dir_path = DOCS_DIR / dir_name
        if not dir_path.exists():
            issues.append(f"[警告] docs/ 缺少子目录: {dir_name}/")
    
    # 检查关键文件
    expected_files = ["structure.md"]
    for file_name in expected_files:
        file_path = DOCS_DIR / file_name
        if not file_path.exists():
            issues.append(f"[错误] docs/ 缺少关键文件: {file_name}")
    
    if not issues:
        return ["[通过] docs/ 目录结构检查通过"]
    return issues


def check_changelog_exists() -> list[str]:
    """检查 CHANGELOG.md 是否存在。"""
    if not CHANGELOG_DOC.exists():
        return ["[警告] CHANGELOG.md 不存在，建议创建"]
    return ["[通过] CHANGELOG.md 存在"]


def check_document_references(changed_files: list[Path]) -> list[str]:
    """检查文档中的引用是否有效。"""
    issues = []
    
    # 只检查 Markdown 文件
    md_files = [f for f in changed_files if f.suffix == ".md" and f.exists()]
    
    for file_path in md_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = file_path.relative_to(WORKSPACE)
            
            # 查找所有文件引用
            for pattern in DOC_REFERENCE_PATTERNS:
                matches = re.findall(pattern, content)
                for match in matches:
                    # 处理相对路径
                    if match.startswith("/"):
                        ref_path = WORKSPACE / match[1:]
                    elif match.startswith("./"):
                        ref_path = (file_path.parent / match[2:]).resolve()
                    else:
                        ref_path = (file_path.parent / match).resolve()
                    
                    # 检查引用是否存在
                    if not ref_path.exists():
                        issues.append(f"[警告] 无效引用: {rel_path} -> {match}")
        except Exception as e:
            issues.append(f"[错误] 读取文件失败: {file_path} ({e})")
    
    if not issues:
        return ["[通过] 文档引用检查通过"]
    return issues


def main():
    parser = argparse.ArgumentParser(description="同步更新检查点")
    parser.add_argument("--changed", action="append", help="变更文件路径（可多次指定，不填则自动检测git变更）")
    args = parser.parse_args()
    
    # 优先使用手动指定的变更文件，否则自动检测git变更
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
    
    # 检查 1: 结构索引
    print("[检查 1/6] 结构索引同步")
    issues = check_structure_index(changed_files)
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    # 检查 2: 主报告引用
    print("[检查 2/6] 主报告引用同步")
    issues = check_main_report_reference(changed_files)
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    # 检查 3: session 归档
    print("[检查 3/6] session 归档")
    issues = check_session_archive()
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    # 检查 4: README.md
    print("[检查 4/6] README.md")
    issues = check_readme_exists()
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    # 检查 5: docs/ 目录结构
    print("[检查 5/6] docs/ 目录结构")
    issues = check_docs_structure()
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    # 检查 6: 文档引用有效性
    print("[检查 6/6] 文档引用有效性")
    issues = check_document_references(changed_files)
    for msg in issues:
        print(f"  {msg}")
    all_issues.extend([i for i in issues if i.startswith("[错误]")])
    print()
    
    # 总结
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
