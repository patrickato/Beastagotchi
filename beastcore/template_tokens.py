from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any


_TOKEN_RE = re.compile(r"\{([A-Za-z0-9_.-]{1,64})\}")


@dataclass(frozen=True)
class TokenSpec:
    """Declarative mapping from a presentation token to canonical Beast state.

    Tokens are presentation/configuration helpers only. They never poll hardware
    or become a second source of truth; every value comes from StateRegistry.
    """

    token: str
    state_key: str
    description: str
    format_kind: str = "text"
    unit: str | None = None
    privacy: str = "local"
    publication: str = "never"
    update_class: str = "live"
    aliases: tuple[str, ...] = ()


def _specs() -> tuple[TokenSpec, ...]:
    return (
        TokenSpec("system.temp", "system.temp.cpu_c", "CPU temperature", "temp_c", "C", aliases=("temp",)),
        TokenSpec("system.cpu", "system.cpu.total", "Total CPU utilization", "percent", "%", aliases=("cpu",)),
        TokenSpec("system.memory", "system.memory.used_pct", "System memory utilization", "percent", "%", aliases=("ram", "memory")),
        TokenSpec("system.health", "health.core.state", "Beast Core health", aliases=("health",)),
        TokenSpec("system.governor", "governor.mode", "Resource Governor mode", aliases=("governor",)),
        TokenSpec("wifi.aps", "wifi.ap_count", "Currently observed access points", "int", aliases=("aps",)),
        TokenSpec("wifi.clients", "wifi.client_count", "Currently observed clients", "int", aliases=("clients",)),
        TokenSpec("radio.channel", "radio.primary.channel", "Primary radio channel", "int", aliases=("channel",)),
        TokenSpec("captures.total", "captures.total", "Stored capture records", "int", publication="policy"),
        TokenSpec("captures.handshakes", "pwnagotchi.handshakes", "Current Pwnagotchi handshake count", "int", aliases=("handshakes",)),
        TokenSpec("gps.fix", "gps.fix", "GPS fix state", "fix", aliases=("gps",)),
        TokenSpec("gps.sats", "gps.satellites_used", "Satellites used in current fix", "int", aliases=("sats",)),
        TokenSpec("power.battery", "power.battery.percent_estimate", "Estimated UPS battery percentage", "percent", "%", aliases=("battery",)),
        TokenSpec("dock.state", "dock.state", "Current dock/field state", aliases=("dock",)),
        TokenSpec("context.mode", "context.mode.effective", "Effective Beast operating context", aliases=("mode",)),
        TokenSpec("beast.name", "progression.beast.name", "Active Beast name", privacy="profile", publication="policy", aliases=("name",)),
        TokenSpec("beast.kind", "progression.beast.kind", "Active creature kind", privacy="profile", publication="policy"),
        TokenSpec("beast.level", "progression.level", "Active Beast level", "int", privacy="profile", publication="policy", aliases=("level",)),
        TokenSpec("beast.stage", "progression.stage", "Active Beast evolution stage", privacy="profile", publication="policy", aliases=("stage",)),
        TokenSpec("beast.aura", "progression.aura", "Active Beast session aura", privacy="profile", publication="policy", aliases=("aura",)),
        TokenSpec("beast.mood", "pwnagotchi.mood", "Current Beast/Pwnagotchi mood", privacy="profile", publication="policy", aliases=("mood",)),
        TokenSpec("expedition.active", "expedition.active", "Whether an Expedition is active", "bool", publication="policy"),
        TokenSpec("expedition.distance", "expedition.distance_m", "Current Expedition distance", "distance", "m", publication="policy"),
        TokenSpec("expedition.aps", "expedition.ap_unique", "Unique APs observed this Expedition", "int", publication="policy"),
        TokenSpec("expedition.captures", "expedition.captures_delta", "Captures added this Expedition", "int", publication="policy"),
        TokenSpec("peers.total", "peerdex.total_peers", "Persistent PeerDex peer count", "int", publication="policy", aliases=("peers",)),
    )


