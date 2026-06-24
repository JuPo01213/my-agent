"""
agent_core.frontend.bus - 事件总线
====================================

**职责**：聚合 + 缓存事件，供前端/测试/SSE 适配器使用。

**不依赖**：任何网络库（sse-starlette / flask / fastapi 都只是上层消费者）。

**典型用法**：

```python
from agent_core.frontend import EventBus

bus = EventBus()
engine.run(user_query="...", on_event=bus.emit)
# 跑完后可以拿完整事件流
for ev in bus.events:
    print(ev)
```
"""
from __future__ import annotations

from typing import Any, Callable


class EventBus:
    """
    简单事件总线：把核心层 on_event 调用聚合成可消费的列表。

    设计原则：
    - 同步 emit（核心层就是同步的，不引入异步复杂度）
    - 缓存所有事件，便于离线分析 / 单元测试
    - 可注入 sink：把事件流同步到 stdout / 文件 / SSE
    """

    def __init__(self, sink: Callable[[dict], None] | None = None) -> None:
        self.events: list[dict[str, Any]] = []
        self._sink = sink

    def emit(self, event: dict[str, Any]) -> None:
        """核心层 on_event 的实现。缓存 + 可选 sink。"""
        self.events.append(event)
        if self._sink is not None:
            self._sink(event)

    def clear(self) -> None:
        self.events = []

    def by_type(self, event_type: str) -> list[dict[str, Any]]:
        """按 type 过滤事件。"""
        return [e for e in self.events if e.get("type") == event_type]

    def count(self, event_type: str) -> int:
        return sum(1 for e in self.events if e.get("type") == event_type or e.get("kind") == event_type)

    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self):
        return iter(self.events)


__all__ = ["EventBus"]
