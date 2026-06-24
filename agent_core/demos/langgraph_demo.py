"""
方案 C：引入 LangGraph 部分组件
==================================
使用 LangGraph 的 StateGraph 和条件边，实现同样的研究助手

运行方式：
    pip install langgraph  # 需要先安装
    python agent_core/langgraph_demo.py
"""

from __future__ import annotations
from typing import TypedDict
from langgraph.graph import StateGraph, END


# ---------------------------------------------------------------------------
# 1. 定义状态（LangGraph 风格）
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    """LangGraph 使用 TypedDict 定义状态"""
    task: str
    search_result: str
    analysis_result: str
    final_answer: str
    step: int


# ---------------------------------------------------------------------------
# 2. 定义节点函数
# ---------------------------------------------------------------------------

def search_node(state: AgentState) -> AgentState:
    """搜索节点"""
    print(f"\n[Node: search] 执行搜索...")
    state["step"] = state.get("step", 0) + 1
    state["search_result"] = f"关于「{state['task']}」的搜索结果..."
    return state


def analysis_node(state: AgentState) -> AgentState:
    """分析节点"""
    print(f"[Node: analysis] 分析内容...")
    state["step"] = state.get("step", 0) + 1
    result = state.get("search_result", "")
    state["analysis_result"] = f"分析：{result[:30]}..."
    return state


def report_node(state: AgentState) -> AgentState:
    """报告节点"""
    print(f"[Node: report] 生成报告...")
    state["step"] = state.get("step", 0) + 1
    state["final_answer"] = f"""【研究报告】
搜索：{state.get('search_result', '')}
分析：{state.get('analysis_result', '')}
---
结论：报告完成"""
    return state


def simple_report_node(state: AgentState) -> AgentState:
    """简单报告节点"""
    print(f"[Node: simple_report] 直接生成简短报告...")
    state["step"] = state.get("step", 0) + 1
    state["final_answer"] = f"【简短报告】关于「{state['task']}」的简要信息。"
    return state


# ---------------------------------------------------------------------------
# 3. 定义路由函数（条件边）
# ---------------------------------------------------------------------------

def route_after_search(state: AgentState) -> str:
    """搜索后路由"""
    result = state.get("search_result", "")
    if len(result) > 50:
        return "analysis"
    return "simple_report"


def route_after_analysis(state: AgentState) -> str:
    """分析后路由"""
    return "report"


# ---------------------------------------------------------------------------
# 4. 构建图
# ---------------------------------------------------------------------------

def build_langgraph() -> StateGraph:
    """构建 LangGraph"""
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("search", search_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("report", report_node)
    graph.add_node("simple_report", simple_report_node)

    # 设置入口
    graph.set_entry_point("search")

    # 条件边：search 之后去哪
    graph.add_conditional_edges(
        "search",
        route_after_search,
        {
            "analysis": "analysis",
            "simple_report": "simple_report"
        }
    )

    # analysis 之后去哪
    graph.add_conditional_edges(
        "analysis",
        route_after_analysis,
        {"report": "report"}
    )

    # 设置结束节点
    graph.add_edge("report", END)
    graph.add_edge("simple_report", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# 5. 主程序
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  方案 C：LangGraph 演示")
    print("  特点：使用官方框架，API 更规范")
    print("=" * 60)

    compiled_graph = build_langgraph()

    # 场景 1：复杂任务
    print("\n" + "-" * 40)
    print("场景 1：复杂任务")
    print("-" * 40)

    result = compiled_graph.invoke({
        "task": "人工智能最新发展趋势和深度分析",
        "step": 0
    })

    print(f"\n最终结果：\n{result['final_answer']}")

    # 场景 2：简单任务
    print("\n" + "-" * 40)
    print("场景 2：简单任务")
    print("-" * 40)

    result2 = compiled_graph.invoke({
        "task": "今天天气",
        "step": 0
    })

    print(f"\n最终结果：\n{result2['final_answer']}")


if __name__ == "__main__":
    main()
