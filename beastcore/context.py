from __future__ import annotations

import time
from typing import Any

class ContextEngine:
    """Derives safe automatic context for presentation/session behavior.

    Automatic context is deliberately visual/passive. It never arms Lab Mode or
    initiates intrusive radio actions. A debounced GPS fix is preferred so a brief
    satellite wobble does not rip Beast out of WALK/TRAVEL/WARDRIVE presentation.
    """
    def __init__(self, state) -> None:
        self.state = state
        self.current = "unknown"
        self.candidate = "unknown"
        self.candidate_since = time.monotonic()
        self.confirm_sec = 6.0

    @staticmethod
    def classify(speed_mph: float) -> str:
        if speed_mph < 1.5: return "stationary"
        if speed_mph < 7.0: return "walking"
        if speed_mph < 15.0: return "moving"
        return "wardrive"

    @staticmethod
    def _mode_and_tags(motion: str) -> tuple[str, list[str]]:
        mode = {
            "stationary": "pwn",
            "walking": "walk",
            "moving": "travel",
            "wardrive": "wardrive",
        }.get(motion, "pwn")
        tags = {
            "stationary": ["calm"],
            "walking": ["walking", "trail"],
            "moving": ["motion", "wind"],
            "wardrive": ["wardrive", "wind", "goggles"],
        }.get(motion, [])
        return mode, tags

    def tick(self) -> dict[str, Any]:
        raw_fix = bool(self.state.get("gps.fix", False))
        debounced_value = self.state.get("gps.fix.debounced", None)
        fix = raw_fix if debounced_value is None else bool(debounced_value)
        speed_mps = self.state.get("gps.speed_mps")
        values: dict[str, Any] = {
            "context.auto.enabled": True,
            "context.auto.safe_only": True,
        }

        # If raw GPS briefly drops but the semantic debounce still considers the fix
        # valid, preserve the last visual motion mode instead of snapping back to PWN.
        if fix and not raw_fix and self.current != "unknown":
            mode, tags = self._mode_and_tags(self.current)
            values.update({
                "context.motion.state": self.current,
                "context.motion.raw": "gps_grace",
                "context.mode.auto": mode,
                "context.mode.effective": mode,
                "context.motion.confidence": "medium",
                "context.visual.tags": tags,
            })
            return values

        if not fix or not isinstance(speed_mps, (int, float)):
            values.update({
                "context.motion.state": "unknown",
                "context.mode.auto": "pwn",
                "context.mode.effective": "pwn",
                "context.motion.confidence": "low",
                "context.visual.tags": ["calm"],
            })
            return values

        mph = max(0.0, float(speed_mps) * 2.2369362920544)
        raw = self.classify(mph)
        now = time.monotonic()
        if raw != self.candidate:
            self.candidate = raw
            self.candidate_since = now
        elif raw != self.current and now - self.candidate_since >= self.confirm_sec:
            self.current = raw
        if self.current == "unknown":
            self.current = raw

        mode, tags = self._mode_and_tags(self.current)
        values.update({
            "context.motion.speed_mph": round(mph, 2),
            "context.motion.state": self.current,
            "context.motion.raw": raw,
            "context.motion.confidence": "high",
            "context.mode.auto": mode,
            "context.mode.effective": mode,
            "context.visual.tags": tags,
        })
        return values
