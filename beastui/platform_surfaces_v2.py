from __future__ import annotations

from typing import Any

from .widgets import panel


_GENERIC_ACCENTS = {
    "timeline": "info",
    "notifications": "warn",
    "diagnostics": "warn",
    "services": "accent",
    "hardware": "secondary",
    "storage": "info",
    "tasks": "secondary",
    "field_library": "accent",
    "missions": "primary",
    "containers": "info",
    "incidents": "warn",
    "backups": "accent",
    "ai_operator": "primary",
    "connectivity": "info",
    "command_center": "accent",
}

_GENERIC_LABELS = {
    "notifications": "NOTIFICATIONS",
    "diagnostics": "COLLECTOR HEALTH",
    "services": "SERVICES",
    "hardware": "HARDWARE",
    "storage": "STORAGE",
    "timeline": "TIMELINE",
    "tasks": "TASK CENTER",
    "field_library": "FIELD LIBRARY",
    "missions": "MISSIONS",
    "containers": "CONTAINERS",
    "incidents": "INCIDENTS",
    "backups": "BACKUPS",
    "ai_operator": "AI OPERATOR",
    "connectivity": "CONNECTIVITY",
    "command_center": "COMMAND CENTER",
}

_EMPTY_COPY = {
    "notifications": ("NO ACTIVE NOTICES", "Important events and warnings will appear here."),
    "incidents": ("NO OPEN INCIDENTS", "Black Box has no incident rows to surface."),
    "tasks": ("NO RECENT TASKS", "Durable background operations will appear here."),
    "hardware": ("NO HARDWARE ROWS", "Detected capabilities will appear when available."),
    "backups": ("NO BACKUP ROWS", "Create and verify backups from Beast Studio."),
}


def _clean_hardware_rows(self) -> list[dict[str, Any]]:
    rows = []
    for row in self.state.get("platform.hardware") or []:
        if not isinstance(row, dict):
            continue
        raw = str(row.get("raw") or row.get("id") or "USB device")
        rid = str(row.get("id") or "USB")
        title = raw
        subtitle = ""
        if " ID " in raw:
            bus, rest = raw.split(" ID ", 1)
            parts = rest.split(" ", 1)
            parsed_id = parts[0] if parts else rid
            label = parts[1] if len(parts) > 1 else ""
            title = label or parsed_id
            subtitle = f"{bus} · {parsed_id}"
        rows.append({
            "title": title,
            "subtitle": subtitle or raw[:44],
            "value": rid,
            "severity": "info",
        })
    if rows:
        return rows

    for row in self.state.get("capabilities.items") or []:
        if isinstance(row, dict):
            rows.append({
                "title": str(row.get("label") or row.get("id") or "capability"),
                "subtitle": str(row.get("detail") or ""),
                "value": str(row.get("state") or "DETECTED"),
                "severity": "info",
            })
    return rows


def _connectivity_rows(self) -> list[dict[str, Any]]:
    route = bool(self.state.get("network.route.available"))
    rows = [{
        "title": "DEFAULT ROUTE",
        "subtitle": f"{self.state.get('network.default.dev') or '--'} via {self.state.get('network.default.gateway') or '--'}",
        "value": "AVAILABLE" if route else "NONE",
        "severity": "info" if route else "warning",
    }, {
        "title": "INTERNET",
        "subtitle": "Route alone does not prove Internet reachability",
        "value": str(self.state.get("network.internet.state") or "unknown").upper(),
        "severity": "info",
    }]
    for row in self.state.get("network.interfaces") or []:
        if not isinstance(row, dict):
            continue
        addresses = ", ".join(str(x) for x in (row.get("addresses") or [])[:2]) or "--"
        up = str(row.get("operstate") or "unknown")
        rows.append({
            "title": str(row.get("name") or "interface"),
            "subtitle": addresses,
            "value": up.upper(),
            "severity": "info" if up == "up" else "warning",
        })
    return rows


def _draw_beast_badge(self, draw, color) -> None:
    """Persistent companion signature for operational apps."""
    t = self.theme
    f = self.fonts
    name = str(self.state.get("progression.beast.name") or "BEAST").strip().upper()[:7] or "BEAST"
    level = self.state.get("progression.level")
    bx, by = 326, 46
    draw.polygon(
        [(bx, by + 12), (bx + 4, by + 5), (bx + 10, by + 3), (bx + 16, by + 6),
         (bx + 20, by + 12), (bx + 17, by + 20), (bx + 10, by + 23), (bx + 3, by + 20)],
        fill=t.c("panel2"), outline=color,
    )
    draw.polygon([(bx + 4, by + 7), (bx + 3, by + 1), (bx + 8, by + 5)], fill=t.c("panel2"), outline=color)
    draw.polygon([(bx + 13, by + 5), (bx + 18, by + 1), (bx + 18, by + 8)], fill=t.c("panel2"), outline=color)
    draw.point((bx + 7, by + 12), fill=t.c("accent"))
    draw.point((bx + 14, by + 12), fill=t.c("accent"))
    ident = name
    if isinstance(level, (int, float)):
        ident += f" · {int(level)}"
    draw.text((351, 50), ident, font=f["small"], fill=color)


