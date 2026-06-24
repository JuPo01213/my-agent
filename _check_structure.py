from pathlib import Path
import os
p = Path("docs/structure.md")
print("mtime :", os.path.getmtime(p))
print("size  :", p.stat().st_size)
print("lines :", sum(1 for _ in p.open(encoding="utf-8")))
print("-" * 50)
content = p.read_text(encoding="utf-8")
for marker in ["outputs/", "tool-scenario", "2026-06-24-09", "ADR-008", "YAML 缺省 tools"]:
    print(f"  {marker!r:35s}  {'FOUND' if marker in content else 'MISSING'}")