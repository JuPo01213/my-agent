"""experiments/2026-06-24-scenario-kpi.py
从 log 反推 KPI（避免主脚本在打印长报告后被截断 KPI 段的问题）"""
import re
from pathlib import Path

LOG = Path(__file__).resolve().parent / "2026-06-24-scenario.log"
txt = LOG.read_text(encoding="utf-8")

# history
hist = []
for m in re.finditer(r"step=\s*(\d+)\s+source=\S+\s+key=(result::\w+)", txt):
    hist.append((int(m.group(1)), m.group(2)))

# facts 字数
facts = dict(re.findall(r"-\s+(result::\w+):\s+共\s+(\d+)\s+字", txt))

# elapsed & status
m = re.search(r"elapsed\s+:\s+([\d.]+)s", txt)
elapsed = m.group(1) if m else "N/A"
m = re.search(r"status\s+:\s*(\w+)", txt)
status = m.group(1) if m else "N/A"

# 提取每步耗时
steps_cost = {}
for m in re.finditer(r"\[(\w+)\] 完成\s+cost=([\d.]+)s", txt):
    steps_cost[m.group(1)] = float(m.group(2))

print(f"history        : {hist}")
print(f"facts 字数     : {facts}")
print(f"elapsed        : {elapsed}s")
print(f"status         : {status}")
print(f"每步耗时       : {steps_cost}")
print(f"总 OODA 耗时   : {sum(steps_cost.values()):.2f}s")
print()
print("=" * 50)
print("KPI 校验（从 log 反推）")
print("=" * 50)

key_order = [h[1] for h in hist]
writer_chars = int(facts.get("result::writer", 0))
checks = [
    (f"status == solved  (实际: {status})", status == "solved"),
    ("facts 含 result::advisor", "result::advisor" in facts),
    ("facts 含 result::strategist", "result::strategist" in facts),
    ("facts 含 result::writer", "result::writer" in facts),
    (
        "顺序 advisor → strategist → writer",
        key_order == ["result::advisor", "result::strategist", "result::writer"],
    ),
    (
        f"writer 报告 > 500 字  (实际: {writer_chars} 字)",
        writer_chars > 500,
    ),
    (
        f"writer 报告 > 5000 字  (实际: {writer_chars} 字)",
        writer_chars > 5000,
    ),
    (
        f"3 段产出总计 > 15000 字  (实际: {sum(int(v) for v in facts.values())} 字)",
        sum(int(v) for v in facts.values()) > 15000,
    ),
]
all_ok = True
for name, ok in checks:
    flag = "OK  " if ok else "FAIL"
    if not ok:
        all_ok = False
    print(f"  [{flag}] {name}")
print()
print("ALL OK" if all_ok else "SOME FAILED")