class TemplateTokenRegistry:
    """Lazy, bounded presentation tokens backed only by canonical Beast state.

    This is intentionally a neutral service. Beast UI, Studio, Packs and a future
    Theme Manager adapter can all consume it without creating new telemetry
    pollers or importing one another's renderer.
    """

    schema = 1
    unavailable_text = "--"

    def __init__(self, state, *, clock=time.time) -> None:
        self.state = state
        self.clock = clock
        self._specs = {spec.token: spec for spec in _specs()}
        self._aliases: dict[str, str] = {}
        for spec in self._specs.values():
            for alias in spec.aliases:
                self._aliases[alias] = spec.token

    @staticmethod
    def _normalize(token: str) -> str:
        token = str(token or "").strip()
        if token.startswith("{") and token.endswith("}"):
            token = token[1:-1].strip()
        return token.lower()

    def canonical_name(self, token: str) -> str | None:
        name = self._normalize(token)
        if name in self._specs:
            return name
        return self._aliases.get(name)

    @staticmethod
    def _number(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _format(self, spec: TokenSpec, value: Any) -> str:
        if value is None:
            return self.unavailable_text
        kind = spec.format_kind
        if kind == "int":
            try:
                return str(int(round(float(value))))
            except (TypeError, ValueError):
                return self.unavailable_text
        if kind == "percent":
            n = self._number(value)
            return self.unavailable_text if n is None else f"{n:.0f}%"
        if kind == "temp_c":
            n = self._number(value)
            return self.unavailable_text if n is None else f"{n:.1f}C"
        if kind == "distance":
            n = self._number(value)
            if n is None:
                return self.unavailable_text
            if abs(n) >= 1000:
                return f"{n / 1000.0:.2f} km"
            return f"{n:.0f} m"
        if kind == "fix":
            return "FIX" if bool(value) else "NO FIX"
        if kind == "bool":
            return "YES" if bool(value) else "NO"
        return str(value)

    def catalog(self) -> list[dict[str, Any]]:
        rows = []
        for spec in sorted(self._specs.values(), key=lambda row: row.token):
            rows.append({
                "token": spec.token,
                "state_key": spec.state_key,
                "description": spec.description,
                "format": spec.format_kind,
                "unit": spec.unit,
                "privacy": spec.privacy,
                "publication": spec.publication,
                "update_class": spec.update_class,
                "aliases": list(spec.aliases),
            })
        return rows

    def resolve(self, token: str) -> dict[str, Any]:
        requested = self._normalize(token)
        canonical = self.canonical_name(requested)
        if canonical is None:
            return {
                "requested": requested,
                "token": None,
                "known": False,
                "status": "unknown",
                "value": None,
                "text": self.unavailable_text,
                "reason": "token is not allow-listed",
            }

        spec = self._specs[canonical]
        meta = self.state.meta(spec.state_key) or {}
        value = self.state.get(spec.state_key)
        quality = str(meta.get("quality") or "")
        error = meta.get("error")
        if not meta or value is None:
            status = "unavailable"
        elif quality in {"stale", "unavailable"}:
            status = quality
        elif error:
            status = "stale"
        else:
            status = "live"

        updated_at = meta.get("updated_at")
        age = None
        try:
            if updated_at is not None:
                age = max(0.0, float(self.clock()) - float(updated_at))
        except (TypeError, ValueError):
            age = None

        return {
            "requested": requested,
            "token": canonical,
            "known": True,
            "state_key": spec.state_key,
            "status": status,
            "quality": quality or None,
            "source": meta.get("source"),
            "updated_at": updated_at,
            "age_sec": round(age, 3) if age is not None else None,
            "error": error,
            "value": value if status != "unavailable" else None,
            "text": self._format(spec, value) if status != "unavailable" else self.unavailable_text,
            "unit": spec.unit,
            "privacy": spec.privacy,
            "publication": spec.publication,
            "update_class": spec.update_class,
        }

    def snapshot(self, names: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
        if names is None:
            selected = list(sorted(self._specs))
        else:
            selected = [str(name) for name in list(names)[:64]]
        items = [self.resolve(name) for name in selected]
        return {
            "schema": self.schema,
            "count": len(items),
            "known_count": sum(1 for row in items if row.get("known")),
            "live_count": sum(1 for row in items if row.get("status") == "live"),
            "items": items,
        }

    def render(self, template: str, *, max_chars: int = 1024, max_tokens: int = 64) -> dict[str, Any]:
        raw = str(template or "")
        if len(raw) > max_chars:
            raise ValueError(f"template exceeds {max_chars} characters")
        resolved: list[dict[str, Any]] = []
        count = 0

        def repl(match: re.Match[str]) -> str:
            nonlocal count
            if count >= max_tokens:
                return self.unavailable_text
            count += 1
            row = self.resolve(match.group(1))
            resolved.append(row)
            return str(row.get("text") or self.unavailable_text)

        rendered = _TOKEN_RE.sub(repl, raw)
        return {
            "schema": self.schema,
            "template": raw,
            "text": rendered,
            "token_count": count,
            "unresolved": sorted({
                row.get("requested")
                for row in resolved
                if row.get("status") in {"unknown", "unavailable"}
            } - {None}),
            "items": resolved,
        }