def _platform_rows_v2(self, mode):
    mode = str(mode or "")
    if mode == "connectivity":
        return _connectivity_rows(self)
    if mode == "hardware":
        return _clean_hardware_rows(self)
    return self._platform_rows_v1(mode)


def _platform_browser_v2(self, draw):
    if not self.platform_overlay:
        return
    mode = str(self.platform_overlay)

    if mode in {"topology", "operations"}:
        return self._platform_browser_v1(draw)

    t = self.theme
    f = self.fonts
    rows = self._platform_rows(mode)
    page = self.platform_offset // self.PLATFORM_PAGE_SIZE + 1
    pages = max(1, (len(rows) + self.PLATFORM_PAGE_SIZE - 1) // self.PLATFORM_PAGE_SIZE)
    accent = _GENERIC_ACCENTS.get(mode, "primary")
    color = t.c(accent, t.c("primary"))

    draw.rectangle((0, 34, 480, 278), fill=t.c("ink"))
    panel(draw, (8, 40, 472, 274), t, accent=color, width=2)
    title = _GENERIC_LABELS.get(mode, mode.replace("_", " ").upper())
    draw.text((20, 47), title + " // LIVE", font=f["medium"], fill=color)
    _draw_beast_badge(self, draw, t.c("secondary"))
    draw.text((438, 50), f"{page}/{pages}", font=f["small"], fill=t.c("dim"))

    visible = rows[self.platform_offset:self.platform_offset + self.PLATFORM_PAGE_SIZE]
    for i, row in enumerate(visible):
        y = 72 + i * 50
        severity = str(row.get("severity") or "info").lower()
        value_color = (
            t.c("danger") if severity in {"error", "critical"}
            else t.c("warn") if severity == "warning"
            else t.c("accent")
        )
        draw.rounded_rectangle((16, y - 3, 464, y + 43), radius=6, fill=t.c("panel2"), outline=t.c("edge"))
        draw.rectangle((16, y - 3, 21, y + 43), fill=value_color)

        draw.text((30, y + 1), str(row.get("title") or "--")[:29], font=f["body"], fill=t.c("text"))
        value = str(row.get("value") or "")[:13]
        box = draw.textbbox((0, 0), value, font=f["small"])
        value_width = max(0, box[2] - box[0])
        pill_x = max(342, 452 - value_width - 12)
        draw.rounded_rectangle((pill_x, y, 458, y + 18), radius=4, fill=t.c("ink"), outline=value_color)
        draw.text((458 - value_width - 6, y + 4), value, font=f["small"], fill=value_color)
        draw.text((30, y + 24), str(row.get("subtitle") or "")[:57], font=f["small"], fill=t.c("text"))

    if not rows:
        headline, detail = _EMPTY_COPY.get(mode, ("NO CURRENT ITEMS", "This live surface has no rows to display."))
        draw.text((20, 100), headline, font=f["medium"], fill=t.c("dim"))
        draw.text((20, 126), detail[:58], font=f["small"], fill=t.c("text"))
        draw.text((20, 151), "Unavailable stays unavailable; Beast does not invent demo state.", font=f["small"], fill=t.c("warn"))

    for box, border in (
        (self.PLATFORM_NAV_PREV, t.c("primary")),
        (self.PLATFORM_NAV_CLOSE, t.c("edge")),
        (self.PLATFORM_NAV_NEXT, t.c("primary")),
    ):
        draw.rounded_rectangle(box, radius=7, fill=t.c("panel2"), outline=border, width=2)
    draw.text((43, 241), "<< PREV", font=f["small"], fill=t.c("primary"))
    draw.text((214, 241), "APPS", font=f["small"], fill=t.c("text"))
    draw.text((365, 241), "NEXT >>", font=f["small"], fill=t.c("primary"))


def install(BeastUI) -> None:
    """Install the physical-readability operational-surface grammar once."""
    if getattr(BeastUI, "_platform_surface_v2_installed", False):
        return
    BeastUI._platform_rows_v1 = BeastUI._platform_rows
    BeastUI._platform_browser_v1 = BeastUI._platform_browser
    BeastUI._platform_rows = _platform_rows_v2
    BeastUI._platform_browser = _platform_browser_v2
    BeastUI._platform_surface_v2_installed = True
