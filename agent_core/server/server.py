"""
agent_core.server - FastAPI 后端服务
======================================

职责：
1. 提供前端页面访问入口
2. 提供配置读取/保存 API（agents.yaml / relationships.yaml）
3. 提供多 Agent 运行 + SSE 事件流 API

启动方式：
    python agent_core/server/run.py
或
    uvicorn agent_core.server.server:app --host 0.0.0.0 --port 8000

访问：
    http://localhost:8000/
"""
from __future__ import annotations

import json
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from agent_core.config import get_provider
from agent_core.frontend import EventBus
from agent_core.multi_agent.relationship import (
    Blackboard,
    Command,
    ControlShell,
    KnowledgeSource,
    RelationshipEngine,
)


# ============================================================
# 基础配置
# ============================================================

ROOT = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = ROOT / "agent_core" / "static"
AGENTS_YAML = ROOT / "config" / "agents.yaml"
RELATIONSHIPS_YAML = ROOT / "config" / "relationships.yaml"

# 运行状态存储（内存，单进程）
RUNS: dict[str, dict[str, Any]] = {}
RUN_LOCK = threading.Lock()


# ============================================================
# FastAPI 应用
# ============================================================

app = FastAPI(title="My Agent Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ============================================================
# 工具函数
# ============================================================

def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )


def _build_knowledge_source(name: str, cfg: dict[str, Any]) -> KnowledgeSource:
    """根据前端/API 传入的配置字典构建 KnowledgeSource。"""
    preconditions_expr = cfg.get("preconditions", "True")
    if preconditions_expr in (None, "", "True", True):
        preconditions = None
    else:
        # 通过闭包固定当前表达式，避免 lambda 晚期绑定问题
        expr = str(preconditions_expr)
        preconditions = lambda snap, e=expr: _eval_precondition(snap, e)

    return KnowledgeSource(
        name=name,
        role=cfg.get("role", name),
        goal=cfg.get("goal", ""),
        backstory=cfg.get("backstory", ""),
        tools=cfg.get("tools") or [],
        max_iter=int(cfg.get("max_iter", 8) or 8),
        preconditions=preconditions,
    )


def _eval_precondition(snap: dict, expr: str) -> bool:
    """安全子集表达式解析：仅支持 True/False 与 facts.has(...)。"""
    expr = expr.strip()
    if expr in {"True", "true"}:
        return True
    if expr in {"False", "false"}:
        return False

    m = re_precondition.match(expr)
    if m:
        key = m.group(1).strip("'\"")
        return key in snap.get("facts", {})

    return False


# 预编译正则，避免每次调用都编译
import re as _re
re_precondition = _re.compile(r"^facts\.has\(['\"](.*?)['\"]\)$")


def _run_pipeline_in_thread(run_id: str, payload: dict[str, Any]) -> None:
    """后台线程：执行多 Agent 流水线，将事件写入 RUNS[run_id]['events']。"""
    bus = EventBus()
    run_record: dict[str, Any] = {}

    try:
        api_key, base_url, model = get_provider()
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)

        agents_cfg = payload.get("agents", {})
        relationships_cfg = payload.get("relationships", {})
        strategy = payload.get("strategy", "first_match")
        max_steps = int(payload.get("max_steps", 50) or 50)
        user_query = payload.get("user_query", "")

        # 构造 agents
        agents = []
        for name, cfg in agents_cfg.items():
            agents.append(_build_knowledge_source(name, cfg))

        # 构造 priority 映射
        priority_map = {}
        for name, val in (relationships_cfg.get("priority") or {}).items():
            try:
                priority_map[name] = int(val)
            except (TypeError, ValueError):
                pass

        # 构造 termination 表达式
        termination_exprs = relationships_cfg.get("termination") or []
        def _done_when(blackboard: Blackboard) -> bool:
            for expr in termination_exprs:
                if _eval_precondition(blackboard.snapshot(), expr):
                    return True
            return False

        engine = RelationshipEngine(
            client=client,
            model=model,
            agents=agents,
            max_steps=max_steps,
        )

        # 记录启动时间
        started_at = time.time()

        # 预置 user.input，确保事件流按时间顺序可消费
        from agent_core.frontend.events import make_user_input, make_run_done
        user_input_event = make_user_input(run_id, user_query)
        with RUN_LOCK:
            RUNS[run_id].setdefault('events', []).append(user_input_event)

        # 实时 on_event：同步写入 RUNS，避免全部堆积到结束时一次性返回
        def _on_event(event: dict[str, Any]) -> None:
            bus.emit(event)
            with RUN_LOCK:
                RUNS[run_id].setdefault('events', []).append(event)

        blackboard = engine.run(
            user_query=user_query,
            strategy=strategy,
            metadata={"priority": priority_map},
            done_when=_done_when,
            on_event=_on_event,
        )
        ended_at = time.time()

        # 末尾补充 run.done
        done_event = make_run_done(
            run_id=run_id,
            status=blackboard.status,
            summary={"elapsed_s": round(ended_at - started_at, 3)},
        )
        with RUN_LOCK:
            RUNS[run_id].setdefault('events', []).append(done_event)

        # DEBUG
        import sys
        print(f"[DEBUG] bus.events count: {len(bus.events)}", file=sys.stderr)
        print(f"[DEBUG] final events count: {len(RUNS[run_id].get('events', []))}", file=sys.stderr)

        run_record = {
            "status": "done",
            "blackboard": {
                "status": blackboard.status,
                "facts": dict(blackboard.facts),
                "current_step": blackboard.current_step,
            },
            "events": RUNS[run_id].get('events', []),
            "error": None,
        }

    except Exception as exc:  # noqa: BLE001
        run_record = {
            "status": "error",
            "blackboard": {},
            "events": bus.events,
            "error": str(exc),
        }

    with RUN_LOCK:
        RUNS[run_id].update(run_record)


