"""
多 Agent 协作示例：研究助手
=============================
演示 Supervisor 模式：用户输入主题 → 调度 Agent A 搜索 → Agent B 分析 → Agent C 总结

运行方式：
    python agent_core/multi_agent_demo.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
import os

# ---------------------------------------------------------------------------
# 1. 状态定义：所有 Agent 共享的数据
# ---------------------------------------------------------------------------
# 区别于之前的 messages 列表，这里用 dataclass 定义结构化状态


@dataclass
class AgentState:
    """多 Agent 协作时的共享状态"""
    task: str = ""                    # 用户原始任务
    search_result: str = ""            # Agent A 搜索结果
    analysis_result: str = ""         # Agent B 分析结果
    final_answer: str = ""             # 最终输出
    current_agent: str = "supervisor"  # 当前执行到哪个 Agent
    step: int = 0                     # 执行的步骤数
    history: list[str] = field(default_factory=list)  # 执行历史


# ---------------------------------------------------------------------------
# 2. 工具定义：各 Agent 可调用的工具
# ---------------------------------------------------------------------------

def web_search(query: str) -> str:
    """模拟搜索，返回一段占位文本"""
    return f"【搜索结果】关于「{query}」的信息...（这里是真实搜索 API 返回）"


def analyze_content(content: str, focus: str) -> str:
    """模拟分析内容"""
    return f"【分析结果】从「{focus}」角度分析：{content[:50]}..."


def write_report(search_result: str, analysis: str) -> str:
    """模拟写报告"""
    return f"""【研究报告】

基于以下信息整理：

搜索摘要：{search_result[:100]}...
分析要点：{analysis[:100]}...

结论：这是一个基于上述信息的简要报告。"""


# ---------------------------------------------------------------------------
# 3. 各 Agent 的实现
# ---------------------------------------------------------------------------

def supervisor_agent(state: AgentState) -> AgentState:
    """
    Supervisor Agent：负责任务调度
    根据当前状态，决定下一步调用哪个 Agent
    """
    state.step += 1
    state.current_agent = "supervisor"

    print(f"\n{'='*50}")
    print(f"[Step {state.step}] Supervisor 调度决策")
    print(f"{'='*50}")

    # 调度逻辑：根据当前状态决定下一步
    if not state.search_result:
        # 还没有搜索结果，去搜索
        print("决策：去 Search Agent")
        return search_agent(state)

    elif not state.analysis_result:
        # 有搜索结果，去分析
        print("决策：去 Analysis Agent")
        return analysis_agent(state)

    elif not state.final_answer:
        # 有分析结果，去写报告
        print("决策：去 Report Agent")
        return report_agent(state)

    else:
        # 全部完成
        print("决策：任务完成")
        state.history.append(f"[Step {state.step}] 任务完成")
        return state


def search_agent(state: AgentState) -> AgentState:
    """Agent A：负责搜索"""
    state.current_agent = "search"
    state.step += 1

    print(f"\n{'='*50}")
    print(f"[Step {state.step}] Search Agent 执行")
    print(f"{'='*50}")

    # 模拟：搜索用户任务相关的内容
    state.search_result = web_search(state.task)
    print(f"搜索结果：{state.search_result}")

    state.history.append(f"[Step {state.step}] Search Agent: 已搜索")

    # 搜索完成后，回到 Supervisor 决定下一步
    return supervisor_agent(state)


def analysis_agent(state: AgentState) -> AgentState:
    """Agent B：负责分析"""
    state.current_agent = "analysis"
    state.step += 1

    print(f"\n{'='*50}")
    print(f"[Step {state.step}] Analysis Agent 执行")
    print(f"{'='*50}")

    # 模拟：分析搜索结果
    state.analysis_result = analyze_content(state.search_result, "关键信息提取")
    print(f"分析结果：{state.analysis_result}")

    state.history.append(f"[Step {state.step}] Analysis Agent: 已分析")

    # 分析完成后，回到 Supervisor 决定下一步
    return supervisor_agent(state)


def report_agent(state: AgentState) -> AgentState:
    """Agent C：负责写报告"""
    state.current_agent = "report"
    state.step += 1

    print(f"\n{'='*50}")
    print(f"[Step {state.step}] Report Agent 执行")
    print(f"{'='*50}")

    # 模拟：整合搜索和分析结果，写报告
    state.final_answer = write_report(state.search_result, state.analysis_result)
    print(f"报告已生成")

    state.history.append(f"[Step {state.step}] Report Agent: 已生成报告")

    # 报告完成后，回到 Supervisor
    return supervisor_agent(state)


# ---------------------------------------------------------------------------
# 4. 主程序
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*60)
    print("  多 Agent 协作演示：研究助手")
    print("  模式：Supervisor 调度 Search → Analysis → Report")
    print("="*60)

    # 创建初始状态
    state = AgentState(task="人工智能最新发展趋势")

    # 从 Supervisor 开始执行
    print("\n开始执行...\n")
    result = supervisor_agent(state)

    # 输出最终结果
    print("\n" + "="*60)
    print("  执行完成")
    print("="*60)
    print(f"\n执行步骤数：{result.step}")
    print(f"\n执行历史：")
    for h in result.history:
        print(f"  - {h}")

    print(f"\n{'='*60}")
    print("  最终报告")
    print("="*60)
    print(result.final_answer)


if __name__ == "__main__":
    main()
