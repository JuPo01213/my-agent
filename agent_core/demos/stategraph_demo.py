"""
方案 B：自己实现状态图（简化版 StateGraph）
==============================================
核心思路：用字典定义图结构，节点是函数，边决定路由

运行方式：
    python agent_core/stategraph_demo.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Literal
import re


# ---------------------------------------------------------------------------
# 1. 状态定义
# ---------------------------------------------------------------------------

@dataclass
class State:
    """工作流状态"""
    task: str = ""
    search_result: str = ""
    analysis_result: str = ""
    final_answer: str = ""
    step: int = 0
    route_log: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 2. 状态图核心：定义节点和边
# ---------------------------------------------------------------------------

class StateGraph:
    """
    简化的状态图实现
    核心组成：
    - nodes: 节点字典 {节点名: 节点函数}
    - edges: 边字典 {节点名: [出边列表]}
    - conditional_edges: 条件边字典 {节点名: 路由函数}
    """

    def __init__(self):
        self.nodes: dict[str, Callable] = {}
        self.edges: dict[str, list[str]] = {}      # 固定边
        self.conditional_edges: dict[str, Callable] = {}  # 条件边
        self.start_node: str = ""
        self.end_nodes: set[str] = set()

    def add_node(self, name: str, func: Callable):
        """添加节点"""
        self.nodes[name] = func

    def add_edge(self, from_node: str, to_node: str):
        """添加固定边：A → B"""
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)

    def add_conditional_edges(self, from_node: str, router: Callable):
        """
        添加条件边：A → [B|C|D]（根据 state 决定）
        router 函数返回目标节点名
        """
        self.conditional_edges[from_node] = router

    def set_entry_point(self, node: str):
        """设置入口节点"""
        self.start_node = node

    def add_end_point(self, node: str):
        """添加结束节点"""
        self.end_nodes.add(node)

    def run(self, initial_state: dict) -> dict:
        """
        执行状态图
        从 entry_point 开始，按照边的指引流转，直到到达 end_point
        """
        state = State(**initial_state)

        # 从入口开始
        current_node = self.start_node

        while True:
            state.step += 1
            state.route_log.append(f"Step {state.step}: {current_node}")

            # 执行当前节点
            if current_node not in self.nodes:
                raise ValueError(f"未知节点: {current_node}")

            # 节点函数返回更新的 state
            state = self.nodes[current_node](state)

            # 检查是否到达结束节点
            if current_node in self.end_nodes:
                break

            # 根据边决定下一步
            if current_node in self.conditional_edges:
                # 条件边：调用路由函数决定目标
                router = self.conditional_edges[current_node]
                current_node = router(state)
            elif current_node in self.edges:
                # 固定边：直接取第一条
                current_node = self.edges[current_node][0]
            else:
                raise ValueError(f"节点 {current_node} 没有定义出边")

        return state


# ---------------------------------------------------------------------------
# 3. 节点实现
# ---------------------------------------------------------------------------

def search_node(state: State) -> State:
    """搜索节点"""
    print(f"\n[Node: search] 执行搜索...")
    # 模拟：根据任务是否需要深入分析决定结果详细程度
    if "分析" in state.task or "深度" in state.task:
        # 复杂任务，搜索结果长
        state.search_result = "这是一段非常详细的搜索结果，包含了关于" + state.task + "的多个方面的深入分析，包括技术趋势、市场动态、最新进展等重要信息..."
    else:
        # 简单任务，搜索结果短
        state.search_result = f"关于「{state.task}」的结果"
    return state


def analysis_node(state: State) -> State:
    """分析节点"""
    print(f"[Node: analysis] 分析内容...")
    state.analysis_result = f"分析：{state.search_result[:30]}..."
    return state


def report_node(state: State) -> State:
    """报告节点"""
    print(f"[Node: report] 生成报告...")
    state.final_answer = f"""【研究报告】
搜索：{state.search_result}
分析：{state.analysis_result}
---
结论：报告完成"""
    return state


def simple_report_node(state: State) -> State:
    """简单报告节点（不需要分析）"""
    print(f"[Node: simple_report] 直接生成简短报告...")
    state.final_answer = f"【简短报告】关于「{state.task}」的简要信息。"
    return state


# ---------------------------------------------------------------------------
# 4. 路由函数（条件边的核心）
# ---------------------------------------------------------------------------

def router_after_search(state: State) -> str:
    """搜索后路由：根据搜索结果决定下一步"""
    print(f"   [Router] 搜索结果长度: {len(state.search_result)}")
    if len(state.search_result) > 50:
        # 结果较长，需要分析
        return "analysis"
    else:
        # 结果简短，直接出报告
        return "simple_report"


def router_after_analysis(state: State) -> str:
    """分析后路由"""
    return "report"


def router_end(state: State) -> str:
    """结束节点（不执行任何操作）"""
    return "__END__"


# ---------------------------------------------------------------------------
# 5. 构建状态图
# ---------------------------------------------------------------------------

def build_research_graph() -> StateGraph:
    """构建研究助手状态图"""
    graph = StateGraph()

    # 添加节点
    graph.add_node("search", search_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("report", report_node)
    graph.add_node("simple_report", simple_report_node)

    # 设置入口
    graph.set_entry_point("search")

    # 设置条件边
    graph.add_conditional_edges("search", router_after_search)
    graph.add_conditional_edges("analysis", router_after_analysis)

    # 设置结束节点
    graph.add_end_point("report")
    graph.add_end_point("simple_report")

    return graph


# ---------------------------------------------------------------------------
# 6. 主程序
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  方案 B：状态图（StateGraph）演示")
    print("  特点：节点 + 边 + 条件路由")
    print("=" * 60)

    # 场景 1：复杂任务（需要分析）
    print("\n" + "-" * 40)
    print("场景 1：复杂任务")
    print("-" * 40)

    graph = build_research_graph()
    result = graph.run({"task": "人工智能最新发展趋势和深度分析"})

    print(f"\n执行路径：{' → '.join(result.route_log)}")
    print(f"\n最终结果：\n{result.final_answer}")

    # 场景 2：简单任务（不需要分析）
    print("\n" + "-" * 40)
    print("场景 2：简单任务")
    print("-" * 40)

    graph2 = build_research_graph()
    result2 = graph2.run({"task": "今天天气"})

    print(f"\n执行路径：{' → '.join(result2.route_log)}")
    print(f"\n最终结果：\n{result2.final_answer}")


if __name__ == "__main__":
    main()
