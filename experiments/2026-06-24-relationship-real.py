"""
experiments/2026-06-24-relationship-real.py
==========================================

目的：用真实 LLM（StepFun step-3.7-flash）跑 relationship.py 的 3 Agent 协作，
验证代码走读文档"代码走读-relationship.py-2026-06-24.md"的预期是否符合实际。

运行方式：
    cd c:\\Users\\Administrator\\Desktop\\my-agent
    python experiments/2026-06-24-relationship-real.py

日志：所有输出会同步写入 experiments/2026-06-24-relationship-real.log
（避免 PowerShell > 重定向丢中间输出的问题）

凭据来源：agent_core/config.py（StepFun 默认配置）
"""
from __future__ import annotations

import logging
import sys
import time
import traceback
from pathlib import Path

# 路径：让脚本能直接运行
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 日志：写文件 + stderr
LOG_FILE = PROJECT_ROOT / "experiments" / "2026-06-24-relationship-real.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
_file_handler = logging.FileHandler(str(LOG_FILE), mode="w", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(message)s"))
logger = logging.getLogger("rel_real")
logger.setLevel(logging.INFO)
logger.handlers = [_file_handler, logging.StreamHandler(sys.stderr)]


def log(msg: str = "") -> None:
    """统一输出：写文件 + stderr。"""
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


def main() -> int:
    banner("关系驱动多 Agent 协作 — 真实 API 运行")
    log(f"base_url : {STEPFUN_BASE_URL}")
    log(f"model    : {STEPFUN_MODEL}")
    log(f"api_key  : {STEPFUN_API_KEY[:8]}...{STEPFUN_API_KEY[-4:]} (已脱敏)")

    # 1. 构造真实 LLM 客户端（OpenAI 兼容协议）
    client = OpenAI(
        api_key=STEPFUN_API_KEY,
        base_url=STEPFUN_BASE_URL,
    )

    # 2. 从 YAML 加载（与走读文档一致）
    config_dir = PROJECT_ROOT / "config"
    agents_yaml = config_dir / "agents.yaml"
    relationships_yaml = config_dir / "relationships.yaml"
    log(f"agents_yaml        : {agents_yaml}")
    log(f"relationships_yaml : {relationships_yaml}")

    engine = RelationshipEngine.from_yaml(
        client=client,
        model=STEPFUN_MODEL,
        agents_yaml_path=str(agents_yaml),
        relationships_yaml_path=str(relationships_yaml),
    )
    # 覆盖 max_iter=3 加快单 Agent 收敛（YAML 默认 8）
    for a in engine.agents:
        a.max_iter = 3
        log(f"  agent {a.name}: max_iter override -> 3")
    priority_map = engine._relationships.get("priority", {})
    log(f"loaded agents      : {[a.name for a in engine.agents]}")
    log(f"priority_map       : {priority_map}")

    # 给每个 agent 的 action 套一层计时打印
    _orig_actions = {a.name: a.action for a in engine.agents}

    def _timed_factory(name):
        def _wrapped(blackboard, engine_):
            log(f"  [run] start agent={name}")
            t = time.time()
            cmd = _orig_actions[name](blackboard, engine_)
            log(f"  [run] done  agent={name}  cost={time.time()-t:.2f}s")
            return cmd
        return _wrapped

    for a in engine.agents:
        a.action = _timed_factory(a.name)

    # 3. 跑协作（沿用走读文档的 user_query）
    user_query = "调研 2024 年 LLM Agent 领域的最新进展"
    banner(f"开始协作 — user_query = {user_query!r}")
    t0 = time.time()
    try:
        blackboard = engine.run(
            user_query=user_query,
            strategy="priority",
            metadata={"priority": priority_map},
        )
    except Exception as exc:
        log(f"[FATAL] engine.run 抛异常：{exc}")
        traceback.print_exc(file=sys.stderr)
        logger.exception("engine.run 异常")
        return 2
    elapsed = time.time() - t0

    # 4. 打印黑板摘要
    banner("黑板最终状态")
    log(f"status         : {blackboard.status}")
    log(f"current_step   : {blackboard.current_step}")
    log(f"history len    : {len(blackboard.history)}")
    log(f"elapsed        : {elapsed:.2f}s")
    log()
    log("facts:")
    for k, v in blackboard.facts.items():
        v_str = str(v)
        v_str_short = v_str[:120] + "..." if len(v_str) > 120 else v_str
        log(f"  - {k}: {v_str_short}")
    log()
    log("history (op/source/key):")
    for h in blackboard.history:
        if h.get("op") == "update":
            log(f"  step={h['step']:>2}  {h['source']:<12}  ->  {h['key']}")
        else:
            log(f"  step={h['step']:>2}  {h['source']:<12}  op={h['op']}")

    # 5. 打印最终报告
    banner("最终报告（result::writer）")
    final = blackboard.facts.get("result::writer", "（无）")
    log(final)

    # 6. KPI 校验
    banner("走读文档预期 vs 实际")
    expectations = [
        ("status == 'solved'", blackboard.status == "solved"),
        ("facts 含 result::researcher", "result::researcher" in blackboard.facts),
        ("facts 含 result::analyst", "result::analyst" in blackboard.facts),
        ("facts 含 result::writer", "result::writer" in blackboard.facts),
        (
            "history 中 researcher 出现在 analyst 之前",
            _order(blackboard.history, "researcher", "analyst"),
        ),
        (
            "history 中 analyst 出现在 writer 之前",
            _order(blackboard.history, "analyst", "writer"),
        ),
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


def _order(history: list, first: str, second: str) -> bool:
    """检查 history 中 first 的 update 出现在 second 之前。"""
    def _first_update_idx(agent: str) -> int:
        for i, h in enumerate(history):
            if h.get("source") == agent and h.get("op") == "update":
                return i
        return -1

    fi, si = _first_update_idx(first), _first_update_idx(second)
    return fi != -1 and si != -1 and fi < si


if __name__ == "__main__":
    sys.exit(main())
