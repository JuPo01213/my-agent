"""
docs_sync/engine.py - 文档同步检查引擎

设计原则：
  1. 模型驱动：所有规则来自 docs_sync/config.yaml，不硬编码
  2. 结构感知：自动发现新增/删除/移动，不依赖固定映射表
  3. 分层检查：结构变更 -> 代码-文档同步 -> 引用有效性 -> ADR 触发
  4. 可扩展：新增检查类型只需实现 Check 接口并注册

用法：
  # 自动检测 git 变更
  python docs_sync/engine.py

  # 指定变更文件
  python docs_sync/engine.py --changed agent_core/core/react_agent.py

  # 仅检查结构变更
  python docs_sync/engine.py --check structure
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


# ============================================================
# 数据模型
# ============================================================

@dataclass
class DocObligation:
    """单个文档义务：某个代码单元必须维护的文档。"""
    doc_path: str
    required: bool = True


@dataclass
class DirectoryRule:
    """目录规则：定义某个目录的职责和文档义务。"""
    path: str
    role: str
    description: str
    doc_obligations: list[str] = field(default_factory=list)
    adr_required: bool = False


@dataclass
class FileRule:
    """单文件特殊规则。"""
    path: str
    role: str
    description: str
    doc_obligations: list[str] = field(default_factory=list)
    adr_required: bool = False


@dataclass
class Policies:
    """检查策略配置。"""
    code_doc_sync: dict[str, Any] = field(default_factory=dict)
    reference_check: dict[str, Any] = field(default_factory=dict)
    adr_trigger: dict[str, Any] = field(default_factory=dict)
    structure_change: dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncConfig:
    """同步配置顶层模型。"""
    version: str
    structure: dict[str, Any]
    policies: dict[str, Any]
    site: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    """单条检查结果。"""
    check_name: str
    severity: str  # error / warning / info
    message: str
    file: str | None = None
    suggestion: str | None = None


# ============================================================
# 配置加载
# ============================================================

def load_config(config_path: Path) -> SyncConfig:
    """加载 docs_sync/config.yaml。"""
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return SyncConfig(
        version=raw.get("version", "1.0"),
        structure=raw.get("structure", {}),
        policies=raw.get("policies", {}),
        site=raw.get("site", {}),
    )


# ============================================================
# 结构扫描器
# ============================================================

class StructureScanner:
    """扫描实际项目结构，返回目录树和文件清单。"""

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def scan_directories(self) -> set[str]:
        """扫描所有一级子目录。"""
        dirs = set()
        for p in self.workspace.iterdir():
            if p.is_dir() and not p.name.startswith(".") and p.name not in {"__pycache__"}:
                dirs.add(p.name)
        return dirs

    def scan_files(self, relative_to: Path | None = None) -> set[str]:
        """扫描所有文件（相对路径）。"""
        base = relative_to or self.workspace
        files = set()
        for p in base.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                rel = p.relative_to(self.workspace)
                files.add(str(rel).replace("\\", "/"))
        return files

    def scan_directory_tree(self, dir_path: str) -> set[str]:
        """扫描指定目录下的所有文件。"""
        full_path = self.workspace / dir_path
        if not full_path.exists():
            return set()
        return self.scan_files(full_path)


# ============================================================
# 检查器接口
# ============================================================

class Check:
    """检查器基类。"""
    name: str = "base"
    severity: str = "info"

    def run(self, ctx: "CheckContext") -> list[CheckResult]:
        raise NotImplementedError


class CheckContext:
    """检查上下文：所有检查器共享的状态。"""
    def __init__(
        self,
        workspace: Path,
        config: SyncConfig,
        changed_files: list[Path],
        scanner: StructureScanner,
    ):
        self.workspace = workspace
        self.config = config
        self.changed_files = changed_files
        self.scanner = scanner
        self.results: list[CheckResult] = []

    def add_result(self, result: CheckResult) -> None:
        self.results.append(result)


# ============================================================
# 检查器 1：结构变更检测
# ============================================================

class StructureChangeCheck(Check):
    """检测项目结构变化：新增/删除/移动文件或目录。"""

    name = "structure_change"
    severity = "error"

    def run(self, ctx: CheckContext) -> list[CheckResult]:
        results: list[CheckResult] = []
        config = ctx.config
        scanner = ctx.scanner
        workspace = ctx.workspace

        # 1. 检查配置中定义的目录是否还存在
        for dir_rule in config.structure.get("directories", []):
            dir_path = workspace / dir_rule["path"]
            if not dir_path.exists():
                results.append(CheckResult(
                    check_name=self.name,
                    severity=self.severity,
                    message=f"目录缺失：{dir_rule['path']}（角色：{dir_rule.get('role', 'unknown')}）",
                    file=dir_rule["path"],
                    suggestion="恢复目录或更新 docs_sync/config.yaml",
                ))

        # 2. 检查配置中定义的文件是否还存在
        for file_rule in config.structure.get("files", []):
            file_path = workspace / file_rule["path"]
            if not file_path.exists():
                results.append(CheckResult(
                    check_name=self.name,
                    severity=self.severity,
                    message=f"文件缺失：{file_rule['path']}（角色：{file_rule.get('role', 'unknown')}）",
                    file=file_rule["path"],
                    suggestion="恢复文件或更新 docs_sync/config.yaml",
                ))

        # 3. 扫描实际存在的核心文件，检查是否在配置中
        configured_paths = set()
        for dir_rule in config.structure.get("directories", []):
            configured_paths.add(dir_rule["path"])
        for file_rule in config.structure.get("files", []):
            configured_paths.add(file_rule["path"])

        # 检查 agent_core/ 下的子目录
        agent_core_dirs = scanner.scan_directories()
        for dir_name in agent_core_dirs:
            full_dir = f"agent_core/{dir_name}"
            if full_dir not in configured_paths and not full_dir.startswith("."):
                # 新目录，检查是否有 Python 文件
                py_files = [f for f in scanner.scan_directory_tree(full_dir) if f.endswith(".py")]
                if py_files:
                    results.append(CheckResult(
                        check_name=self.name,
                        severity=self.severity,
                        message=f"发现未配置的目录：{full_dir}，包含 {len(py_files)} 个 Python 文件",
                        file=full_dir,
                        suggestion="在 docs_sync/config.yaml 的 structure.directories 中添加该目录规则",
                    ))

        # 4. 检查变更文件中是否有未映射的（仅检查代码/配置文件，不检查文档）
        code_like_suffixes = {".py", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}
        for changed_file in ctx.changed_files:
            rel = str(changed_file.relative_to(workspace)).replace("\\", "/")
            # 跳过文档文件本身
            if rel.startswith("docs/") or rel.startswith("research/"):
                continue
            # 只检查代码/配置文件
            if changed_file.suffix.lower() not in code_like_suffixes:
                continue
            if self._is_unmapped(rel, config):
                results.append(CheckResult(
                    check_name=self.name,
                    severity=self.severity,
                    message=f"变更文件未在配置中映射：{rel}",
                    file=rel,
                    suggestion="在 docs_sync/config.yaml 中添加该文件的映射规则",
                ))

        return results

    def _is_unmapped(self, rel_path: str, config: SyncConfig) -> bool:
        """判断文件是否未在配置中映射。"""
        # 检查是否在某个目录规则下
        for dir_rule in config.structure.get("directories", []):
            if rel_path.startswith(dir_rule["path"] + "/"):
                return False
        # 检查是否是单文件规则
        for file_rule in config.structure.get("files", []):
            if rel_path == file_rule["path"]:
                return False
        return True


# ============================================================
# 检查器 2：代码-文档同步
# ============================================================

class CodeDocSyncCheck(Check):
    """检查代码变更后，对应文档是否在合理时间内更新。"""

    name = "code_doc_sync"
    severity = "warning"

    def run(self, ctx: CheckContext) -> list[CheckResult]:
        results: list[CheckResult] = []
        policies = ctx.config.policies.get("code_doc_sync", {})
        if not policies.get("enabled", True):
            return results

        threshold_days = policies.get("threshold_days", 7)
        threshold_seconds = threshold_days * 24 * 3600
        now = datetime.now().timestamp()

        # 构建路径 -> 文档义务的映射
        path_to_docs = self._build_path_doc_map(ctx.config)

        for changed_file in ctx.changed_files:
            rel = str(changed_file.relative_to(ctx.workspace)).replace("\\", "/")
            doc_obligations = self._find_obligations(rel, path_to_docs)

            if not doc_obligations:
                continue

            code_mtime = changed_file.stat().st_mtime

            for doc_rel in doc_obligations:
                doc_path = ctx.workspace / doc_rel
                if not doc_path.exists():
                    results.append(CheckResult(
                        check_name=self.name,
                        severity="error",
                        message=f"代码 {rel} 已变更，但对应文档 {doc_rel} 不存在",
                        file=rel,
                        suggestion=f"创建文档 {doc_rel}",
                    ))
                    continue

                doc_mtime = doc_path.stat().st_mtime
                if code_mtime > doc_mtime and (now - doc_mtime) > threshold_seconds:
                    results.append(CheckResult(
                        check_name=self.name,
                        severity=self.severity,
                        message=(
                            f"代码 {rel} 在 {datetime.fromtimestamp(code_mtime).strftime('%Y-%m-%d')} 变更，"
                            f"但文档 {doc_rel} 最后更新于 {datetime.fromtimestamp(doc_mtime).strftime('%Y-%m-%d')}，"
                            f"已超过 {threshold_days} 天未同步"
                        ),
                        file=rel,
                        suggestion=f"更新文档 {doc_rel}",
                    ))

        return results

    def _build_path_doc_map(self, config: SyncConfig) -> dict[str, list[str]]:
        """从配置构建路径 -> 文档义务映射。"""
        path_map: dict[str, list[str]] = {}

        for dir_rule in config.structure.get("directories", []):
            path_map[dir_rule["path"]] = dir_rule.get("doc_obligations", [])

        for file_rule in config.structure.get("files", []):
            path_map[file_rule["path"]] = file_rule.get("doc_obligations", [])

        return path_map

    def _find_obligations(self, rel_path: str, path_map: dict[str, list[str]]) -> list[str]:
        """查找文件对应的文档义务。"""
        # 精确匹配
        if rel_path in path_map:
            return path_map[rel_path]

        # 目录前缀匹配
        for prefix, docs in path_map.items():
            if rel_path.startswith(prefix + "/"):
                return docs

        return []


# ============================================================
# 检查器 3：文档引用有效性
# ============================================================

class ReferenceCheck(Check):
    """检查 Markdown 文档中的链接是否有效。"""

    name = "reference_check"
    severity = "warning"

    # 默认外部链接前缀
    DEFAULT_EXTERNAL_PREFIXES = (
        "http://",
        "https://",
        "ftp://",
        "mailto:",
        "#",
    )

    def run(self, ctx: CheckContext) -> list[CheckResult]:
        results: list[CheckResult] = []
        policies = ctx.config.policies.get("reference_check", {})
        if not policies.get("enabled", True):
            return results

        external_prefixes = tuple(policies.get("external_link_prefixes", self.DEFAULT_EXTERNAL_PREFIXES))
        patterns = [
            r"\[.*?\]\((.*?)\)",  # Markdown 链接
            r"`([^`]*\.(py|md|yaml|yml|json|html|js|ts))`",  # 代码块文件引用
        ]

        # 只检查变更的 Markdown 文件
        md_files = [f for f in ctx.changed_files if f.suffix == ".md" and f.exists()]

        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                rel_path = file_path.relative_to(ctx.workspace)

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if self._is_external(match, external_prefixes):
                            continue

                        ref_path = self._resolve(match, file_path, ctx.workspace)
                        if ref_path is None or not ref_path.exists():
                            results.append(CheckResult(
                                check_name=self.name,
                                severity=self.severity,
                                message=f"无效引用：{rel_path} -> {match}",
                                file=str(rel_path),
                                suggestion=f"修复链接或确认文件 {match} 已删除",
                            ))
            except Exception as e:
                results.append(CheckResult(
                    check_name=self.name,
                    severity="error",
                    message=f"读取文件失败：{file_path} ({e})",
                    file=str(file_path.relative_to(ctx.workspace)),
                ))

        return results

    def _is_external(self, link: str, prefixes: tuple[str, ...]) -> bool:
        return any(link.startswith(p) for p in prefixes)

    def _resolve(self, link: str, base: Path, workspace: Path) -> Path | None:
        if link.startswith("./"):
            link = link[2:]
        if link.startswith("/"):
            link = link[1:]
        candidate = workspace / link
        return candidate if candidate.exists() else None


# ============================================================
# 检查器 4：ADR 触发
# ============================================================

class AdrTriggerCheck(Check):
    """架构相关代码变更后，检查是否在窗口期内有 ADR 更新。"""

    name = "adr_trigger"
    severity = "warning"

    def run(self, ctx: CheckContext) -> list[CheckResult]:
        results: list[CheckResult] = []
        policies = ctx.config.policies.get("adr_trigger", {})
        if not policies.get("enabled", True):
            return results

        window_days = policies.get("window_days", 30)
        adr_dir = ctx.workspace / "docs" / "adr"

        # 检查变更是否涉及架构相关路径
        arch_patterns = []
        for dir_rule in ctx.config.structure.get("directories", []):
            if dir_rule.get("adr_required", False):
                arch_patterns.append(dir_rule["path"] + "/")
        for file_rule in ctx.config.structure.get("files", []):
            if file_rule.get("adr_required", False):
                arch_patterns.append(file_rule["path"])

        arch_changed = any(
            str(f.relative_to(ctx.workspace)).replace("\\", "/").startswith(tuple(arch_patterns))
            for f in ctx.changed_files
        )

        if not arch_changed:
            return results

        if not adr_dir.exists():
            results.append(CheckResult(
                check_name=self.name,
                severity="warning",
                message="架构文件已变更，但 docs/adr/ 目录不存在",
                suggestion="创建 docs/adr/ 目录并记录架构决策",
            ))
            return results

        # 检查窗口期内是否有 ADR 更新
        now = datetime.now()
        recent_count = sum(
            1 for f in adr_dir.glob("*.md")
            if f.stat().st_mtime > (now - timedelta(days=window_days)).timestamp()
        )

        if recent_count == 0:
            results.append(CheckResult(
                check_name=self.name,
                severity=self.severity,
                message=f"架构相关文件已变更，但最近 {window_days} 天内没有 ADR 更新",
                suggestion="评估是否需要创建新的架构决策记录",
            ))
        else:
            results.append(CheckResult(
                check_name=self.name,
                severity="info",
                message=f"架构文件已变更，最近 {window_days} 天内有 {recent_count} 个 ADR 更新",
            ))

        return results


# ============================================================
# 引擎
# ============================================================

class DocsSyncEngine:
    """文档同步检查引擎。"""

    def __init__(self, config_path: Path | None = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        self.config = load_config(config_path)
        self.workspace = Path(__file__).resolve().parents[1]
        self.scanner = StructureScanner(self.workspace)

        # 注册检查器
        self.checks: list[Check] = [
            StructureChangeCheck(),
            CodeDocSyncCheck(),
            ReferenceCheck(),
            AdrTriggerCheck(),
        ]

    def get_git_changed_files(self) -> list[Path]:
        """自动获取 git 工作区变更文件。"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMR"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                check=True,
            )
            files = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    full_path = self.workspace / line.strip()
                    if full_path.exists():
                        files.append(full_path.resolve())
            return files
        except Exception:
            return []

    def run(self, changed_files: list[Path] | None = None, check_names: list[str] | None = None) -> int:
        """
        运行检查。

        Args:
            changed_files: 变更文件列表，None 则自动检测
            check_names: 指定运行的检查器名称，None 则运行全部

        Returns:
            0: 通过
            1: 有错误
            2: 有警告但无错误
        """
        if changed_files is None:
            changed_files = self.get_git_changed_files()

        ctx = CheckContext(
            workspace=self.workspace,
            config=self.config,
            changed_files=changed_files,
            scanner=self.scanner,
        )

        # 运行检查器
        for check in self.checks:
            if check_names and check.name not in check_names:
                continue
            results = check.run(ctx)
            ctx.results.extend(results)

        # 输出结果
        self._print_results(ctx.results)

        # 判断退出码
        has_error = any(r.severity == "error" for r in ctx.results)
        has_warning = any(r.severity == "warning" for r in ctx.results)

        if has_error:
            return 1
        if has_warning:
            return 2
        return 0

    def _print_results(self, results: list[CheckResult]) -> None:
        """格式化输出检查结果。"""
        print("=" * 60)
        print("[docs_sync] 文档同步检查引擎")
        print("=" * 60)
        print(f"配置版本: {self.config.version}")
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"检查项数: {len(results)}")
        print()

        # 按严重程度分组
        errors = [r for r in results if r.severity == "error"]
        warnings = [r for r in results if r.severity == "warning"]
        infos = [r for r in results if r.severity == "info"]

        if errors:
            print(f"[错误] {len(errors)} 个错误：")
            for r in errors:
                print(f"  ❌ {r.check_name}: {r.message}")
                if r.file:
                    print(f"     文件: {r.file}")
                if r.suggestion:
                    print(f"     建议: {r.suggestion}")
            print()

        if warnings:
            print(f"[警告] {len(warnings)} 个警告：")
            for r in warnings:
                print(f"  ⚠️  {r.check_name}: {r.message}")
                if r.file:
                    print(f"     文件: {r.file}")
                if r.suggestion:
                    print(f"     建议: {r.suggestion}")
            print()

        if infos:
            print(f"[信息] {len(infos)} 个提示：")
            for r in infos:
                print(f"  ℹ️  {r.check_name}: {r.message}")
            print()

        print("=" * 60)
        if errors:
            print(f"[失败] 发现 {len(errors)} 个错误，文档同步检查未通过")
        elif warnings:
            print(f"[警告] 发现 {len(warnings)} 个警告，建议修复")
        else:
            print("[通过] 所有检查通过，文档同步完整")


# ============================================================
# CLI 入口
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="docs_sync 文档同步检查引擎")
    parser.add_argument("--changed", action="append", help="变更文件路径（可多次指定）")
    parser.add_argument(
        "--check",
        action="append",
        choices=["structure", "code_doc_sync", "reference_check", "adr_trigger"],
        help="指定运行的检查器",
    )
    args = parser.parse_args()

    engine = DocsSyncEngine()

    changed_files = None
    if args.changed:
        changed_files = [Path(p).resolve() for p in args.changed]

    return engine.run(changed_files=changed_files, check_names=args.check)


if __name__ == "__main__":
    sys.exit(main())