# ============================================================
# 页面路由
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    index_path = STATIC_DIR / "bubble.html"
    return index_path.read_text(encoding="utf-8")


# ============================================================
# 配置 API
# ============================================================

@app.get("/api/config/agents")
async def get_agents_config() -> JSONResponse:
    data = _load_yaml(AGENTS_YAML)
    return JSONResponse({"data": data})


@app.post("/api/config/agents")
async def save_agents_config(body: dict[str, Any]) -> JSONResponse:
    _save_yaml(AGENTS_YAML, body)
    return JSONResponse({"ok": True})


@app.get("/api/config/relationships")
async def get_relationships_config() -> JSONResponse:
    data = _load_yaml(RELATIONSHIPS_YAML)
    return JSONResponse({"data": data})


@app.post("/api/config/relationships")
async def save_relationships_config(body: dict[str, Any]) -> JSONResponse:
    _save_yaml(RELATIONSHIPS_YAML, body)
    return JSONResponse({"ok": True})


# ============================================================
# 运行 + SSE 事件流
# ============================================================

@app.post("/api/run")
async def start_run(body: dict[str, Any]) -> JSONResponse:
    run_id = uuid.uuid4().hex
    with RUN_LOCK:
        RUNS[run_id] = {
            "status": "running",
            "blackboard": {},
            "events": [],
            "error": None,
        }

    t = threading.Thread(
        target=_run_pipeline_in_thread,
        args=(run_id, body),
        daemon=True,
    )
    t.start()

    return JSONResponse({"run_id": run_id})


@app.get("/api/runs/{run_id}/events")
async def stream_events(run_id: str):
    """SSE 流：有新事件就推送，结束时推送 [DONE]。"""
    async def event_generator():
        last_index = 0
        for _ in range(600):  # 最多等 10 分钟
            with RUN_LOCK:
                run = RUNS.get(run_id)
            if run is None:
                yield {"event": "error", "data": json.dumps({"message": "run_id not found"})}
                return

            events = run.get("events", [])
            while last_index < len(events):
                evt = events[last_index]
                last_index += 1
                yield {"event": "message", "data": json.dumps(evt)}

            if run.get("status") in ("done", "error"):
                yield {"event": "done", "data": json.dumps({
                    "status": run["status"],
                    "blackboard": run.get("blackboard", {}),
                    "error": run.get("error"),
                })}
                return

            await asyncio_sleep(0.5)

        yield {"event": "error", "data": json.dumps({"message": "timeout waiting for run to finish"})}

    return EventSourceResponse(event_generator())


@app.get("/api/runs/{run_id}/result")
async def get_run_result(run_id: str) -> JSONResponse:
    with RUN_LOCK:
        run = RUNS.get(run_id)
    if not run:
        return JSONResponse({"error": "run_id not found"}, status_code=404)
    return JSONResponse({
        "status": run.get("status"),
        "blackboard": run.get("blackboard", {}),
        "error": run.get("error"),
    })


# ============================================================
# asyncio sleep（避免顶部 import 报错）
# ============================================================

async def asyncio_sleep(seconds: float) -> None:
    import asyncio
    await asyncio.sleep(seconds)
