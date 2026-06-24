"""
test_control_shell - ControlShell 真风险守护

设计原则（参见 ADR-012）：
- 不为"测 Python 集合/dict 操作"而存在
- 每个测试都该回答"哪个未来改动会因这个失败被打回"

守护的真风险：
1. priority 策略必须真的按 metadata 数字排序（不是 sources 顺序）
2. 3 Agent 串行链必须按 preconditions 链式触发（最常见的协作模式）
3. action 抛异常必须 status=failed + 写 error::<name>
4. max_steps timeout 的设计语义：Agent 数 ≥ max_steps 才能触发
"""
from __future__ import annotations

import unittest

from agent_core.multi_agent.relationship import (
    Blackboard,
    Command,
    ControlShell,
    KnowledgeSource,
    RelationshipEngine,
    _parse_precondition,
)


def _make_ks(name: str, precond_str: str = "True", action=None) -> KnowledgeSource:
    return KnowledgeSource(
        name=name,
        role=name,
        preconditions=_parse_precondition(precond_str),
        action=action or (lambda bb, eng: Command(update={"facts": {f"result::{name}": "ok"}})),
    )


def _make_engine(ks_list):
    return RelationshipEngine(client=None, model="test", agents=ks_list)


class TestControlShellRiskPoints(unittest.TestCase):
    """每个测试守一个真风险点"""

    def test_priority_strategy_uses_metadata_map(self):
        """
        风险 1：priority 策略必须按 metadata.priority 数字排序，
        不能退化为 sources 顺序（曾 bug 风险点）。
        """
        engine = _make_engine([_make_ks("a"), _make_ks("b"), _make_ks("c")])
        bb = Blackboard(metadata={"priority": {"a": 3, "b": 1, "c": 2}})
        shell = ControlShell(bb, engine.agents, engine, strategy="priority")
        # 数字最小者优先 → b
        self.assertEqual(shell._select_source().name, "b")

    def test_three_agent_chain_activates_in_order(self):
        """
        风险 2：最常见的协作模式 — 3 Agent 串行链
        (a → b 需要 a 的结果 → c 需要 b 的结果)
        任意一环失败都会破坏整个工作流。
        """
        engine = _make_engine([
            _make_ks("a"),
            _make_ks("b", precond_str="facts.has('result::a')"),
            _make_ks("c", precond_str="facts.has('result::b')"),
        ])
        shell = ControlShell(Blackboard(), engine.agents, engine, max_steps=10)
        result_bb = shell.run()
        self.assertEqual(result_bb.status, "solved")
        self.assertIn("result::a", result_bb.facts)
        self.assertIn("result::b", result_bb.facts)
        self.assertIn("result::c", result_bb.facts)

    def test_action_exception_marks_failed(self):
        """
        风险 3：action 抛异常必须 status=failed + 写 error::<name> 到 facts
        （让上层可以诊断哪个 Agent 坏了，不能崩整个 run_loop）。
        """
        def bad_action(bb, eng):
            raise RuntimeError("intentional test failure")

        engine = _make_engine([_make_ks("a", action=bad_action)])
        shell = ControlShell(Blackboard(), engine.agents, engine, max_steps=10)
        result_bb = shell.run()
        self.assertEqual(result_bb.status, "failed")
        self.assertIn("error::a", result_bb.facts)
        self.assertIn("intentional test failure", result_bb.facts["error::a"])

    def test_max_steps_timeout_design_semantics(self):
        """
        风险 4：max_steps 触发条件 = Agent 数 ≥ max_steps
        这是 ControlShell 的设计语义（参见 ADR-011），如果未来重构改了
        for-else 的 break 条件，这个测试会先失败提示设计变更。
        """
        def make_loop(name):
            def action(bb, eng):
                return Command(
                    update={"facts": {name: bb.facts.get(name, 0) + 1}},
                    terminate=False,
                )
            return action

        # 6 Agent + max_steps=5：保证 5 步都有非空 candidates
        ks_list = [
            KnowledgeSource(
                name=n, role=n,
                preconditions=_parse_precondition("True"),
                action=make_loop(n),
            )
            for n in ["a", "b", "c", "d", "e", "f"]
        ]
        engine = _make_engine(ks_list)
        shell = ControlShell(Blackboard(), engine.agents, engine, max_steps=5)
        result_bb = shell.run()
        self.assertEqual(result_bb.status, "timeout")


if __name__ == "__main__":
    unittest.main(verbosity=2)
