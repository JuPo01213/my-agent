"""
test_parse_precondition - _parse_precondition 风险点守护

设计原则（参见 ADR-012）：
- 表驱动，每个测试一个真实风险点
- 不为"测 Python 函数"而存在
- 每个测试都该回答"哪个未来改动会因这个失败被打回"

守护的真风险：
1. 未知表达式必须默认放行（不能崩、不能错判为 False）
2. 三+ key 的 and 表达式必须真"全部满足"（防止 _extract_str 吃第一个 key）
3. 格式异常的引号不能崩（不能 eval / 不能注入）
4. snapshot 字段缺失不能崩（防御性 .get）
"""
from __future__ import annotations

import unittest

from agent_core.multi_agent.relationship import _parse_precondition


# 表驱动：每行 = (表达式, snapshot, 期望结果, 守护的风险)
_CASES = [
    # --- 风险 1：未知表达式默认放行（不能崩、不能 False）---
    (
        "import os; os.system('rm -rf /')",
        {},
        True,
        "未知表达式不能执行任意代码，必须默认放行（参见 docstring）",
    ),
    (
        "facts.has(missing_quotes)",  # 缺引号
        {},
        True,
        "缺引号的 malformed 表达式不能崩",
    ),
    # --- 风险 2：三+ key and 必须真"全部满足"（防 _extract_str 误吃第一个 key）---
    (
        "facts.has('a') and facts.has('b') and facts.has('c')",
        {"facts": {"a": 1}},  # 只 a 存在
        False,
        "三 key and 表达式不能退化为'任一满足'（曾 bug，ADR-009 修复）",
    ),
    (
        "facts.has('a') and facts.has('b') and facts.has('c')",
        {"facts": {"a": 1, "b": 2, "c": 3}},
        True,
        "三 key and 表达式全满足时必须返回 True（ADR-009 修复正确性）",
    ),
    # --- 风险 3：snapshot 缺字段不崩（防御性 .get）---
    (
        "facts.has('x')",
        {},  # 没有 'facts' key
        False,
        "snapshot 缺 'facts' 字段不能崩（容错）",
    ),
    (
        "'q1' in open_questions",
        {},  # 没有 'open_questions' key
        False,
        "snapshot 缺 'open_questions' 字段不能崩（容错）",
    ),
]


class TestParsePreconditionRiskPoints(unittest.TestCase):
    """表驱动：每个测试一个真风险点"""

    def test_risk_table(self):
        """覆盖 _parse_precondition 的 4 类真风险"""
        for expr, snap, expected, note in _CASES:
            with self.subTest(note=note, expr=expr):
                fn = _parse_precondition(expr)
                self.assertEqual(
                    fn(snap), expected,
                    f"风险未守：{note} | expr={expr!r} snap={snap!r}"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
