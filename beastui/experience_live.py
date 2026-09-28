from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from typing import Any

from PIL import Image, ImageDraw

from .engine import BeastUI
from .experience_registry import available_experience_pages, render_experience_page
from .monster_reveal import render_monster_reveal, reveal_active
from .rare_overlay import render_rare_overlay


log = logging.getLogger("beastui.experience_live")


@dataclass
class ExperienceSession:
    """Small, non-persistent navigation state for one staged Experience.

    The session deliberately does not write Beast preferences or claim TFT
    ownership. It exists only for an explicitly requested staging run.
    """

    experience_id: str
    pages: tuple[str, ...]
    page_id: str

    @classmethod
    def create(cls, experience_id: str, page_id: str = "home") -> "ExperienceSession":
        eid = str(experience_id or "").strip().lower()
        pages = available_experience_pages(eid)
        if not pages:
            raise ValueError(f"unknown or unrendereable Experience: {experience_id}")
        wanted = str(page_id or "").strip().lower()
        current = wanted if wanted in pages else pages[0]
        return cls(eid, pages, current)

    @property
    def index(self) -> int:
        return self.pages.index(self.page_id)

    def select(self, page_id: str) -> bool:
        page = str(page_id or "").strip().lower()
        if page not in self.pages or page == self.page_id:
            return False
        self.page_id = page
        return True

    def move(self, delta: int) -> bool:
        if not delta:
            return False
        nxt = max(0, min(len(self.pages) - 1, self.index + (1 if delta > 0 else -1)))
        if nxt == self.index:
            return False
        self.page_id = self.pages[nxt]
        return True


