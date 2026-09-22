from __future__ import annotations

import time
from typing import Any, Callable


class ResourceGovernor:
    """Translate live system pressure into a conservative visual/resource budget.

    Escalation is immediate. Recovery to a less restrictive mode is delayed so a
    borderline temperature/load cannot make the UI oscillate every second.
    Core radio/GPS/bridge collectors are deliberately outside this governor in
    v0.11.0; the first controlled consumer is the optional/ambient UI workload.
    """

    MODES = ("FULL", "GUARDED", "REDUCED", "SURVIVAL")
    LEVEL = {name: i for i, name in enumerate(MODES)}
    POLICY = {
        "FULL": {
            "budget_pct": 100, "fps_cap": 18.0, "detail": "full",
            "ambient": True, "foreground": True, "rare_cinematic": True,
            "history_scale": 1.0,
        },
        "GUARDED": {
            "budget_pct": 75, "fps_cap": 10.0, "detail": "guarded",
            "ambient": True, "foreground": True, "rare_cinematic": True,
            "history_scale": 1.0,
        },
        "REDUCED": {
            "budget_pct": 45, "fps_cap": 6.0, "detail": "reduced",
            "ambient": True, "foreground": False, "rare_cinematic": False,
            "history_scale": 1.5,
        },
        "SURVIVAL": {
            "budget_pct": 20, "fps_cap": 3.0, "detail": "survival",
            "ambient": False, "foreground": False, "rare_cinematic": False,
            "history_scale": 2.5,
        },
    }

    def __init__(self, state, *, recovery_hold_sec: float = 20.0,
                 mono: Callable[[], float] = time.monotonic) -> None:
        self.state = state
        self.recovery_hold_sec = max(0.0, float(recovery_hold_sec))
        self._mono = mono
        self.mode = "FULL"
        self._candidate: str | None = None
        self._candidate_since = self._mono()
        self._last_transition = self._candidate_since
        self._last_reasons: list[str] = []

    @staticmethod
    def _num(value: Any) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _throttle_bits(value: Any) -> tuple[bool, bool]:
        """Return (current_throttle, historical_throttle).

        Raspberry Pi ``vcgencmd get_throttled`` uses bits 0..3 for conditions
        happening *now* and bits 16..19 for conditions that happened since
        boot.  Historical bits are useful telemetry but must not pin Beast in
        SURVIVAL after the electrical/thermal event has cleared.
        """
        if value is None:
            return False, False
        s = str(value).strip().lower()
        if not s:
            return False, False
        try:
            flags = int(s, 16) if s.startswith("0x") else int(s)
        except ValueError:
            # Unknown non-numeric status is treated conservatively as current.
            active = s not in {"0", "false", "none", "ok"}
            return active, False
        return bool(flags & 0xF), bool(flags & 0xF0000)

    def _desired(self) -> tuple[str, list[str]]:
        temp = self._num(self.state.get("system.temp.cpu_c"))
        cpu = self._num(self.state.get("system.cpu.total"))
        mem = self._num(self.state.get("system.memory.used_pct"))
        bat = self._num(self.state.get("power.battery.percent_estimate"))
        telemetry = bool(self.state.get("power.telemetry.available", False))
        external = bool(self.state.get("power.external_present", False))
        throttled, throttle_history = self._throttle_bits(self.state.get("system.throttle.flags"))

        level = 0
        reasons: list[str] = []

        def raise_to(target: int, reason: str) -> None:
            nonlocal level
            if target > level:
                level = target
            reasons.append(reason)

        if throttled:
            raise_to(3, "throttle")
        if temp is not None:
            # Start shedding cosmetic load early enough that the governor can
            # prevent, rather than merely report, a Pi thermal throttle event.
            if temp >= 80.0: raise_to(3, f"temp:{temp:.1f}C")
            elif temp >= 76.0: raise_to(2, f"temp:{temp:.1f}C")
            elif temp >= 70.0: raise_to(1, f"temp:{temp:.1f}C")
        if cpu is not None:
            if cpu >= 97.0: raise_to(3, f"cpu:{cpu:.0f}%")
            elif cpu >= 90.0: raise_to(2, f"cpu:{cpu:.0f}%")
            elif cpu >= 75.0: raise_to(1, f"cpu:{cpu:.0f}%")
        if mem is not None:
            if mem >= 94.0: raise_to(3, f"ram:{mem:.0f}%")
            elif mem >= 86.0: raise_to(2, f"ram:{mem:.0f}%")
            elif mem >= 76.0: raise_to(1, f"ram:{mem:.0f}%")
        if telemetry and not external and bat is not None:
            if bat <= 7.0: raise_to(3, f"battery:{bat:.0f}%")
            elif bat <= 15.0: raise_to(2, f"battery:{bat:.0f}%")
            elif bat <= 25.0: raise_to(1, f"battery:{bat:.0f}%")

        if not reasons:
            reasons = ["nominal"]
        return self.MODES[level], reasons

    def tick(self) -> dict[str, Any]:
        desired, reasons = self._desired()
        now = self._mono()
        old = self.mode
        old_level = self.LEVEL[old]
        new_level = self.LEVEL[desired]

        if new_level > old_level:
            self.mode = desired
            self._candidate = None
            self._last_transition = now
        elif new_level < old_level:
            if self._candidate != desired:
                self._candidate = desired
                self._candidate_since = now
            elif now - self._candidate_since >= self.recovery_hold_sec:
                self.mode = desired
                self._candidate = None
                self._last_transition = now
        else:
            self._candidate = None

        self._last_reasons = reasons
        p = self.POLICY[self.mode]
        return {
            "governor.mode": self.mode,
            "governor.level": self.LEVEL[self.mode],
            "governor.reason": ",".join(reasons[:4]),
            "governor.reasons": reasons[:8],
            "governor.budget_pct": p["budget_pct"],
            "governor.ui.fps_cap": p["fps_cap"],
            "governor.ui.detail": p["detail"],
            "governor.ui.ambient_allowed": p["ambient"],
            "governor.ui.foreground_allowed": p["foreground"],
            "governor.rare.cinematic_allowed": p["rare_cinematic"],
            "governor.history.interval_scale": p["history_scale"],
            "governor.recovery_pending": self._candidate is not None,
            "governor.recovery_target": self._candidate,
            "governor.last_transition_mono": round(self._last_transition, 3),
            "governor.throttle_current": bool(self._throttle_bits(self.state.get("system.throttle.flags"))[0]),
            "governor.throttle_history_seen": bool(self._throttle_bits(self.state.get("system.throttle.flags"))[1]),
        }
