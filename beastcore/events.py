from __future__ import annotations

import asyncio
import time
import uuid
from collections import deque
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Event:
    id: str
    ts: float
    type: str
    source: str
    severity: str
    data: dict[str, Any]


class EventBus:
    def __init__(self, history: int = 1500) -> None:
        self._history = deque(maxlen=history)
        self._subscribers: set[asyncio.Queue] = set()

    @staticmethod
    def is_transient(event_type: str) -> bool:
        return event_type in {"state.changed", "context.changed"}

    def publish(self, event_type: str, source: str, data: dict[str, Any] | None = None, severity: str = "info") -> Event:
        ev = Event(str(uuid.uuid4()), time.time(), event_type, source, severity, data or {})
        self._history.append(ev)
        for q in tuple(self._subscribers):
            try:
                q.put_nowait(ev)
            except asyncio.QueueFull:
                pass
        return ev

    def recent(self, limit: int = 100, include_transient: bool = True) -> list[dict[str, Any]]:
        items = list(self._history)
        if not include_transient:
            items = [e for e in items if not self.is_transient(e.type)]
        return [asdict(e) for e in items[-max(1, min(limit, 1000)):]]

    def subscribe(self, maxsize: int = 256) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.discard(q)
