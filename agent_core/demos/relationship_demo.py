"""
agent_core.demos.relationship_demo - 关系驱动多 Agent 协作演示
============================================================

**这是一个可运行示例**，演示如何用 YAML 配置文件驱动多 Agent 协作。

运行方式：
    python agent_core/demos/relationship_demo.py

**核心效果**：
- 加载 config/agents.yaml + config/relationships.yaml
- 构造 3 个 Agent：researcher → analyst → writer
- 按 priority 策略调度
- 每个 Agent 通过 preconditions 强约束激活
- 最终输出协同完成的研究报告

**这是一个 mock 版本**，不调用真实 LLM（用 mock 模拟 LLM 响应）。
要看真实 LLM 调用效果，请把 MockLLMClient 替换为真实的 OpenAI 客户端。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# 路径处理：让脚本能直接运行
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent_core.multi_agent.relationship import (
    Blackboard,
    Command,
    KnowledgeSource,
    ControlShell,
    RelationshipEngine,
    _parse_precondition,
)


# ============================================================
# Mock LLM 客户端（不调用真实 API）
# ============================================================

class _MockCompletions:
    """Mock 的 client.chat.completions 子层。"""
    def __init__(self, parent):
        self.parent = parent

    def create(self, model, messages, temperature, tools, tool_choice):
        """模拟 OpenAI chat.completions.create 调用。"""
        self.parent._call_count += 1
        # 从 system prompt 识别 Agent 身份
        system_msg = next(
            (m["content"] for m in messages if m.get("role") == "system"),
            "",
        )

        if "高级研究员" in system_msg:
            content = (
                "根据搜索结果，2024 年 LLM Agent 领域呈现三大趋势：\n"
                "1. 多 Agent 协作框架成熟（LangGraph、CrewAI、AutoGen）\n"
                "2. 工具调用协议标准化（Function Calling、MCP）\n"
                "3. Agent 记忆与反思能力大幅提升"
            )
        elif "数据分析师" in system_msg:
            content = (
                "【分析洞察】\n"
                "- 趋势 1 表明：单一 Agent 已无法应对复杂任务\n"
                "- 趋势 2 表明：标准化是生态成熟的关键\n"
                "- 趋势 3 表明：长时记忆成为新瓶颈"
            )
        elif "技术作家" in system_msg:
            content = (
                "# LLM Agent 2024 趋势报告\n\n"
                "## 摘要\n"
                "2024 年 LLM Agent 领域三大趋势：多 Agent 协作、工具标准化、记忆增强。\n\n"
                "## 详细分析\n"
                "详见上文研究材料和分析洞察。\n\n"
                "## 结论\n"
                "多 Agent 协作是必然方向。"
            )
        else:
            content = "（通用回答）"

        return _MockResponse(content)


class _MockChat:
    """Mock 的 client.chat 子层。"""
    def __init__(self, parent):
        self.parent = parent
        self.completions = _MockCompletions(parent)


class MockLLMClient:
    """
    模拟 LLM 客户端：根据 system prompt 中的 Agent 身份返回不同回答。

    接口必须与 OpenAI 客户端一致：client.chat.completions.create(...)

    替换为真实客户端时：
        from openai import OpenAI
        client = OpenAI(api_key=..., base_url=...)
    """

    def __init__(self):
        self._call_count = 0
        # 公开属性：client.chat.completions.create
        self.chat = _MockChat(self)


class _MockResponse:
    """模拟 OpenAI chat.completions.create 返回值。"""
    def __init__(self, content: str):
        choice = _MockChoice(_MockMessage(content))
        self.choices = [choice]


class _MockChoice:
    def __init__(self, message):
        self.message = message


class _MockMessage:
    def __init__(self, content: str):
        self.content = content
        self.tool_calls = None  # mock 模式不调用工具


# ============================================================
# 演示 1：直接用 Python API（不读 YAML）
# ============================================================

def demo_python_api():
    """演示 1：纯 Python 方式构造 3 个 Agent 协作。"""
    print("=" * 60)
    print("演示 1：纯 Python API（不读 YAML）")
    print("=" * 60)

    # 1. 准备 mock 客户端
    client = MockLLMClient()

    # 2. 用代码构造 3 个 KnowledgeSource
    researcher = KnowledgeSource(
        name="researcher",
        role="高级研究员",
        goal="收集关于用户查询主题的最新信息",
        backstory="清华 AI 实验室研究员",
        tools=["search"],
        max_iter=5,
    )
    analyst = KnowledgeSource(
        name="analyst",
        role="高级数据分析师",
        goal="分析研究材料",
        tools=["calculator"],
        max_iter=5,
        # preconditions: 必须先有 researcher 的结果
        preconditions=_parse_precondition("facts.has('result::researcher')"),
    )
    writer = KnowledgeSource(
        name="writer",
        role="资深技术作家",
        goal="写报告",
        tools=[],
        max_iter=5,
        # preconditions: 必须先有 analyst 的结果
        preconditions=_parse_precondition("facts.has('result::analyst')"),
    )

    # 3. 构造 engine
    engine = RelationshipEngine(
        client=client,  # type: ignore
        model="mock-model",
        agents=[researcher, analyst, writer],
        max_steps=10,
    )

    # 4. 启动协作
    blackboard = engine.run(
        user_query="调研 2024 年 LLM Agent 领域的最新进展",
        strategy="priority",
        metadata={"priority": {"researcher": 1, "analyst": 2, "writer": 3}},
    )

    # 5. 输出结果
    _print_blackboard_summary(blackboard, "Python API 模式")


# ============================================================
# 演示 2：从 YAML 文件加载
# ============================================================

def demo_yaml_driven():
    """演示 2：从 YAML 加载（零代码改动即可改变协作流程）。"""
    print()
    print("=" * 60)
    print("演示 2：YAML 驱动（推荐生产用法）")
    print("=" * 60)

    client = MockLLMClient()

    # YAML 路径（相对项目根）
    config_dir = PROJECT_ROOT / "config"
    agents_yaml = config_dir / "agents.yaml"
    relationships_yaml = config_dir / "relationships.yaml"

    # 加载 YAML
    engine = RelationshipEngine.from_yaml(
        client=client,  # type: ignore
        model="mock-model",
        agents_yaml_path=str(agents_yaml),
        relationships_yaml_path=str(relationships_yaml),
    )

    # 优先级注入（从 relationships.yaml 读 priority 字段）
    priority_map = engine._relationships.get("priority", {})

    # 启动协作
    blackboard = engine.run(
        user_query="调研 2024 年 LLM Agent 领域的最新进展",
        strategy="priority",
        metadata={"priority": priority_map},
    )

    # 输出结果
    _print_blackboard_summary(blackboard, "YAML 驱动模式")


# ============================================================
# 演示 3：自定义 action（不用默认 LLM action）
# ============================================================

def demo_custom_action():
    """演示 3：自定义 action，直接用 Python 函数不用 LLM。"""
    print()
    print("=" * 60)
    print("演示 3：自定义 action（不调 LLM，纯函数式协作）")
    print("=" * 60)

    # 自定义 action：把数字 + 1，结果用 result::add_one 标记
    def add_one_action(blackboard: Blackboard, engine: RelationshipEngine) -> Command:
        prev = blackboard.facts.get("counter", 0)
        return Command(
            update={"facts": {"counter": prev + 1, "result::add_one": prev + 1}},
        )

    def double_action(blackboard: Blackboard, engine: RelationshipEngine) -> Command:
        prev = blackboard.facts.get("counter", 0)
        return Command(
            update={"facts": {"counter": prev * 2, "result::doubler": prev * 2}},
        )

    # 不需要 LLM 客户端
    add_one = KnowledgeSource(
        name="add_one",
        action=add_one_action,
        preconditions=_parse_precondition("True"),
    )
    doubler = KnowledgeSource(
        name="doubler",
        action=double_action,
        preconditions=_parse_precondition("facts.has('result::add_one')"),
    )

    engine = RelationshipEngine(
        client=None,  # type: ignore
        model="",
        agents=[add_one, doubler],
    )

    blackboard = engine.run(
        user_query="从 0 开始：+1 然后 ×2",
        strategy="first_match",
        # 终止条件：doubler 完成
        done_when=lambda bb: "result::doubler" in bb.facts,
    )

    print(f"最终 counter = {blackboard.facts.get('counter')}")
    print(f"  预期：0 + 1 = 1, 1 * 2 = 2")
    print(f"  history:")
    for h in blackboard.history:
        if h.get("op") == "update":
            print(f"    - step {h['step']}: {h['source']} 写入 {h['key']}")


# ============================================================
# 辅助：打印黑板摘要
# ============================================================

def _print_blackboard_summary(blackboard: Blackboard, title: str):
    print(f"\n=== {title} 协作完成 ===")
    print(f"状态：{blackboard.status}")
    print(f"总步数：{len(blackboard.history)}")
    print(f"\n黑板事实：")
    for k, v in blackboard.facts.items():
        v_str = str(v)[:80] + "..." if len(str(v)) > 80 else str(v)
        print(f"  - {k}: {v_str}")
    print(f"\n最终报告（writer 的输出）：")
    final = blackboard.facts.get("result::writer", "（无）")
    final_str = str(final)[:200] + "..." if len(str(final)) > 200 else str(final)
    print(f"  {final_str}")


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    demo_python_api()
    demo_yaml_driven()
    demo_custom_action()
    print()
    print("=" * 60)
    print("全部演示完成")
    print("=" * 60)
