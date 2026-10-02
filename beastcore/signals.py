from __future__ import annotations

from typing import Any

from .telemetry import TelemetryCatalog


_PRIVACY_PREFIXES: tuple[tuple[str, str, str], ...] = (
    ("gps.", "sensitive_location", "never"),
    ("wifi.", "local_operational", "never"),
    ("radio.", "local_operational", "never"),
    ("captures.", "sensitive_capture", "never"),
    ("peerdex.", "peer_identity", "policy"),
    ("progression.", "profile", "policy"),
    ("beast.", "profile", "policy"),
    ("expedition.", "activity", "policy"),
    ("system.", "local_system", "never"),
    ("power.", "local_system", "never"),
)

_HISTORY_PREFIXES = (
    "system.", "storage.", "radio.", "wifi.", "gps.", "power.",
    "pwnagotchi.", "expedition.", "performance.",
)

_STRUCTURED_HINTS = {
    "wifi.aps": "collection",
    "wifi.clients": "collection",
    "wifi.channel_activity": "series",
    "wifi.channel_history": "matrix",
    "gps.track": "route",
    "expedition.route_points": "route",
    "platform.services": "collection",
    "platform.hardware": "collection",
    "plugins.catalog": "collection",
}


def _value_type(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, (list, tuple)):
        return "array"
    return type(value).__name__


def _privacy_for(key: str) -> tuple[str, str]:
    for prefix, privacy, publication in _PRIVACY_PREFIXES:
        if key.startswith(prefix):
            return privacy, publication
    return "local", "never"


class SignalCatalog:
    """Typed presentation/integration metadata over canonical Beast state.

    A Signal is *not* a new collector or persistence layer.  Values and freshness
    remain owned by StateRegistry; descriptive labels/units reuse TelemetryCatalog.
    This contract exists so Scenes, Studio, Apps, Packs and external adapters can
    consume the same semantic metadata without learning collector internals.
    """

    schema = 1

    def __init__(self, state, telemetry: TelemetryCatalog | None = None) -> None:
        self.state = state
        self.telemetry = telemetry or TelemetryCatalog(state)

    def describe(self, key: str) -> dict[str, Any]:
        key = str(key or "").strip()
        row = self.telemetry.inspect(key)
        value = row.get("value")
        privacy, publication = _privacy_for(key)
        structure = _STRUCTURED_HINTS.get(key)
        if structure is None:
            structure = "scalar" if _value_type(value) in {"bool", "int", "float", "string", "unknown"} else "structured"

        return {
            "schema": self.schema,
            "signal": key,
            "label": row.get("label"),
            "category": row.get("category"),
            "unit": row.get("unit"),
            "kind": row.get("kind"),
            "cadence": row.get("cadence"),
            "value_type": _value_type(value),
            "structure": structure,
            "history_supported": key.startswith(_HISTORY_PREFIXES),
            "privacy": privacy,
            "publication": publication,
            "available": bool(row.get("available")),
            "quality": row.get("quality"),
            "source": row.get("source"),
            "updated_at": row.get("updated_at"),
            "age_sec": row.get("age_sec"),
            "error": row.get("error"),
            "priority": row.get("priority"),
            "seq": row.get("seq"),
            "value": value,
        }

    def snapshot(self, keys: list[str] | tuple[str, ...] | None = None, *, limit: int = 512) -> dict[str, Any]:
        if keys is None:
            selected = list(self.state.snapshot(False).keys())[: max(1, int(limit))]
        else:
            selected = [str(x) for x in list(keys)[: max(1, int(limit))]]
        items = [self.describe(key) for key in sorted(set(selected))]
        return {
            "schema": self.schema,
            "count": len(items),
            "available_count": sum(1 for row in items if row["available"]),
            "history_capable_count": sum(1 for row in items if row["history_supported"]),
            "items": items,
        }
