from __future__ import annotations

import time
from typing import Any


# Small explicit overrides plus conservative prefix inference.  This catalog is
# descriptive metadata only; it never fabricates a value.
EXPLICIT: dict[str, dict[str, Any]] = {
    "system.cpu.total": {"label": "CPU total", "unit": "%", "kind": "live", "cadence": "1s"},
    "system.temp.cpu_c": {"label": "CPU temperature", "unit": "C", "kind": "live", "cadence": "1s"},
    "system.memory.used_pct": {"label": "Memory used", "unit": "%", "kind": "live", "cadence": "1s"},
    "gps.latitude": {"label": "Latitude", "unit": "deg", "kind": "live", "cadence": "1s"},
    "gps.longitude": {"label": "Longitude", "unit": "deg", "kind": "live", "cadence": "1s"},
    "gps.speed_mps": {"label": "GPS speed", "unit": "m/s", "kind": "live", "cadence": "1s"},
    "gps.accuracy_m": {"label": "GPS accuracy", "unit": "m", "kind": "live", "cadence": "1s"},
    "wifi.ap_count": {"label": "Observed APs", "unit": "AP", "kind": "live", "cadence": "Bettercap scan"},
    "wifi.client_count": {"label": "Observed clients", "unit": "client", "kind": "live", "cadence": "Bettercap scan"},
    "wifi.channel_activity": {"label": "Channel activity", "unit": "observations", "kind": "derived_live", "cadence": "2s"},
    "wifi.channel_history": {"label": "Channel activity history", "unit": "observations", "kind": "derived_live", "cadence": "2s"},
    "expedition.distance_m": {"label": "Expedition distance", "unit": "m", "kind": "derived_persisted", "cadence": "1s"},
    "expedition.route_points": {"label": "Expedition route points", "unit": "point", "kind": "persisted", "cadence": "event"},
    "captures.total": {"label": "Capture total", "unit": "capture", "kind": "persisted", "cadence": "scan"},
    "governor.mode": {"label": "Resource mode", "unit": None, "kind": "derived_live", "cadence": "1s"},
}

PREFIXES: tuple[tuple[str, dict[str, Any]], ...] = (
    ("system.", {"category": "System", "kind": "live"}),
    ("storage.", {"category": "Storage", "kind": "live"}),
    ("radio.", {"category": "Radio", "kind": "live"}),
    ("wifi.", {"category": "Wi-Fi", "kind": "live"}),
    ("gps.", {"category": "GPS", "kind": "live"}),
    ("pwnagotchi.", {"category": "Pwnagotchi", "kind": "live"}),
    ("bettercap.", {"category": "Bettercap", "kind": "live"}),
    ("power.", {"category": "Power", "kind": "live"}),
    ("dock.", {"category": "Dock", "kind": "derived_live"}),
    ("context.", {"category": "Context", "kind": "derived_live"}),
    ("progression.", {"category": "Beast", "kind": "derived_persisted"}),
    ("rare.", {"category": "Beast", "kind": "derived_persisted"}),
    ("expedition.", {"category": "Expedition", "kind": "derived_persisted"}),
    ("plugins.", {"category": "Plugins", "kind": "derived_live"}),
    ("platform.plugins", {"category": "Plugins", "kind": "derived_live"}),
    ("capabilities.", {"category": "Hardware", "kind": "derived_live"}),
    ("health.", {"category": "Health", "kind": "derived_live"}),
    ("governor.", {"category": "Performance", "kind": "derived_live"}),
)


def _unit_for(key: str) -> str | None:
    k = key.lower()
    if k.endswith("_pct") or k.endswith(".percent") or "percent" in k:
        return "%"
    if k.endswith("_c") or ".temp." in k:
        return "C"
    if k.endswith("_m") or k.endswith(".distance_m") or k.endswith(".accuracy_m") or k.endswith(".altitude_m"):
        return "m"
    if k.endswith("_mps"):
        return "m/s"
    if k.endswith("_mph"):
        return "mph"
    if k.endswith("_v"):
        return "V"
    if k.endswith("_ma"):
        return "mA"
    if k.endswith("_w"):
        return "W"
    if k.endswith("_bytes") or k.endswith(".bytes"):
        return "bytes"
    if k.endswith("_sec") or k.endswith(".uptime_sec"):
        return "s"
    return None


def _label(key: str) -> str:
    tail = key.split(".")[-1].replace("_", " ")
    return tail.title()


class TelemetryCatalog:
    """Explain where every visible Beast value came from.

    The catalog is the foundation for Telemetry Inspector, Beast Studio data
    binding, confidence/freshness badges, and a hard rule that production
    widgets never substitute decorative fake measurements for unavailable data.
    """

    def __init__(self, state) -> None:
        self.state = state

    @staticmethod
    def schema_for(key: str) -> dict[str, Any]:
        out: dict[str, Any] = {"key": key, "label": _label(key), "unit": _unit_for(key), "category": "Other", "kind": "live"}
        for prefix, meta in PREFIXES:
            if key.startswith(prefix):
                out.update(meta)
                break
        out.update(EXPLICIT.get(key, {}))
        return out

    def inspect(self, key: str) -> dict[str, Any]:
        meta = self.state.meta(key)
        base = self.schema_for(key)
        now = time.time()
        if not meta:
            return {**base, "available": False, "value": None, "quality": "unavailable", "source": None,
                    "updated_at": None, "age_sec": None, "error": None}
        return {
            **base,
            "available": meta.get("quality") != "unavailable" and meta.get("value") is not None,
            "value": meta.get("value"),
            "quality": meta.get("quality"),
            "source": meta.get("source"),
            "updated_at": meta.get("updated_at"),
            "age_sec": round(max(0.0, now - float(meta.get("updated_at") or now)), 3),
            "error": meta.get("error"),
            "priority": meta.get("priority"),
            "seq": meta.get("seq"),
        }

    def snapshot(self, keys: list[str] | None = None) -> list[dict[str, Any]]:
        if keys is None:
            keys = list(self.state.snapshot(False).keys())
        return [self.inspect(str(k)) for k in sorted(set(keys))]
