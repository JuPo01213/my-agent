"""
experiments/2026-06-24-relationship-real-kpi.py
================================================

目的：在第一次完整运行（experiments/2026-06-24-relationship-real.py）的 log
基础上，用 key 字段而非 source 字段做顺序校验。说明：
- Blackboard.update() 的 source 参数在 _apply_command 里被硬编码为 "command"
- history 里识别"哪个 agent 写的"应当看 key（result::<agent_name>）
"""
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG = PROJECT_ROOT / "experiments" / "2026-06-24-relationship-real.log"

txt = LOG.read_text(encoding="utf-8")

# 从 log 抓 history 段
m = re.search(r"history \(op/source/key\):\n(.*?)\n\n====", txt, re.S)
if not m:
    print("[FATAL] 未找到 history 段")
    sys.exit(2)
seg = m.group(1)

# 抓每行 "step=N  command  ->  result::<name>"
key_order = []
for line in seg.splitlines():
    mm = re.search(r"->\s+(result::\w+)", line)
    if mm:
        key_order.append(mm.group(1))

print(f"key_order = {key_order}")

# 走读文档的预期：researcher 在 analyst 之前，analyst 在 writer 之前
expected = ["result::researcher", "result::analyst", "result::writer"]
checks = [
    ("result::researcher 在 result::analyst 之前",
        key_order.index("result::researcher") < key_order.index("result::analyst")),
    ("result::analyst 在 result::writer 之前",
        key_order.index("result::analyst") < key_order.index("result::writer")),
    ("总顺序与走读文档一致",
        key_order == expected),
]
all_ok = True
for name, ok in checks:
    flag = "OK  " if ok else "FAIL"
    if not ok:
        all_ok = False
    print(f"  [{flag}] {name}")
print()
print("ALL OK" if all_ok else "SOME FAILED")
sys.exit(0 if all_ok else 1)
