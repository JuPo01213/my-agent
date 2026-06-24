"""
experiments/2026-06-24-scenario.py
==================================

目的：完整跑一个"纯 LLM"场景，证明 relationship.py 的 ReAct 循环在工作。
展示完整流程、过程与结果。

场景：传统软件公司 6 个月 AI 转型路线图
- advisor（顾问）: 给出 AI 工程师能力模型
- strategist（策略师）: 转化为 6 个月分阶段计划
- writer（作家）: 写为给 CEO 的咨询报告

实现关键：**保留默认 ReAct 循环**（KnowledgeSource._default_action → run_react_agent
→ run_loop）。不显式限制 tools 字段，让 LLM 自主决定是否调用工具。
- 如果任务不需要工具，ReAct 循环会在第 1 轮 thought 后直接给 final answer
- 如果需要（如算预算），LLM 会主动调 calculator 进入多轮循环

日志：experiments/2026-06-24-scenario.log
"""
from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 日志：写文件 + stderr
LOG_FILE = PROJECT_ROOT / "experiments" / "2026-06-24-scenario.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
_file_handler = logging.FileHandler(str(LOG_FILE), mode="w", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(message)s"))
logger = logging.getLogger("scenario")
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
from agent_core.core.tool_registry import TOOLS


def main() -> int:
    banner("场景实验 — 纯 LLM 协作：6 个月 AI 转型路线图（默认 ReAct 循环）")
    log(f"base_url : {STEPFUN_BASE_URL}")
    log(f"model    : {STEPFUN_MODEL}")
    log(f"api_key  : {STEPFUN_API_KEY[:8]}...{STEPFUN_API_KEY[-4:]} (已脱敏)")
    log(f"log file : {LOG_FILE}")
    log(f"已注册工具 : {list(TOOLS.keys())}  （不显式限制，让 LLM 自主决定）")

    # 1. 构造真实 LLM 客户端
    client = OpenAI(api_key=STEPFUN_API_KEY, base_url=STEPFUN_BASE_URL)

    # 2. 从 YAML 加载
    agents_yaml = PROJECT_ROOT / "experiments" / "2026-06-24-scenario.yaml"
    rels_yaml = PROJECT_ROOT / "experiments" / "2026-06-24-scenario-relationships.yaml"
    log(f"agents_yaml        : {agents_yaml}")
    log(f"relationships_yaml : {rels_yaml}")

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
        # tools=None 表示用所有已注册工具；显式 [] 才表示不调
        tools_repr = "ALL（默认）" if a.tools is None else a.tools
        log(f"  agent {a.name}: tools={tools_repr}  max_iter={a.max_iter}  action={a.action.__qualname__}")
    log(f"priority_map : {priority_map}")

    # 不替换 action！用默认 _default_action → run_react_agent → run_loop（完整 ReAct 循环）
    log()
    log("使用默认 _default_action（→ run_react_agent → ReAct 循环）")

    # 3. 业务输入
    user_query = (
        "请就一家 200 人研发团队、6 个月完成 AI 转型的预算分配，"
        "依次回答三个问题："
        "(1) 团队需要具备哪 5 项核心 AI 能力，按重要度排序；"
        "(2) 1500 万元预算如何在招聘 / 培训 / 工具 / 外部咨询这 4 项上分配，"
        "    用 calculator 工具给出每项的百分比并验证总和等于 100；"
        "(3) 6 个月分 3 个阶段的关键里程碑，每个阶段 2 个月。"
    )
    banner("业务问题（user_query）")
    log(user_query)

    # 4. 给 action 套一层：打印激活前后 blackboard 状态 + 计时
    _wrapped_actions = {a.name: a.action for a in engine.agents}

    def _traced_factory(name, inner):
        def _wrapped(blackboard, engine_):
            log()
            log(f"---- OODA step: 选中 {name} ----")
            log(f"  激活前 blackboard.facts = {list(blackboard.facts.keys())}")
            t = time.time()
            cmd = inner(blackboard, engine_)
            cost = time.time() - t
            log(f"  [{name}] 完成  cost={cost:.2f}s")
            log(f"  Command.goto={cmd.goto}  terminate={cmd.terminate}")
            log(f"  Command.update keys: {list(cmd.update.keys())}")
            if "facts" in cmd.update and isinstance(cmd.update["facts"], dict):
                for fk, fv in cmd.update["facts"].items():
                    log(f"    写入 {fk}: 共 {len(str(fv))} 字")
                    log(f"    预览: {str(fv)[:200]}{'...' if len(str(fv)) > 200 else ''}")
            return cmd
        return _wrapped

    for a in engine.agents:
        a.action = _traced_factory(a.name, _wrapped_actions[a.name])

    # 5. 启动 OODA 循环
    banner("启动 OODA 循环")
    t0 = time.time()
    try:
        blackboard = engine.run(
            user_query=user_query,
            strategy="priority",
            metadata={"priority": priority_map},
        )
    except Exception as exc:
        log(f"[FATAL] engine.run 抛异常：{exc}")
        logger.exception("engine.run 异常")
        return 2
    elapsed = time.time() - t0

    # 6. 黑板最终状态
    banner("OODA 循环结束 — 黑板最终状态")
    log(f"status         : {blackboard.status}")
    log(f"current_step   : {blackboard.current_step}")
    log(f"history len    : {len(blackboard.history)}")
    log(f"elapsed        : {elapsed:.2f}s")
    log()
    log("facts 概览：")
    for k, v in blackboard.facts.items():
        log(f"  - {k}: 共 {len(str(v))} 字")
    log()
    log("history 顺序：")
    for h in blackboard.history:
        if h.get("op") == "update":
            log(f"  step={h['step']:>2}  source={h['source']:<12}  key={h['key']}")

    # 7. 三段产出
    for key, label in [
        ("result::advisor", "顾问（advisor）的产出 — 能力模型"),
        ("result::strategist", "策略师（strategist）的产出 — 6 个月计划"),
        ("result::writer", "作家（writer）的最终交付 — 给 CEO 的咨询报告"),
    ]:
        banner(label)
        content = blackboard.facts.get(key, "（无）")
        log(content)

    # 8. KPI
    banner("KPI 校验")
    expectations = [
        ("status == 'solved'", blackboard.status == "solved"),
        ("facts 含 result::advisor", "result::advisor" in blackboard.facts),
        ("facts 含 result::strategist", "result::strategist" in blackboard.facts),
        ("facts 含 result::writer", "result::writer" in blackboard.facts),
        ("顺序 advisor → strategist → writer", _order(
            blackboard.history, "advisor", "strategist", "writer",
        )),
        ("writer 报告 > 500 字", len(str(blackboard.facts.get("result::writer", ""))) > 500),
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


def _order(history, *names) -> bool:
    def _first_idx(agent):
        # history 里 source 硬编码为 "command"，用 key 字段（result::<agent>）判断
        for i, h in enumerate(history):
            if h.get("op") == "update" and h.get("key") == f"result::{agent}":
                return i
        return -1

    indices = [_first_idx(n) for n in names]
    return all(i != -1 for i in indices) and indices == sorted(indices)


if __name__ == "__main__":
    sys.exit(main())
