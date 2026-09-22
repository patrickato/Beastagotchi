from __future__ import annotations

# Physical 3.5-inch resistive-panel policy derived from 3x stylus + 3x finger
# Touch Lab runs. Visible art may be smaller; the interaction bounds should not.
TOUCH_TARGET_MIN = 48
TOUCH_TARGET_NORMAL = 56
TOUCH_TARGET_PRIMARY = 72
EDGE_EXPAND_PX = 10


GLOBAL_CONTROLS = [
    ("TAP", "open/select / footer arrows"),
    ("LONG PRESS", "open/close Visual Control"),
    ("SWIPE LEFT / RIGHT", "next / previous main page"),
    ("SWIPE DOWN", "open Visual Control"),
    ("SWIPE UP", "close drawer / help"),
    ("BOTTOM <  >", "reliable page navigation"),
    ("CENTER FOOTER", "return Home"),
]

PAGE_HINTS = {
    "home": "HOME: summary; tap-able widgets arrive as app/detail views mature.",
    "recon": "RECON: radar/signal objects will gain tap-for-detail and filters.",
    "networks": "NETWORKS: list/detail sorting and search are planned here.",
    "spectrum": "SPECTRUM: per-widget renderer switching is the next major UI control.",
    "captures": "CAPTURES: Capture Vault browsing/validation/session links live here.",
    "map": "MAP: pan/layers/markers/routes will use the same interaction registry.",
    "beast": "BEAST: progression, evolution, face packs, auras and achievements.",
    "system": "SYSTEM: Hardware Studio, power, dock, services and diagnostics.",
}

TOUCH_ZONES = [
    (4, 281, 122, 319, "PREV"),
    (122, 274, 358, 319, "HOME"),
    (358, 281, 476, 319, "NEXT"),
]


def rows_for(page_id: str):
    return list(GLOBAL_CONTROLS)


def hint_for(page_id: str):
    return PAGE_HINTS.get(page_id, "Context help is generated from the active interaction registry.")
