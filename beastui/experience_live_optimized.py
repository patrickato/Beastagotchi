from __future__ import annotations

import inspect
import time

from .engine import BeastUI
from .experience_live import ExperienceBeastUI as _ExperienceBeastUI
from .experience_registry import get_experience_renderer, render_experience_page
from .monster_reveal import reveal_active, render_monster_reveal
from .rare_overlay import render_rare_overlay


class ExperienceBeastUI(_ExperienceBeastUI):
    """Hybrid, thermally sane runtime for authored Experiences.

    Experiences override only the primary pages they have actually authored.
    The complete Beast primary carousel remains reachable; pages without an
    Experience renderer fall back to the mature shared Beast page instead of
    silently disappearing behind a two-page prototype.

    The legacy Beast scheduler also uses a background-image cache to decide
    when an ambient frame is due. Experience renderers bypass that background
    pipeline, so unsolicited authored-page redraws are gated to their explicit
    cadence while dirty input/DataFeed updates remain immediate.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Renderer coverage and navigation coverage are intentionally separate.
        # The registry says which pages the Experience authored; the product
        # carousel says which primary surfaces must remain reachable.
        self.experience.pages = tuple(self.pages.IDS)
        self.experience.page_id = self.pages.IDS[self.page]

    def _current_page_id(self) -> str:
        return str(self.pages.IDS[self.page])

    def _authored_page(self, page_id: str | None = None) -> bool:
        if not hasattr(self, 'pages') or not hasattr(self, 'experience'):
            return True
        pid = str(page_id or self._current_page_id())
        return get_experience_renderer(self.experience.experience_id, pid) is not None

    def _sync_experience_page(self) -> None:
        self.experience.page_id = self._current_page_id()

    def _change_page(self, delta, wrap=True):
        BeastUI._change_page(self, delta, wrap=wrap)
        self._sync_experience_page()

    def _open_app(self, app_id):
        app = self.apps.get(app_id)
        if app is None:
            return
        if app.kind == 'page' and app.target in self.pages.IDS:
            self.app_launcher = False
            self.active_board_id = ''
            idx = self.pages.IDS.index(app.target)
            if idx != self.page:
                self._change_page(idx - self.page, wrap=False)
            else:
                self._sync_experience_page()
                self.dirty.set()
            return
        if app.kind == 'board':
            self.app_launcher = False
            self.active_board_id = str(app.target)
            idx = self.pages.IDS.index('dashboard')
            if idx != self.page:
                self._change_page(idx - self.page, wrap=False)
            else:
                self._sync_experience_page()
                self.dirty.set()
            return
        return BeastUI._open_app(self, app_id)

    def on_input(self, kind, event):
        # Shared/fallback pages retain their complete mature interaction model:
        # graph taps, widget inspector long-press, footer navigation, etc.
        if not self._authored_page():
            result = BeastUI.on_input(self, kind, event)
            self._sync_experience_page()
            return result

        # Make long-press a predictable Back action for Capsule Share as it is
        # for the other deep operational surfaces.
        if kind == 'long_press' and self.capsule_share_overlay:
            self.capsule_share_overlay = False
            self.app_launcher = True
            self.dirty.set()
            return

        return super().on_input(kind, event)

    def _theme_palette_overrides(self) -> dict[str, tuple[int, int, int]]:
        """Bridge semantic Theme colors into Experience renderers that opt in.

        This is intentionally role-based. Experience geometry remains its own
        identity while user/theme color choices can skin readable wording,
        accents and scene layers without per-screen hard-coded rewrites.
        """
        t = self.theme
        return {
            'bg': t.c('bg'),
            'header': t.c('ink'),
            'world': t.c('panel'),
            'world_deep': t.c('panel2'),
            'panel': t.c('panel2'),
            'grid': t.c('edge'),
            'edge': t.c('edge'),
            'paper': t.c('text'),
            'text': t.c('text'),
            'dim': t.c('dim'),
            'primary': t.c('primary'),
            'secondary': t.c('secondary'),
            'warn': t.c('warn'),
        }

    def _compose(self, page_idx):
        page_id = str(self.pages.IDS[page_idx])
        row = get_experience_renderer(self.experience.experience_id, page_id)
        if row is None:
            # Shared page fallback restores the complete primary carousel and
            # all of its mature theme/visualizer/input behavior.
            return BeastUI._compose(self, page_idx)

        self.phase = float(self.phase_override) if self.phase_override is not None else time.monotonic()
        kwargs = {
            'phase': self.phase,
            'navigation_pages': tuple(self.pages.IDS),
        }
        if 'palette_overrides' in inspect.signature(row.renderer).parameters:
            kwargs['palette_overrides'] = self._theme_palette_overrides()
        im = render_experience_page(
            self.experience.experience_id,
            page_id,
            self.state,
            scene_runtime=self.scene_runtime,
            **kwargs,
        )
        self.scene_runtime.end()
        from PIL import ImageDraw
        d = ImageDraw.Draw(im)
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
        im = render_monster_reveal(
            im, self.state, self.phase, self.theme, self.fonts,
            dismissed_id=self.monster_reveal_dismissed_id,
        )
        return render_rare_overlay(im, self.state, self.phase, self.theme, self.fonts)

    def _dynamic_frame_due(self, now=None):
        now = time.monotonic() if now is None else float(now)
        if self.transition:
            return True
        if self.state.get('rare.omen.active') or self.state.get('rare.moment.active'):
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
            if str(self.notice.get('kind') or '') == 'loading':
                return True

        # Shared fallback pages retain the normal Beast scheduler, including
        # theme background cadence. Authored pages use Experience cadence.
        if not self._authored_page():
            return BeastUI._dynamic_frame_due(self, now)
        cadence = max(0.1, float(self._background_cadence({}) or 1.0))
        last = float(getattr(self, '_experience_ambient_at', self.last_render) or 0.0)
        return now - last >= 1.0 / cadence

    def render(self):
        image = super().render()
        if self._authored_page():
            self._experience_ambient_at = self.last_render
        return image
