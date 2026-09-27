from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


QUALITY_LIVE = "live"
QUALITY_CAPTURED = "captured"
QUALITY_STALE = "stale"
QUALITY_ESTIMATED = "estimated"
QUALITY_UNKNOWN = "unknown"
QUALITY_UNAVAILABLE = "unavailable"
QUALITY_ERROR = "error"

KNOWN_QUALITIES = {
    QUALITY_LIVE,
    QUALITY_CAPTURED,
    QUALITY_STALE,
    QUALITY_ESTIMATED,
    QUALITY_UNKNOWN,
    QUALITY_UNAVAILABLE,
    QUALITY_ERROR,
}


@dataclass(frozen=True)
class ShellTypeRamp:
    """Legibility-first type sizes for the 480x320 / 3.5-inch shell.

    Experience bodies may use larger display type, but shell-critical meaning
    must not depend on the legacy 6-9 px microtext scale.
    """

    caption: int = 11
    body: int = 13
    label: int = 15
    title: int = 18
    hero: int = 24


SHELL_TYPE = ShellTypeRamp()


@dataclass(frozen=True)
class Reading:
    key: str
    value: Any = None
    unit: str = ""
    quality: str = QUALITY_UNKNOWN
    source: str = ""
    age_s: float | None = None

    @property
    def known(self) -> bool:
        return self.quality not in {QUALITY_UNKNOWN, QUALITY_UNAVAILABLE, QUALITY_ERROR} and self.value is not None

    @property
    def display(self) -> str:
        if self.quality == QUALITY_UNAVAILABLE:
            return "N/A"
        if self.quality == QUALITY_ERROR:
            return "ERR"
        if self.value is None:
            return "—"
        return str(self.value)


@dataclass(frozen=True)
class AttentionState:
    level: str
    summary: str
    source: str = ""


@dataclass(frozen=True)
class NavigationModel:
    experience_id: str
    page_id: str
    pages: tuple[str, ...]
    index: int
    previous_page: str
    next_page: str
    footer_y: int = 264
    footer_h: int = 56
    previous_box: tuple[int, int, int, int] = (0, 264, 160, 320)
    home_box: tuple[int, int, int, int] = (160, 264, 320, 320)
    next_box: tuple[int, int, int, int] = (320, 264, 480, 320)


@dataclass(frozen=True)
class BeastShellModel:
    experience_id: str
    page_id: str
    attention: AttentionState
    navigation: NavigationModel
    status_sentence: str


def _number(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _quality(state: dict[str, Any], key: str, *, default: str) -> str:
    q = str(state.get(f"{key}.quality") or default).strip().lower()
    return q if q in KNOWN_QUALITIES else default


def reading(
    state: dict[str, Any],
    key: str,
    *,
    unit: str = "",
    source: str = "",
    default_quality: str = QUALITY_LIVE,
) -> Reading:
    """Return one truthful reading without coercing missing data to zero.

    Optional sibling metadata keys are understood when present:
      <key>.quality  live/captured/stale/estimated/unknown/unavailable/error
      <key>.source   provider identifier
      <key>.age_s    observation age
    """

    state = dict(state or {})
    present = key in state and state.get(key) is not None and state.get(key) != ""
    quality = _quality(state, key, default=default_quality if present else QUALITY_UNKNOWN)
    value = state.get(key) if present else None
    if quality in {QUALITY_UNKNOWN, QUALITY_UNAVAILABLE, QUALITY_ERROR} and not present:
        value = None
    age = _number(state.get(f"{key}.age_s"))
    return Reading(
        key=str(key),
        value=value,
        unit=str(unit or ""),
        quality=quality,
        source=str(state.get(f"{key}.source") or source or ""),
        age_s=age,
    )


def format_reading(row: Reading, *, precision: int = 0, suffix: str | None = None) -> str:
    """Format a Reading while preserving unknown/unavailable/error semantics."""

    if not row.known:
        return row.display
    value = row.value
    if isinstance(value, bool):
        text = "YES" if value else "NO"
    else:
        n = _number(value)
        if n is None:
            text = str(value)
        elif precision <= 0:
            text = str(int(round(n)))
        else:
            text = f"{n:.{int(precision)}f}"
    tail = row.unit if suffix is None else str(suffix)
    return f"{text}{tail}"


def _state_word(state: dict[str, Any], key: str) -> str:
    return str(state.get(key) or "").strip().lower()


def attention_state(state: dict[str, Any]) -> AttentionState:
    """One shared, conservative attention ladder for all Experiences."""

    state = dict(state or {})
    health = _state_word(state, "health.core.state")
    temp = _number(state.get("system.temp.cpu_c"))
    pwn = _state_word(state, "pwnagotchi.service.state")
    bettercap = _state_word(state, "bettercap.service.state")
    monitor = _state_word(state, "radio.monitor.state")

    if health in {"critical", "fault", "failed", "failure"}:
        return AttentionState("critical", "SYSTEM NEEDS ATTENTION", "health.core.state")
    if temp is not None and temp >= 80.0:
        return AttentionState("critical", "THERMAL CRITICAL", "system.temp.cpu_c")
    if pwn in {"failed", "failure", "inactive", "dead"} or bettercap in {"failed", "failure", "inactive", "dead"}:
        return AttentionState("warning", "RADIO STACK OFFLINE", "radio-stack")
    if monitor in {"failed", "failure", "offline", "down"}:
        return AttentionState("warning", "MONITOR INPUT OFFLINE", "radio.monitor.state")
    if health in {"degraded", "warning", "warn"}:
        return AttentionState("warning", "SYSTEM DEGRADED", "health.core.state")
    if temp is not None and temp >= 75.0:
        return AttentionState("warning", "THERMAL HIGH", "system.temp.cpu_c")
    if health in {"healthy", "ok", "ready", "nominal"}:
        return AttentionState("normal", "SYSTEM READY", "health.core.state")
    return AttentionState("notice", "STATUS UNKNOWN", "health.core.state")


def navigation_model(experience_id: str, page_id: str, pages: Iterable[str]) -> NavigationModel:
    ordered = tuple(str(p).strip().lower() for p in pages if str(p).strip()) or ("home",)
    current = str(page_id or "home").strip().lower()
    try:
        index = ordered.index(current)
    except ValueError:
        index = 0
        current = ordered[0]
    previous_page = ordered[index - 1] if len(ordered) > 1 else current
    next_page = ordered[(index + 1) % len(ordered)] if len(ordered) > 1 else current
    return NavigationModel(
        experience_id=str(experience_id or "").strip().lower(),
        page_id=current,
        pages=ordered,
        index=index,
        previous_page=previous_page,
        next_page=next_page,
    )


def status_sentence(state: dict[str, Any], attention: AttentionState) -> str:
    if attention.level in {"critical", "warning"}:
        return attention.summary

    ch = reading(state, "radio.primary.channel")
    nearby = reading(state, "wifi.ap_count")
    if ch.known and nearby.known:
        return f"CH {format_reading(ch)} · {format_reading(nearby)} NEARBY"
    if ch.known:
        return f"CH {format_reading(ch)}"
    if nearby.known:
        return f"{format_reading(nearby)} NEARBY"
    return attention.summary


def build_shell_model(
    experience_id: str,
    page_id: str,
    state: dict[str, Any],
    pages: Iterable[str],
) -> BeastShellModel:
    attn = attention_state(state)
    nav = navigation_model(experience_id, page_id, pages)
    return BeastShellModel(
        experience_id=str(experience_id or "").strip().lower(),
        page_id=nav.page_id,
        attention=attn,
        navigation=nav,
        status_sentence=status_sentence(state, attn),
    )
