from __future__ import annotations

import copy
import time
from collections import deque
from typing import Any, Callable


class ChannelActivityEngine:
    """Build a truthful rolling Wi-Fi channel history from Bettercap AP data.

    This is intentionally *not* a spectrum analyzer: the current Wi-Fi hardware
    supplies observed AP/client/RSSI metadata, not raw RF power.  Beast keeps the
    semantics explicit so a heatmap/waterfall can be visually rich without
    pretending to be hardware it is not.
    """

    def __init__(self, state, *, max_snapshots: int = 180,
                 clock: Callable[[], float] = time.time) -> None:
        self.state = state
        self.clock = clock
        self.history: deque[dict[str, Any]] = deque(maxlen=max(8, int(max_snapshots)))
        self._last_signature: tuple | None = None

    @staticmethod
    def _channel(ap: dict[str, Any]) -> int | None:
        try:
            ch = int(ap.get("channel"))
            return ch if ch > 0 else None
        except Exception:
            return None

    @staticmethod
    def _rssi(ap: dict[str, Any]) -> float | None:
        try:
            return float(ap.get("rssi"))
        except Exception:
            return None

    @staticmethod
    def _is_open(ap: dict[str, Any]) -> bool:
        enc = str(ap.get("encryption") or ap.get("security") or "").strip().lower()
        return enc in {"", "open", "none", "unencrypted"}

    @staticmethod
    def _is_hidden(ap: dict[str, Any]) -> bool:
        ssid = str(ap.get("hostname") or ap.get("ssid") or "").strip()
        return not ssid or ssid.lower() in {"<hidden>", "hidden"}

    def current(self) -> list[dict[str, Any]]:
        aps = self.state.get("wifi.aps", []) or []
        channels: dict[int, dict[str, Any]] = {}
        if isinstance(aps, list):
            for ap in aps:
                if not isinstance(ap, dict):
                    continue
                ch = self._channel(ap)
                if ch is None:
                    continue
                row = channels.setdefault(ch, {
                    "channel": ch,
                    "ap_count": 0,
                    "client_count": 0,
                    "strongest_rssi": None,
                    "hidden_count": 0,
                    "open_count": 0,
                })
                row["ap_count"] += 1
                clients = ap.get("clients") or []
                if isinstance(clients, list):
                    row["client_count"] += len(clients)
                rssi = self._rssi(ap)
                if rssi is not None:
                    prev = row["strongest_rssi"]
                    row["strongest_rssi"] = rssi if prev is None else max(float(prev), rssi)
                if self._is_hidden(ap):
                    row["hidden_count"] += 1
                if self._is_open(ap):
                    row["open_count"] += 1
        return [channels[k] for k in sorted(channels)]

    @staticmethod
    def _signature(rows: list[dict[str, Any]]) -> tuple:
        return tuple(
            (r.get("channel"), r.get("ap_count"), r.get("client_count"),
             r.get("strongest_rssi"), r.get("hidden_count"), r.get("open_count"))
            for r in rows
        )

    def tick(self) -> dict[str, Any]:
        now = float(self.clock())
        rows = self.current()
        signature = self._signature(rows)
        # A sample is still recorded when unchanged: a waterfall should show
        # that the environment remained stable rather than compressing time.
        snap = {"ts": now, "channels": copy.deepcopy(rows)}
        self.history.append(snap)
        changed = signature != self._last_signature
        self._last_signature = signature
        return {
            "wifi.channel_activity": rows,
            "wifi.channel_activity.updated_at": now,
            "wifi.channel_activity.channels_seen": len(rows),
            "wifi.channel_activity.changed": changed,
            "wifi.channel_activity.semantics": "observed_ap_activity",
        }

    def recent(self, limit: int = 90) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), len(self.history) or 1))
        return [copy.deepcopy(x) for x in list(self.history)[-limit:]]
