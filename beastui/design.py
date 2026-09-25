from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DesignTokens:
    """Shared v0.19 visual/interaction tokens for the 480x320 reference canvas.

    These are semantic interaction/layout defaults, not a theme palette. Theme
    families keep their own geometry, effects and identity while sharing a
    readable interaction grammar.
    """

    canvas_w: int = 480
    canvas_h: int = 320
    header_h: int = 34
    footer_y: int = 278
    footer_h: int = 42

    space_xs: int = 4
    space_s: int = 8
    space_m: int = 12
    space_l: int = 16

    radius_s: int = 4
    radius_m: int = 7
    radius_l: int = 10

    stroke_hairline: int = 1
    stroke_emphasis: int = 2

    # Derived from the validated resistive Touch Lab rather than desktop UI
    # conventions. Visible art may be smaller only when the hit target remains
    # at least this large.
    touch_min: int = 48
    touch_normal: int = 56
    touch_primary: int = 72

    motion_fast_s: float = 0.16
    motion_page_s: float = 0.24
    motion_notice_s: float = 0.30
    notice_default_s: float = 2.40

    font_micro: int = 6
    font_tiny: int = 7
    font_small: int = 9
    font_body: int = 11
    font_medium: int = 13
    font_large: int = 18
    font_title: int = 16


TOKENS = DesignTokens()

# The main page/tab/swipe experience is intentionally first-class and distinct
# from the app/studio/depot layers. This is a reference set, not a hard product
# ceiling: future pages may be added when they earn a persistent position.
PRIMARY_PAGES = (
    "home",
    "overview",
    "dashboard",
    "recon",
    "networks",
    "spectrum",
    "captures",
    "map",
    "expedition",
    "beast",
    "system",
)

PAGE_GROUPS = {
    "identity": ("home", "beast"),
    "awareness": ("overview", "recon", "networks", "spectrum", "map"),
    "records": ("captures", "expedition"),
    "workspace": ("dashboard",),
    "device": ("system",),
}


def page_index(page_id: str) -> int:
    try:
        return PRIMARY_PAGES.index(str(page_id))
    except ValueError:
        return 0


def page_group(page_id: str) -> str:
    ident=str(page_id)
    for group, pages in PAGE_GROUPS.items():
        if ident in pages:
            return group
    return "other"


def page_group_boundaries() -> tuple[int, ...]:
    """Indexes where a new semantic page group begins in PRIMARY_PAGES."""
    out=[]
    previous=None
    for idx,page_id in enumerate(PRIMARY_PAGES):
        group=page_group(page_id)
        if idx and group!=previous:
            out.append(idx)
        previous=group
    return tuple(out)