class ExperienceBeastUI(BeastUI):
    """Explicit staging runtime for the new Experience renderers.

    This subclasses the proven BeastUI runtime so the Experience path uses the
    same framebuffer, display transform, touch calibration, DataFeed, overlays,
    performance telemetry, and lifecycle as the release UI. Only the page body
    compositor and page-navigation interpretation are replaced.

    It is intentionally opt-in. Constructing normal BeastUI remains the default
    production path, and no Experience choice is persisted by this class.
    """

    def __init__(self, *args, experience_id: str, experience_page: str = "home", **kwargs):
        super().__init__(*args, **kwargs)
        self.experience = ExperienceSession.create(experience_id, experience_page)
        self._sync_legacy_page_index()
        self.transition = None
        log.info(
            "Experience staging active experience=%s page=%s pages=%s",
            self.experience.experience_id,
            self.experience.page_id,
            ",".join(self.experience.pages),
        )

    def _background_cadence(self, opts):
        """Use an Experience-owned idle cadence instead of the legacy theme cadence.

        Experience pages do not render the inherited theme background. Reusing
        the legacy theme scheduler therefore wastes Pi CPU/heat by redrawing a
        layer that is not present. One idle frame per second preserves gentle
        phase-based motion and live feel; input/data dirties still render at the
        normal responsive frame budget.
        """
        return 1.0

    def _sync_legacy_page_index(self) -> None:
        """Keep inherited runtime telemetry anchored to the equivalent page id."""
        try:
            self.page = self.pages.IDS.index(self.experience.page_id)
        except ValueError:
            self.page = 0

    def _activate_experience_page(self, page_id: str) -> bool:
        changed = self.experience.select(page_id)
        if changed:
            self._sync_legacy_page_index()
            # The Experience shell owns page transition semantics for now. Avoid
            # feeding legacy index transitions into a different page universe.
            self.transition = None
            self.dirty.set()
        return changed

    def _move_experience_page(self, delta: int) -> bool:
        changed = self.experience.move(delta)
        if changed:
            self._sync_legacy_page_index()
            self.transition = None
            self.dirty.set()
        return changed

    def _experience_overlay_active(self) -> bool:
        """Return True when input belongs to an inherited operational overlay."""
        return bool(
            self.drawer
            or self.app_launcher
            or self.capsule_share_overlay
            or self.telemetry_overlay
            or self.widget_inspector_overlay
            or self.correlation_overlay
            or self.plugins_overlay
            or self.beastdex_overlay
            or self.capture_vault_overlay
            or self.performance_overlay
            or self.platform_overlay
            or self.studio_overlay
            or self.theme_library
            or self.theme_detail
            or self.visualizer_overlay
            or self.achievements_overlay
            or self.help_overlay
            or self.touch_zones_overlay
        )

    def _touch_experience_target(self, x: int, y: int) -> str | None:
        """Resolve the topmost current SceneRuntime Experience touch target."""
        rows = list((self.scene_runtime.snapshot() or {}).get("layers") or [])
        for row in reversed(rows):
            touch = str(row.get("touch") or "")
            if not touch.startswith("experience_page:"):
                continue
            bounds = row.get("bounds") or []
            if len(bounds) != 4:
                continue
            x1, y1, x2, y2 = (int(v) for v in bounds)
            if x1 <= int(x) <= x2 and y1 <= int(y) <= y2:
                target = touch.split(":", 1)[1].strip().lower()
                return target if target in self.experience.pages else None
        return None

    def on_input(self, kind, event):
        """Route shell navigation locally; delegate mature overlays to BeastUI."""
        event = dict(event or {})

        # Preserve the base runtime's pointer bookkeeping and all overlay input.
        if kind in {"touch_down", "drag", "touch_up"}:
            return super().on_input(kind, event)
        if self._experience_overlay_active():
            return super().on_input(kind, event)

        # Rare moments and monster reveals remain absolute top-layer interactions.
        if kind == "tap" and (
            reveal_active(self.state, dismissed_id=self.monster_reveal_dismissed_id)
            or self.state.get("rare.moment.active")
        ):
            return super().on_input(kind, event)

        if kind == "long_press":
            self.last_input = (kind, event)
            self.last_input_at = time.monotonic()
            self.drawer = True
            self.dirty.set()
            return

        if kind == "swipe":
            self.last_input = (kind, event)
            self.last_input_at = time.monotonic()
            axis = event.get("axis")
            if axis == "x":
                dx = float(event.get("dx", 0) or 0)
                delta = event.get("delta")
                try:
                    delta = int(delta)
                except (TypeError, ValueError):
                    delta = 1 if dx < 0 else -1 if dx > 0 else 0
                self._move_experience_page(delta)
                return
            if axis == "y" and float(event.get("dy", 0) or 0) > 30:
                self.drawer = True
                self.dirty.set()
                return
            if axis == "y" and float(event.get("dy", 0) or 0) < -30:
                self.app_launcher = True
                self.app_offset = 0
                self.drawer = False
                self.dirty.set()
                return
            return

        if kind == "tap":
            self.last_input = (kind, event)
            self.last_input_at = time.monotonic()
            target = self._touch_experience_target(
                int(event.get("x", 0) or 0), int(event.get("y", 0) or 0)
            )
            if target is not None:
                self._activate_experience_page(target)
            return

        # Unknown/non-touch input types retain the existing runtime behavior.
        return super().on_input(kind, event)

    def _compose(self, page_idx):
        """Render the Experience body, then reuse Beast's operational overlays."""
        self.phase = float(self.phase_override) if self.phase_override is not None else time.monotonic()
        im = render_experience_page(
            self.experience.experience_id,
            self.experience.page_id,
            self.state,
            phase=self.phase,
            scene_runtime=self.scene_runtime,
        )
        self.scene_runtime.end()
        d = ImageDraw.Draw(im)

        # Experience body pixels are not passed through legacy theme foreground
        # effects/header/footer. Operational overlays stay shared so staging uses
        # the actual Beast interaction/runtime stack rather than a demo shell.
        self._physical_test_overlay(d)
        self._drawer(d)
        self._apps_overlay(d)
        self._telemetry_inspector(d)
        self._widget_inspector(d)
        self._correlation_lab(d)
        self._plugins_manager(d)
        self._beastdex(d)
        self._capture_vault(d)
        self._performance_lab(d)
        self._platform_browser(d)
        self._studio_status(d)
        self._visualizers(d)
        self._theme_library_overlay(d)
        self._theme_detail_overlay(d)
        self._achievements(d)
        self._help(d)
        self._touch_zones(d)
        self._transient_notice(d)
        self._capsule_share_view(d)

        # Preserve product-wide celebratory/rare overlays above every Experience.
        im = render_monster_reveal(
            im,
            self.state,
            self.phase,
            self.theme,
            self.fonts,
            dismissed_id=self.monster_reveal_dismissed_id,
        )
        return render_rare_overlay(im, self.state, self.phase, self.theme, self.fonts)

    def experience_runtime_snapshot(self) -> dict[str, Any]:
        """Small test/diagnostic snapshot; not persisted as user preference."""
        return {
            "mode": "staging",
            "experience_id": self.experience.experience_id,
            "page_id": self.experience.page_id,
            "pages": list(self.experience.pages),
            "legacy_page_index": int(self.page),
            "writes_preferences": False,
        }
