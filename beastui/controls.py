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
    "home": "HOME: Beast identity first; live mode, health and exploration stay glanceable.",
    "overview": "OVERVIEW: attention first; Operations keeps the dense diagnostic detail.",
    "dashboard": "DASHBOARD: user-composed live instruments; long-press a tile for its source.",
    "recon": "RECON: tap the live field to cycle truthful views of observed Wi-Fi objects.",
    "networks": "NETWORKS: strongest live APs here; deeper detail/search keeps the complete catalog.",
    "spectrum": "SPECTRUM: tap the chart to change renderer; values are observed occupancy, not raw RF power.",
    "captures": "CAPTURES: tap analytics to change renderer; Capture Vault holds indexed file detail.",
    "map": "MAP: route trace uses recorded GPS fixes only; no fix means no invented position.",
    "expedition": "EXPEDITION: live field-session glance; archive/replay belongs in deeper history.",
    "beast": "BEAST: active creature progression, evolution, aura and achievement context.",
    "system": "SYSTEM: health/resource glance; Hardware and Operations provide deeper controls.",
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
