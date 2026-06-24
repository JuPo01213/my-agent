"""
run_log.py - 跑一个 Python 脚本并把 stdout/stderr 强制以 UTF-8 写入指定日志文件
=============================================================================

用途：绕过 PowerShell 5.1 的 GBK / UTF-16 默认行为，确保 .log 永远是 UTF-8。

用法：
  python run_log.py <log_path> <script_path> [args...]

示例：
  python run_log.py experiments/2026-06-24-walkthrough-v2.log experiments/2026-06-24-scenario.py

实现：
  1. 用 Python 重新执行目标脚本
  2. 子进程 stdout/stderr 全部以 utf-8 解码
  3. 在 Python 内 write 到目标文件，open(..., encoding="utf-8")
  4. 同时把内容原样打到父进程 stdout，便于实时观察
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("用法: python run_log.py <log_path> <script_path> [args...]", file=sys.stderr)
        return 2

    log_path = Path(sys.argv[1])
    script_path = Path(sys.argv[2])
    extra_args = sys.argv[3:]

    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 子进程以 utf-8 通信，避免父进程解码失败
    result = subprocess.run(
        [sys.executable, str(script_path), *extra_args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
    )

    output = result.stdout or ""

    # 1) 写到目标文件，强制 utf-8（无 BOM）
    log_path.write_text(output, encoding="utf-8")

    # 2) 实时打到父进程 stdout（终端显示）
    sys.stdout.write(output)
    sys.stdout.flush()

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
