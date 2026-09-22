from __future__ import annotations

import abc
from typing import Any

class Collector(abc.ABC):
    name = "collector"
    interval = 5.0
    priority = 50
    stale_after: float | None = None

    @property
    def effective_stale_after(self) -> float:
        return float(self.stale_after if self.stale_after is not None else max(5.0, self.interval * 4.0))

    @abc.abstractmethod
    def collect(self) -> dict[str, Any]:
        raise NotImplementedError

    def drain_events(self) -> list[dict[str, Any]]:
        return []
