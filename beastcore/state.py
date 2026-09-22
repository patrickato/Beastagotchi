from __future__ import annotations

import copy
import threading
import time
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class StateValue:
    value: Any
    source: str
    updated_at: float
    quality: str = "live"
    error: str | None = None
    seq: int = 0
    priority: int = 0

class StateRegistry:
    """Thread-safe canonical flat-key state registry with source priority and freshness."""
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._values: dict[str, StateValue] = {}
        self._seq = 0

    def update_many(self, source: str, values: dict[str, Any], quality: str = "live", priority: int = 0) -> list[tuple[str, Any, Any]]:
        changed: list[tuple[str, Any, Any]] = []
        now = time.time()
        with self._lock:
            for key, value in values.items():
                old = self._values.get(key)
                # Prefer higher-priority live sources. Lower-priority sources may take over only
                # when the current value is stale/unavailable.
                if old is not None and priority < old.priority and old.quality == "live" and not old.error:
                    continue
                old_value = old.value if old else None
                if old is None or old_value != value or old.error or old.quality != quality or old.priority != priority:
                    self._seq += 1
                    self._values[key] = StateValue(copy.deepcopy(value), source, now, quality, None, self._seq, priority)
                    changed.append((key, old_value, value))
                else:
                    old.updated_at = now
                    old.quality = quality
                    old.source = source
                    old.priority = priority
        return changed

    def set_error(self, source: str, key: str, message: str, priority: int = 0) -> None:
        now = time.time()
        with self._lock:
            old = self._values.get(key)
            value = old.value if old else None
            self._seq += 1
            self._values[key] = StateValue(value, source, now, "stale" if old else "unavailable", message, self._seq, priority)

    def mark_source_stale(self, source: str, older_than: float) -> list[str]:
        now = time.time()
        marked: list[str] = []
        with self._lock:
            for key, item in self._values.items():
                if item.source != source or item.quality != "live":
                    continue
                if now - item.updated_at >= older_than:
                    self._seq += 1
                    item.quality = "stale"
                    item.seq = self._seq
                    marked.append(key)
        return marked

    def snapshot(self, include_meta: bool = True) -> dict[str, Any]:
        with self._lock:
            if include_meta:
                return {k: asdict(v) for k, v in sorted(self._values.items())}
            return {k: copy.deepcopy(v.value) for k, v in sorted(self._values.items())}

    def snapshot_keys(self, keys: list[str], include_meta: bool = False) -> dict[str, Any]:
        with self._lock:
            out = {}
            for key in keys:
                v = self._values.get(key)
                if v is None:
                    continue
                out[key] = asdict(v) if include_meta else copy.deepcopy(v.value)
            return out

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            value = self._values.get(key)
            return copy.deepcopy(value.value) if value else default

    def meta(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            value = self._values.get(key)
            return asdict(value) if value else None

    def stats(self) -> dict[str, Any]:
        now = time.time()
        with self._lock:
            live = stale = unavailable = 0
            oldest_age = 0.0
            for v in self._values.values():
                if v.quality == "live": live += 1
                elif v.quality == "stale": stale += 1
                else: unavailable += 1
                oldest_age = max(oldest_age, now - v.updated_at)
            return {
                "keys": len(self._values),
                "live": live,
                "stale": stale,
                "unavailable": unavailable,
                "oldest_age_sec": round(oldest_age, 3),
                "seq": self._seq,
            }
