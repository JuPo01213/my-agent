"""
test_run_loop - run_loop 真风险守护

设计原则（参见 ADR-012）：
- 不为"测 mock 行为"而存在
- 每个测试都该回答"哪个未来改动会因这个失败被打回"
- mock 出来的假 LLM 行为只在确认"代码自身反应正确"时有意义

守护的真风险：
1. 推理模型 content 为空 → 必须 fallback 到 reasoning_content（ADR-007）
2. 工具调用返回错误字符串 → 不崩，下一轮能继续
3. max_steps 耗尽 → 返回明确占位符
"""
from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import MagicMock

from agent_core.core.react_agent import run_loop


# ---------------------------------------------------------------------------
# Mock 工具：构造 OpenAI 兼容 response 对象
# ---------------------------------------------------------------------------

class _MockFunction:
    def __init__(self, name: str, arguments: str = "{}"):
        self.name = name
        self.arguments = arguments


class _MockToolCall:
    def __init__(self, call_id: str, name: str, arguments: str = "{}"):
        self.id = call_id
        self.function = _MockFunction(name, arguments)


class _MockMessage:
    def __init__(
        self,
        content: str | None = None,
        reasoning_content: str | None = None,
        tool_calls: list[_MockToolCall] | None = None,
    ):
        self.content = content
        self.reasoning_content = reasoning_content
        self.tool_calls = tool_calls


class _MockChoice:
    def __init__(self, message: _MockMessage):
        self.message = message


class _MockResponse:
    def __init__(self, message: _MockMessage):
        self.choices = [_MockChoice(message)]


def _make_client(responses: list[_MockResponse]) -> MagicMock:
    """构造一个 mock client，按顺序返回 responses"""
    client = MagicMock()
    iter_responses = iter(responses)

    def _create(*args, **kwargs):
        try:
            return next(iter_responses)
        except StopIteration:
            raise AssertionError("LLM 调用次数超过预期")

    client.chat.completions.create.side_effect = _create
    return client


# ---------------------------------------------------------------------------
# 真风险点
# ---------------------------------------------------------------------------

class TestRunLoopRiskPoints(unittest.TestCase):
    """每个测试守一个真风险点"""

    def test_reasoning_model_fallback_works(self):
        """
        风险 1：StepFun step-3.7-flash 等推理模型 content 为空，
        真实输出在 reasoning_content。run_loop 必须 fallback。
        """
        client = _make_client([
            _MockResponse(_MockMessage(content=None, reasoning_content="推理后的答案"))
        ])
        result = run_loop("问题", client, model="step-3.7-flash")
        self.assertEqual(result, "推理后的答案")

    def test_unknown_tool_returns_error_string_no_crash(self):
        """
        风险 2：LLM 调了未注册工具名 → 错误返回字符串而非抛异常，
        让 LLM 自我修正（生产里推理模型容易幻觉工具名）。
        """
        client = _make_client([
            _MockResponse(_MockMessage(
                content=None,
                tool_calls=[_MockToolCall("call_1", "non_existent_tool", '{}')],
            )),
            _MockResponse(_MockMessage(content="好的，我修正了")),
        ])
        result = run_loop("问题", client, model="test-model")
        self.assertEqual(result, "好的，我修正了")

    def test_max_steps_returns_clear_placeholder(self):
        """
        风险 3：工具调用一直不收敛触发 max_steps 上限，
        必须返回明确占位符（让上层知道是"超限"而非"无回答"）。
        """
        tool_response = _MockResponse(_MockMessage(
            content=None,
            tool_calls=[_MockToolCall("call_x", "calculator", '{"a": 1, "b": 2}')],
        ))
        client = _make_client([tool_response] * 3)  # 3 个相同 response
        result = run_loop("问题", client, model="test-model", max_steps=3)
        self.assertEqual(result, "超过最大步数限制，未得出最终答案。")


if __name__ == "__main__":
    unittest.main(verbosity=2)
