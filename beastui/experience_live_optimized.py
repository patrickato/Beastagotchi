from __future__ import annotations

import time

from .experience_live import ExperienceBeastUI as _ExperienceBeastUI
from .monster_reveal import reveal_active


class ExperienceBeastUI(_ExperienceBeastUI):
    """Thermally sane staging runtime for authored Experiences.

    The legacy Beast scheduler uses a background-image cache to decide when an
    ambient frame is due. Experience renderers deliberately bypass that legacy
    background pipeline, so the cache remains empty. Treating an empty legacy
    cache as a redraw request caused otherwise-static Experiences to recompose
    at the adaptive frame budget instead of their authored ambient cadence.

    Dirty input/DataFeed updates remain immediate. This override only gates
    unsolicited ambient frames and transient animation still bypasses the gate.
    """

    def _dynamic_frame_due(self, now=None):
        now = time.monotonic() if now is None else float(now)
        if self.transition:
            return True
        if self.state.get("rare.omen.active") or self.state.get("rare.moment.active"):
            return True
        mr = reveal_active(self.state, dismissed_id=self.monster_reveal_dismissed_id)
        if mr:
            self._monster_reveal_was_active = True
            return True
        if self._monster_reveal_was_active:
            self._monster_reveal_was_active = False
            return True
        if self.button_flash:
            age = now - self.button_flash_at
            if age < 0.30:
                return True
            self.button_flash = None
            return True
        if self.notice:
            age = now - float(self.notice_started or 0.0)
            if age >= float(self.notice_duration or 2.4):
                self.notice = None
                return True
            if str(self.notice.get("kind") or "") == "loading":
                return True

        cadence = max(0.1, float(self._background_cadence({}) or 1.0))
        last = float(getattr(self, "_experience_ambient_at", self.last_render) or 0.0)
        return now - last >= 1.0 / cadence

    def render(self):
        image = super().render()
        self._experience_ambient_at = self.last_render
        return image
