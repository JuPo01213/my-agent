"""
experiments/2026-06-24-tool-scenario.py
======================================

目的：必触发工具调用的 ReAct 循环场景测试。
关键改进（相对 2026-06-24-scenario.py）：
  1. 包装 OpenAI client — 把每次 LLM 调用的**完整 request body** 与
     **完整 response body**（含 reasoning_content / tool_calls / finish_reason）
     以 JSON 原样打印到日志。
  2. 包装 TOOLS — 把每次工具调用的入参与返回值原样打印。
  3. 时间戳精确到毫秒，记录每个事件的发生顺序。

日志：experiments/2026-06-24-tool-scenario.log
"""
from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# 日志基础设施：写文件 + stderr，绕开 PowerShell `>` 只保留最后一行的 bug
# ---------------------------------------------------------------------------
LOG_FILE = PROJECT_ROOT / "experiments" / "2026-06-24-tool-scenario.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

_file_handler = logging.FileHandler(str(LOG_FILE), mode="w", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(message)s"))
logger = logging.getLogger("tool_scenario")
logger.setLevel(logging.INFO)
logger.handlers = [_file_handler, logging.StreamHandler(sys.stderr)]


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log(msg: str = "") -> None:
    logger.info(msg)


def banner(title: str) -> None:
    log()
    log("=" * 70)
    log(title)
    log("=" * 70)


# ---------------------------------------------------------------------------
# 1. 包装 OpenAI client：记录每次 chat.completions.create 的完整 body
# ---------------------------------------------------------------------------
class LoggingCompletions:
    """替代 client.chat.completions，捕获完整 request / response"""

    def __init__(self, real_completions: object, label: str):
        self._real = real_completions
        self._label = label
        self._counter = 0

    def create(self, **kwargs):
        self._counter += 1
        idx = self._counter

        # 请求体：序列化（保留中文，indent 2）
        try:
            req_dump = json.dumps(kwargs, ensure_ascii=False, indent=2, default=str)
        except Exception as exc:
            req_dump = f"<serialize failed: {exc}>"

        log()
        log(f"┌─[{self._label} #{idx}] LLM REQUEST @ {now()}")
        log("│ REQUEST BODY (完整原始 JSON):")
        for line in req_dump.splitlines():
            log(f"│   {line}")

        t0 = time.time()
        response = self._real.create(**kwargs)
        cost = time.time() - t0

        # 响应体：完整 dump（含 reasoning_content / tool_calls / finish_reason）
        try:
            resp_dump = response.model_dump()
        except Exception as exc:
            resp_dump = {"_serialize_error": str(exc), "_raw": str(response)}

        log(f"│")
        log(f"│ RESPONSE BODY @ {now()}  (cost={cost:.2f}s):")
        resp_str = json.dumps(resp_dump, ensure_ascii=False, indent=2, default=str)
        for line in resp_str.splitlines():
            log(f"│   {line}")
        log(f"└─[end of LLM CALL #{idx}]")
        return response


class LoggingChat:
    def __init__(self, real_chat: object, label: str):
        self.completions = LoggingCompletions(real_chat.completions, label)


class LoggingClient:
    """完整包装 OpenAI client"""

    def __init__(self, real_client: object):
        self._real = real_client
        self.chat = LoggingChat(real_client.chat, label="LLM")

    def __getattr__(self, name):
        return getattr(self._real, name)


# ---------------------------------------------------------------------------
# 2. 包装 TOOLS：记录每次工具调用的入参和返回值
# ---------------------------------------------------------------------------
def instrument_tools() -> None:
    """包装 agent_core.core.tool_registry.TOOLS 中每个工具"""
    from agent_core.core.tool_registry import TOOLS

    for name, tool in TOOLS.items():
        original = tool["func"]

        def make_wrapper(orig, tname):
            def wrapper(**kwargs):
                ts = now()
                log()
                log(f"┌─[TOOL CALL @ {ts}] {tname}")
                log(f"│ args  = {kwargs!r}")
                t0 = time.time()
                try:
                    result = orig(**kwargs)
                except Exception as exc:
                    cost = time.time() - t0
                    log(f"│ RAISED: {exc!r}  (cost={cost*1000:.1f}ms)")
                    log(f"└─[end TOOL CALL]")
                    raise
                cost = time.time() - t0
                log(f"│ return = {result!r}  (cost={cost*1000:.1f}ms)")
                log(f"└─[end TOOL CALL]")
                return result

            wrapper.__name__ = f"logged_{tname}"
            wrapper.__qualname__ = f"logged_{tname}"
            return wrapper

        tool["func"] = make_wrapper(original, name)


# ---------------------------------------------------------------------------
# 3. 主流程
# ---------------------------------------------------------------------------
def main() -> int:
    banner("工具调用场景实验 — ReAct 循环中的 Action / Observation 链路")

    # 必须在 import relationship 之前包装 TOOLS（因为 _call_tool 直接查 TOOLS 字典）
    instrument_tools()

    from openai import OpenAI
    from agent_core.config import STEPFUN_API_KEY, STEPFUN_BASE_URL, STEPFUN_MODEL
    from agent_core.multi_agent.relationship import RelationshipEngine

    raw_client = OpenAI(api_key=STEPFUN_API_KEY, base_url=STEPFUN_BASE_URL)
    client = LoggingClient(raw_client)

    log()
    log(f"[{now()}]  LLM 客户端已包装（LoggingClient）")
    log(f"  base_url : {STEPFUN_BASE_URL}")
    log(f"  model    : {STEPFUN_MODEL}")
    log(f"  log file : {LOG_FILE}")

    # YAML 加载
    agents_yaml = PROJECT_ROOT / "experiments" / "2026-06-24-tool-scenario.yaml"
    rels_yaml = PROJECT_ROOT / "experiments" / "2026-06-24-tool-scenario-relationships.yaml"

    log()
    log(f"[{now()}]  从 YAML 加载场景")
    log(f"  agents_yaml        : {agents_yaml}")
    log(f"  relationships_yaml : {rels_yaml}")

    engine = RelationshipEngine.from_yaml(
        client=client,
        model=STEPFUN_MODEL,
        agents_yaml_path=str(agents_yaml),
        relationships_yaml_path=str(rels_yaml),
    )
    priority_map = engine._relationships.get("priority", {})

    log()
    log(f"[{now()}]  已注册 Agent：")
    for a in engine.agents:
        log(f"  agent {a.name}: tools={a.tools}  max_iter={a.max_iter}  "
            f"action={a.action.__qualname__}")
    log(f"  priority_map : {priority_map}")

    # 用户问题：强制触发 calculator
    user_query = (
        "某 SaaS 公司 3 条产品线 2026 年 5 月的运营成本如下：\n"
        "  - 产品线 A：GPU 12.5 万元 + 人力 18.3 万元 + 工具订阅 3.2 万元\n"
        "  - 产品线 B：GPU 8.7 万元 + 人力 15.6 万元 + 工具订阅 2.8 万元\n"
        "  - 产品线 C：GPU 22.4 万元 + 人力 25.8 万元 + 工具订阅 5.6 万元\n"
        "该公司 5 月总营收 380 万元。\n"
        "\n"
        "请按以下步骤完成：\n"
        "1. 对每条产品线，用 calculator 工具分别计算：(a) GPU + 人力 + 工具 的月总成本\n"
        "2. 用 calculator 计算公司月度 AI 运营总成本（三条产品线之和）\n"
        "3. 用 calculator 计算 AI 成本占总营收的比例（百分比，保留 1 位小数）\n"
        "4. 用 get_time 工具获取报告生成时间\n"
        "5. 输出结构化数字。**所有数字必须经过 calculator 计算，禁止心算**。\n"
    )

    banner("业务问题（user_query）")
    log(user_query)

    # 给 action 套一层：打印激活时刻
    _wrapped_actions = {a.name: a.action for a in engine.agents}

    def _traced_factory(name, inner):
        def _wrapped(blackboard, engine_):
            log()
            log("█" * 70)
            log(f"[{now()}]  OODA → 激活 Agent: {name}")
            log(f"  激活前 facts keys = {list(blackboard.facts.keys())}")
            t = time.time()
            cmd = inner(blackboard, engine_)
            cost = time.time() - t
            log(f"[{now()}]  Agent {name} 完成  cost={cost:.2f}s")
            log(f"  Command.goto={cmd.goto}  terminate={cmd.terminate}")
            log(f"  Command.update keys: {list(cmd.update.keys())}")
            if "facts" in cmd.update and isinstance(cmd.update["facts"], dict):
                for fk, fv in cmd.update["facts"].items():
                    log(f"    写入 {fk}: {len(str(fv))} 字")
            log("█" * 70)
            return cmd
        return _wrapped

    for a in engine.agents:
        a.action = _traced_factory(a.name, _wrapped_actions[a.name])

    # 启动 OODA
    banner("启动 OODA 循环")
    log(f"[{now()}]  engine.run(strategy='priority', metadata={priority_map})")
    t0 = time.time()
    try:
        blackboard = engine.run(
            user_query=user_query,
            strategy="priority",
            metadata={"priority": priority_map},
        )
    except Exception as exc:
        log(f"[{now()}]  [FATAL] engine.run 抛异常：{exc}")
        logger.exception("engine.run 异常")
        return 2
    elapsed = time.time() - t0

    # 黑板最终状态
    banner("OODA 循环结束 — 黑板最终状态")
    log(f"[{now()}]  status         : {blackboard.status}")
    log(f"  current_step   : {blackboard.current_step}")
    log(f"  history len    : {len(blackboard.history)}")
    log(f"  elapsed        : {elapsed:.2f}s")
    log()
    log("facts 概览：")
    for k, v in blackboard.facts.items():
        log(f"  - {k}: {len(str(v))} 字")
    log()
    log("history 顺序：")
    for h in blackboard.history:
        if h.get("op") == "update":
            log(f"  step={h['step']:>2}  source={h['source']:<12}  key={h['key']}")

    # 三段产出
    for key, label in [
        ("result::analyst", "analyst 的最终产出 — 数字与计算"),
        ("result::writer",  "writer 的最终产出 — 给 CFO 的简报"),
    ]:
        banner(label)
        content = blackboard.facts.get(key, "（无）")
        log(content)

    # KPI
    banner("KPI 校验")
    expectations = [
        ("status == 'solved'",                       blackboard.status == "solved"),
        ("facts 含 result::analyst",                 "result::analyst" in blackboard.facts),
        ("facts 含 result::writer",                  "result::writer" in blackboard.facts),
        ("顺序 analyst → writer",                    _order(
            blackboard.history, "analyst", "writer",
        )),
        ("writer 报告 > 300 字",                     len(str(blackboard.facts.get("result::writer", ""))) > 300),
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
        for i, h in enumerate(history):
            if h.get("op") == "update" and h.get("key") == f"result::{agent}":
                return i
        return -1

    indices = [_first_idx(n) for n in names]
    return all(i != -1 for i in indices) and indices == sorted(indices)


if __name__ == "__main__":
    sys.exit(main())