"""智能体前端控制台（纯 Python 标准库实现，无需额外依赖）"""

from __future__ import annotations

import json
import queue
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from react_agent import run_react_loop_stream, get_llm_client
from config import STEPFUN_MODEL, get_provider, get_provider_config

# ---------------------------------------------------------------------------
# 运行状态管理
# ---------------------------------------------------------------------------


class Run:
    """一次智能体运行的完整状态。"""

    def __init__(self, run_id: str, user_input: str, model: str, provider: str = "stepfun"):
        self.id = run_id
        self.user_input = user_input
        self.model = model
        self.provider = provider
        self.queue: queue.Queue[dict] = queue.Queue()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.client = _get_client_for_provider(provider)


runs: dict[str, Run] = {}
run_id_counter = 0
run_id_lock = threading.Lock()


def _next_run_id() -> str:
    global run_id_counter
    with run_id_lock:
        run_id_counter += 1
        return f"run-{run_id_counter:04d}"


def _get_client_for_provider(provider: str) -> Any:
    try:
        api_key, base_url, _model = get_provider_config(provider)
    except RuntimeError:
        api_key, base_url, _model = get_provider_config("stepfun")
    return get_llm_client(api_key, base_url)


# ---------------------------------------------------------------------------
# HTTP / SSE 服务
# ---------------------------------------------------------------------------


SCRIPT_DIR = Path(__file__).resolve().parent
STATIC_DIR = SCRIPT_DIR / "static"


class DashboardHandler(SimpleHTTPRequestHandler):
    """极简仪表板：提供前端页面、启动运行、SSE 推送日志。"""

    server_version = "AgentDashboard/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        elif path == "/" or path == "/index.html":
            self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
        elif path == "/vue" or path == "/vue.html":
            self._serve_file(STATIC_DIR / "vue.html", "text/html; charset=utf-8")
        elif path.startswith("/static/"):
            # 回退到标准库的文件服务
            super().do_GET()
        elif path == "/stream":
            self._handle_stream(qs.get("id", [""])[0])
        else:
            self.send_error(404, "Not Found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/run":
            self._handle_run(qs.get("model", [""])[0], qs)
        elif path == "/stop":
            self._handle_stop(qs.get("id", [""])[0])
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):  # noqa: A002
        try:
            text = (format % args) if args else str(format)
        except Exception:
            text = str(format)
        if "404" in text:
            sys.stderr.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), text))

    # ------------------------------------------------------------------
    # 静态文件
    # ------------------------------------------------------------------

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "File Not Found")
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ------------------------------------------------------------------
    # 业务接口
    # ------------------------------------------------------------------

    def _handle_run(self, model_override: str, qs: dict[str, list[str]]) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        user_input = (payload.get("input") or "").strip()
        if not user_input:
            self.send_error(400, "Missing input")
            return

        run_id = _next_run_id()
        provider = (qs.get("provider", [""])[0] or payload.get("provider", "") or "stepfun").strip() or "stepfun"
        model = model_override or payload.get("model", "") or STEPFUN_MODEL
        run = Run(run_id=run_id, user_input=user_input, model=model, provider=provider)
        runs[run_id] = run

        def _target() -> None:
            try:
                run_react_loop_stream(
                    user_input=run.user_input,
                    client=run.client,
                    model=run.model,
                    on_event=run.queue.put,
                    stop_event=run.stop_event,
                )
            except Exception as exc:  # pragma: no cover - 防护边界
                run.queue.put({"type": "error", "content": f"运行异常：{exc}"})
            finally:
                run.queue.put({"type": "end"})

        run.thread = threading.Thread(target=_target, daemon=True)
        run.thread.start()

        self._json_response(200, {"id": run_id, "status": "running"})

    def _handle_stop(self, run_id: str) -> None:
        run = runs.get(run_id)
        if not run:
            self._json_response(404, {"error": "run not found"})
            return
        run.stop_event.set()
        self._json_response(200, {"status": "stopping"})

    def _handle_stream(self, run_id: str) -> None:
        run = runs.get(run_id)
        if not run:
            self.send_error(404, "Run Not Found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        alive = True
        while alive:
            try:
                event = run.queue.get(timeout=0.5)
            except queue.Empty:
                if run.thread is not None and not run.thread.is_alive() and run.queue.empty():
                    break
                continue

            payload = json.dumps(event, ensure_ascii=False)
            try:
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                break

            if event.get("type") in {"final", "stopped", "end"}:
                alive = False

        # 清理历史运行（防止内存泄漏）
        with run_id_lock:
            if run_id in runs and runs[run_id].thread is not None and not runs[run_id].thread.is_alive():
                del runs[run_id]

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _json_response(self, code: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


# ---------------------------------------------------------------------------
# 启动入口
# ---------------------------------------------------------------------------


def main() -> None:
    host = "127.0.0.1"
    port = 8080
    try:
        _api_key, _base_url, default_model = get_provider()
    except RuntimeError:
        default_model = STEPFUN_MODEL
    server = HTTPServer((host, port), DashboardHandler)
    print("=" * 60)
    print("  ReAct 智能体控制台已启动")
    print(f"  请打开浏览器访问：http://{host}:{port}")
    print(f"  按 Ctrl+C 停止服务")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n正在停止服务...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
