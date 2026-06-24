"""
experiments/2026-06-24-event-stream.py
=======================================

目的：演示"中性 trace → 前端契约事件"的完整链路，证明：
  1. core.run_loop 在 return_trace=True 时产出中性 trace
  2. multi_agent.ControlShell 在 on_event 不为 None 时把 trace emit 出去
  3. frontend.adapter.wrap_trace_to_events 能把 trace 翻译成 8 类前端事件
  4. 日志用 UTF-8 编码（不走 PowerShell Tee-Object）

场景：沿用 2026-06-24-scenario.yaml 的 advisor → strategist → writer，
      但这次开 on_event，把所有事件落盘。
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 日志：写文件 + stderr，强制 utf-8
LOG_FILE = PROJECT_ROOT / "experiments" / "2026-06-24-event-stream.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
_file_handler = logging.FileHandler(str(LOG_FILE), mode="w", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(message)s"))
logger = logging.getLogger("event_stream")
logger.setLevel(logging.INFO)
logger.handlers = [_file_handler, logging.StreamHandler(sys.stderr)]


def log(msg: str = "") -> None:
    logger.info(msg)


def banner(title: str) -> None:
    log()
    log("=" * 70)
    log(title)
    log("=" * 70)


from openai import OpenAI
from agent_core.config import STEPFUN_API_KEY, STEPFUN_BASE_URL, STEPFUN_MODEL
from agent_core.multi_agent.relationship import (
    Blackboard,
    Command,
    KnowledgeSource,
    RelationshipEngine,
)
from agent_core.multi_agent.agent_api import run_react_agent
from agent_core.frontend import EventBus, wrap_trace_to_events, aggregate_run_events
from agent_core.core.tool_registry import TOOLS


def main() -> int:
    banner("事件流实验 — 中性 trace → 前端契约事件")
    log(f"base_url : {STEPFUN_BASE_URL}")
    log(f"model    : {STEPFUN_MODEL}")
    log(f"api_key  : {STEPFUN_API_KEY[:8]}...{STEPFUN_API_KEY[-4:]} (已脱敏)")
    log(f"log file : {LOG_FILE}")
    log(f"已注册工具 : {list(TOOLS.keys())}")

    # 1. 构造真实 LLM 客户端
    client = OpenAI(api_key=STEPFUN_API_KEY, base_url=STEPFUN_BASE_URL)

    # 2. 从 YAML 加载
    agents_yaml = PROJECT_ROOT / "experiments" / "2026-06-24-scenario.yaml"
    rels_yaml = PROJECT_ROOT / "experiments" / "2026-06-24-scenario-relationships.yaml"
    log(f"agents_yaml        : {agents_yaml}")
    log(f"relationships_yaml : {rels_yaml}")

    # 3. 用 EventBus 收集事件
    bus = EventBus()

    engine = RelationshipEngine.from_yaml(
        client=client,
        model=STEPFUN_MODEL,
        agents_yaml_path=str(agents_yaml),
        relationships_yaml_path=str(rels_yaml),
    )
    priority_map = engine._relationships.get("priority", {})

    log()
    log("加载的 Agent：")
    for a in engine.agents:
        tools_repr = "ALL（默认）" if a.tools is None else a.tools
        log(f"  agent {a.name}: tools={tools_repr}  max_iter={a.max_iter}")

    # 4. 启动 OODA 循环，传入 on_event
    banner("启动 OODA 循环（on_event=bus.emit）")
    t0 = time.time()
    try:
        blackboard = engine.run(
            user_query=(
                "请就一家 200 人研发团队、6 个月完成 AI 转型的预算分配，"
                "依次回答三个问题："
                "(1) 团队需要具备哪 5 项核心 AI 能力，按重要度排序；"
                "(2) 1500 万元预算如何在招聘 / 培训 / 工具 / 外部咨询这 4 项上分配，"
                "    用 calculator 工具给出每项的百分比并验证总和等于 100；"
                "(3) 6 个月分 3 个阶段的关键里程碑，每个阶段 2 个月。"
            ),
            strategy="priority",
            metadata={"priority": priority_map},
            on_event=bus.emit,
        )
    except Exception as exc:
        log(f"[FATAL] engine.run 抛异常：{exc}")
        logger.exception("engine.run 异常")
        return 2
    elapsed = time.time() - t0

    # 5. 黑板最终状态
    banner("OODA 循环结束 — 黑板最终状态")
    log(f"status         : {blackboard.status}")
    log(f"current_step   : {blackboard.current_step}")
    log(f"history len    : {len(blackboard.history)}")
    log(f"elapsed        : {elapsed:.2f}s")
    log()
    log("facts 概览：")
    for k, v in blackboard.facts.items():
        log(f"  - {k}: 共 {len(str(v))} 字")

    # 6. 事件流概览
    banner("EventBus 收集到的事件")
    log(f"总线事件数 : {len(bus.events)}")
    type_counts: dict[str, int] = {}
    for ev in bus.events:
        t = ev.get("type", ev.get("kind", "unknown"))
        type_counts[t] = type_counts.get(t, 0) + 1
    log("事件类型分布：")
    for t, c in sorted(type_counts.items()):
        log(f"  {t}: {c}")
    log()
    log("前 30 条事件（JSON）：")
    for ev in bus.events[:30]:
        log(json.dumps(ev, ensure_ascii=False))

    # 7. 用 frontend.adapter 验证翻译
    banner("frontend.adapter 验证")
    # 从 bus.events 里提取各 Agent 的 trace（kind 字段）
    agents_traces: list[tuple[str, list[dict]]] = []
    current_agent = None
    current_trace: list[dict] = []
    for ev in bus.events:
        if ev.get("type") == "agent.activate":
            if current_agent and current_trace:
                agents_traces.append((current_agent, current_trace))
            current_agent = ev.get("agent")
            current_trace = []
        elif ev.get("kind") in ("llm", "tool", "final", "error"):
            current_trace.append({
                "kind": ev.get("kind"),
                "step": ev.get("step", 0),
                "data": ev.get("data", {}),
            })
    if current_agent and current_trace:
        agents_traces.append((current_agent, current_trace))

    log(f"agents_traces 数量: {len(agents_traces)}")
    for agent_name, trace in agents_traces:
        log(f"  Agent {agent_name}: {len(trace)} 条 trace")

    # 用 aggregate_run_events 重新聚合
    aggregated = aggregate_run_events(
        user_query=blackboard.metadata.get("user_query", ""),
        agents_traces=agents_traces,
        run_id="run-001",
        final_status=blackboard.status,
        started_at=t0,
        ended_at=time.time(),
    )
    log(f"aggregate_run_events 产出事件数: {len(aggregated)}")
    log("聚合后事件类型分布：")
    agg_counts: dict[str, int] = {}
    for ev in aggregated:
        t = ev.get("type", "unknown")
        agg_counts[t] = agg_counts.get(t, 0) + 1
    for t, c in sorted(agg_counts.items()):
        log(f"  {t}: {c}")

    # 8. KPI
    banner("KPI 校验")
    expectations = [
        ("status == 'solved'", blackboard.status == "solved"),
        ("bus.events 非空", len(bus.events) > 0),
        ("含 agent.activate 事件", bus.count("agent.activate") >= 1),
        ("含 final 事件（中性 trace）", bus.count("final") >= 1),
        ("含 tool 事件（中性 trace）", bus.count("tool") >= 1),
        ("聚合后含 run.done", any(e.get("type") == "run.done" for e in aggregated)),
        ("facts 含 result::advisor", "result::advisor" in blackboard.facts),
        ("facts 含 result::strategist", "result::strategist" in blackboard.facts),
        ("facts 含 result::writer", "result::writer" in blackboard.facts),
    ]
    all_ok = True
    for name, ok in expectations:
        flag = "OK  " if ok else "FAIL"
        if not ok:
            all_ok = False
        log(f"  [{flag}] {name}")
    log()
    log("ALL OK" if all_ok else "SOME FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
