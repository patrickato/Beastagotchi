from __future__ import annotations

import shutil
from typing import Any

from .base import Collector


class DesktopCapabilityCollector(Collector):
    """Discover optional graphical/desktop capabilities without starting them."""

    name = "desktop"
    interval = 60.0
    priority = 25

    CANDIDATES = (
        ("labwc", "Wayland / labwc"),
        ("wayfire", "Wayland / Wayfire"),
        ("startlxde", "LXDE"),
        ("startlxde-pi", "Raspberry Pi Desktop"),
        ("startx", "X11"),
    )

    def collect(self) -> dict[str, Any]:
        found=[]
        for exe,label in self.CANDIDATES:
            path=shutil.which(exe)
            if path:
                found.append({"id":exe,"label":label,"path":path})
        browsers=[]
        for exe in ("chromium","chromium-browser","firefox-esr","firefox"):
            path=shutil.which(exe)
            if path:browsers.append({"id":exe,"path":path})
        return {
            "desktop.runtime.available": bool(found),
            "desktop.runtimes": found,
            "desktop.browser.available": bool(browsers),
            "desktop.browsers": browsers,
            "desktop.session.state": "not_started_by_beast",
        }
