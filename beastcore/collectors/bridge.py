from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .base import Collector


class BridgeCollector(Collector):
    """Read the tiny Pwnagotchi Beast Bridge state file from tmpfs.

    The file can be checked four times per second, but Pwnagotchi often leaves it
    unchanged between callbacks. Avoid repeatedly decoding identical JSON while
    retaining the same low-latency callback behavior.

    Bridge sequence numbers are scoped to one plugin instance. A Pwnagotchi or
    plugin restart may legitimately reset seq to zero, so an instance id is used
    when available instead of assuming seq is globally monotonic forever.
    """
    name = "bridge"
    interval = 0.25
    priority = 100
    stale_after = 8.0

    def __init__(self, path: str = "/run/beastagotchi/pwnagotchi_bridge.json") -> None:
        self.path = Path(path)
        self._events: list[dict[str, Any]] = []
        self._last_seq = 0
        self._instance_id: str | None = None
        self._last_updated_at = 0.0
        self._last_sig: tuple[int, int] | None = None
        self._cached_values: dict[str, Any] = {}

    def collect(self) -> dict[str, Any]:
        if not self.path.is_file():
            self._last_sig = None
            self._cached_values = {"pwnagotchi.bridge.state": "missing"}
            return dict(self._cached_values)
        st = self.path.stat()
        sig = (int(st.st_mtime_ns), int(st.st_size))
        if sig == self._last_sig and self._cached_values:
            return copy.deepcopy(self._cached_values)

        obj = json.loads(self.path.read_text(errors="replace"))
        values = dict(obj.get("state") or {})
        values["pwnagotchi.bridge.state"] = "available"
        if obj.get("updated_at") is not None:
            values["pwnagotchi.bridge.updated_at"] = obj["updated_at"]

        instance_id = str(obj.get("instance_id") or "").strip() or None
        try:
            updated_at = float(obj.get("updated_at") or 0.0)
        except Exception:
            updated_at = 0.0
        try:
            top_seq = int(obj.get("seq", 0) or 0)
        except Exception:
            top_seq = 0

        if instance_id:
            values["pwnagotchi.bridge.instance_id"] = instance_id
            if self._instance_id is not None and instance_id != self._instance_id:
                self._last_seq = 0
            self._instance_id = instance_id
        elif top_seq < self._last_seq and updated_at > self._last_updated_at:
            # Compatibility fallback for legacy bridge files that predate
            # instance_id. Atomic bridge writes make a backwards seq jump with a
            # newer timestamp a useful conservative restart signal.
            self._last_seq = 0

        events = obj.get("events") or []
        if isinstance(events, list):
            for ev in events:
                if not isinstance(ev, dict):
                    continue
                try:
                    seq = int(ev.get("seq", 0) or 0)
                except Exception:
                    seq = 0
                if seq > self._last_seq:
                    self._events.append(ev)
                    self._last_seq = max(self._last_seq, seq)
        # Compatibility with v0.1 bridge file.
        ev = obj.get("last_event")
        if isinstance(ev, dict):
            try:
                seq = int(ev.get("seq", 0) or 0)
            except Exception:
                seq = 0
            marker = seq or int(float(ev.get("ts", 0) or 0) * 1000)
            if marker > self._last_seq:
                e2 = dict(ev)
                e2["seq"] = marker
                self._events.append(e2)
                self._last_seq = marker

        self._last_updated_at = max(self._last_updated_at, updated_at)
        self._last_sig = sig
        self._cached_values = copy.deepcopy(values)
        return values

    def drain_events(self) -> list[dict[str, Any]]:
        out = self._events
        self._events = []
        return out
