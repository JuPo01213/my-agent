# ADR-017: 后续方向 E — 单元测试 + CI 接入

- **日期**：2026-06-24
- **状态**：已采纳

## 背景

当前 8 个 risk-point 测试手测过（`python -m unittest discover -s tests` 0.002s OK），但没接 CI，改 relationship.py 容易偷偷回归。

## 决策

- **测试**：保持 risk-point 风格（不追求覆盖率），按 ADR-012 三问法评估
- **CI**：新增 `.github/workflows/test.yml`，仅在 push/PR 时跑 `python -m unittest discover -s tests`
- **触发条件**：relationship.py / run_loop.py / _parse_precondition 等核心文件变更

## 后果

核心层有最低回归保障；保持"测试是手段不是目的"的工程原则。
