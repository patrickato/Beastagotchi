from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UXTokens:
    """Reference interaction tokens for the v0.19 visual-cohesion milestone.

    These are semantic defaults, not a theme palette. Themes remain free to
    change visual identity while sharing readable spacing and interaction
    grammar.
    """

    canvas_w: int = 480
    canvas_h: int = 320
    header_h: int = 34
    footer_h: int = 38
    edge_pad: int = 8
    gap_xs: int = 3
    gap_sm: int = 6
    gap_md: int = 10
    gap_lg: int = 16
    touch_min: int = 48
    touch_preferred: int = 56
    radius_sm: int = 3
    radius_md: int = 6
    stroke_normal: int = 1
    stroke_emphasis: int = 2
    animation_fast_ms: int = 120
    animation_normal_ms: int = 220
    animation_slow_ms: int = 420


TOKENS = UXTokens()


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

# Pages remain a first-class navigation concept. Apps/studios are deeper tools,
# not a replacement for the swipe/page experience.
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
