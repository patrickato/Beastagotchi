from __future__ import annotations

import re
from typing import Any

_KEY_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,96}$")

WIDGET_STYLES = ("metric", "bar", "radial", "microtrend")
DASHBOARD_GRID_COLS = 12
DASHBOARD_GRID_ROWS = 8
# Preference files are user-editable. This is a corruption/DoS guard, not a UI
# product limit: 96 equals one instrument per logical grid cell and is far
# beyond what a 480x320 composition can use meaningfully.
MAX_DASHBOARD_WIDGETS = DASHBOARD_GRID_COLS * DASHBOARD_GRID_ROWS

# Curated fallback catalog used when Beast Core is not reachable (for example
# during source tests). Beast Studio augments this with the live Telemetry
# Catalog at runtime, so the actual device can bind any safe scalar key Beast
# currently exposes without hard-coding the entire future platform here.
DASHBOARD_KEY_CATALOG: tuple[dict[str, Any], ...] = (
    {"key":"system.cpu.total","label":"CPU","unit":"%","category":"System","min":0,"max":100},
    {"key":"system.memory.used_pct","label":"RAM","unit":"%","category":"System","min":0,"max":100},
    {"key":"system.temp.cpu_c","label":"CPU TEMP","unit":"C","category":"System","min":25,"max":85},
    {"key":"system.uptime_sec","label":"UPTIME","unit":"s","category":"System"},
    {"key":"wifi.ap_count","label":"APS","unit":"AP","category":"Wi-Fi","min":0,"max":100},
    {"key":"wifi.client_count","label":"CLIENTS","unit":"client","category":"Wi-Fi","min":0,"max":100},
    {"key":"wifi.encounters.lifetime_unique","label":"LIFE AP","unit":"AP","category":"Wi-Fi"},
    {"key":"radio.primary.channel","label":"CHANNEL","unit":None,"category":"Radio"},
    {"key":"pwnagotchi.handshakes","label":"HANDSHAKES","unit":"capture","category":"Pwnagotchi"},
    {"key":"gps.satellites_used","label":"GPS SAT","unit":"sat","category":"GPS","min":0,"max":16},
    {"key":"context.motion.speed_mph","label":"SPEED","unit":"mph","category":"Field","min":0,"max":80},
    {"key":"expedition.distance_m","label":"DISTANCE","unit":"m","category":"Expedition"},
    {"key":"expedition.ap_unique","label":"EXP AP","unit":"AP","category":"Expedition"},
    {"key":"power.battery.percent_estimate","label":"BATTERY","unit":"%","category":"Power","min":0,"max":100},
    {"key":"power.power_w","label":"POWER","unit":"W","category":"Power","min":0,"max":20},
    {"key":"performance.beast.cpu_pct","label":"BEAST CPU","unit":"%","category":"Performance","min":0,"max":100},
    {"key":"performance.fb.write_ratio_pct","label":"FB WRITE","unit":"%","category":"Performance","min":0,"max":100},
)

DEFAULT_DASHBOARD_WIDGETS: tuple[dict[str, Any], ...] = (
    {"key":"system.cpu.total","label":"CPU","style":"radial","min":0,"max":100,"x":0,"y":0,"w":4,"h":3},
    {"key":"system.temp.cpu_c","label":"TEMP","style":"bar","min":25,"max":85,"x":4,"y":0,"w":4,"h":3},
    {"key":"wifi.ap_count","label":"APS","style":"microtrend","min":0,"max":100,"x":8,"y":0,"w":4,"h":3},
    {"key":"radio.primary.channel","label":"CHANNEL","style":"metric","x":0,"y":4,"w":4,"h":3},
    {"key":"gps.satellites_used","label":"GPS SAT","style":"bar","min":0,"max":16,"x":4,"y":4,"w":4,"h":3},
    {"key":"expedition.distance_m","label":"TRIP","style":"metric","x":8,"y":4,"w":4,"h":3},
)


def _catalog_map(catalog: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None) -> dict[str, dict[str, Any]]:
    rows = list(DASHBOARD_KEY_CATALOG)
    if catalog:
        rows.extend(x for x in catalog if isinstance(x, dict))
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("key") or "")
        if key and _KEY_RE.fullmatch(key):
            out[key] = dict(row)
    return out


def scalar_catalog(telemetry_rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return Studio-safe scalar telemetry bindings, augmented by live Core data."""
    merged = _catalog_map()
    for row in telemetry_rows or []:
        if not isinstance(row, dict):
            continue
        key = str(row.get("key") or "")
        if not _KEY_RE.fullmatch(key):
            continue
        value = row.get("value")
        # Structured/list telemetry belongs in purpose-built widgets; Dashboard
        # slots are scalar by design so a generic editor cannot misrepresent it.
        if isinstance(value, (dict, list, tuple, set)):
            continue
        merged[key] = {
            **merged.get(key, {}),
            "key": key,
            "label": str(row.get("label") or merged.get(key, {}).get("label") or key.split(".")[-1]).upper()[:22],
            "unit": row.get("unit", merged.get(key, {}).get("unit")),
            "category": str(row.get("category") or merged.get(key, {}).get("category") or "Other"),
            "kind": row.get("kind"),
            "quality": row.get("quality"),
        }
    return sorted(merged.values(), key=lambda r: (str(r.get("category")), str(r.get("label"))))


def validate_dashboard_widgets(raw: Any, *, catalog: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Validate an editable live-instrument composition.

    Older releases always normalized to exactly six slots. The compositor is
    now spatial: users may add/remove instruments and intentionally overlap
    them. ``z`` defines paint/hit order and ``visible`` allows variants to
    retain temporarily hidden instruments.
    """
    cmap = _catalog_map(catalog)
    incoming = raw if isinstance(raw, list) else [dict(x) for x in DEFAULT_DASHBOARD_WIDGETS]
    if not incoming:
        incoming = [dict(x) for x in DEFAULT_DASHBOARD_WIDGETS]
    cleaned: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for idx, src0 in enumerate(incoming[:MAX_DASHBOARD_WIDGETS]):
        if not isinstance(src0, dict):
            continue
        src = dict(src0)
        fallback = dict(DEFAULT_DASHBOARD_WIDGETS[idx % len(DEFAULT_DASHBOARD_WIDGETS)])
        key = str(src.get("key") or fallback["key"])
        if not _KEY_RE.fullmatch(key):
            key = str(fallback["key"])
        meta = cmap.get(key, {})
        style = str(src.get("style") or fallback.get("style") or "metric")
        if style not in WIDGET_STYLES:
            style = "metric"
        label = str(src.get("label") or meta.get("label") or key.split(".")[-1]).strip()[:18]
        wid = str(src.get("id") or f"instrument_{idx+1}").strip().lower().replace(" ", "_")
        if not _KEY_RE.fullmatch(wid) or wid in used_ids:
            base=f"instrument_{idx+1}";wid=base;n=2
            while wid in used_ids:
                wid=f"{base}_{n}";n+=1
        used_ids.add(wid)
        row: dict[str, Any] = {
            "id": wid, "key": key,
            "label": label or key.split(".")[-1][:18],
            "style": style,
            "visible": bool(src.get("visible", True)),
        }
        try: row["z"] = max(-999, min(999, int(src.get("z", idx))))
        except (TypeError, ValueError): row["z"] = idx
        try:
            x=max(0,min(DASHBOARD_GRID_COLS-1,int(src.get("x",fallback["x"]))))
            y=max(0,min(DASHBOARD_GRID_ROWS-1,int(src.get("y",fallback["y"]))))
            w=max(2,min(DASHBOARD_GRID_COLS-x,int(src.get("w",fallback["w"]))))
            h=max(2,min(DASHBOARD_GRID_ROWS-y,int(src.get("h",fallback["h"]))))
        except (TypeError, ValueError):
            x,y,w,h=(fallback[k] for k in ("x","y","w","h"))
        row.update({"x":x,"y":y,"w":w,"h":h})
        for field in ("min", "max"):
            val = src.get(field, meta.get(field))
            try:
                if val is not None:
                    row[field] = float(val)
            except (TypeError, ValueError):
                pass
        if "min" in row and "max" in row and row["max"] <= row["min"]:
            row.pop("min", None); row.pop("max", None)
        cleaned.append(row)
    return cleaned


def dashboard_history_keys(widgets: list[dict[str, Any]]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(w.get("key")) for w in widgets if isinstance(w, dict) and bool(w.get("visible", True)) and str(w.get("style")) == "microtrend" and _KEY_RE.fullmatch(str(w.get("key") or ""))))


_BOARD_ID_RE = re.compile(r"^[a-z0-9_-]{1,40}$")

def validate_custom_boards(raw: Any, *, catalog: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Validate user-created live instrument boards.

    Boards are expandable app destinations, not members of a fixed main-page
    list. Each board uses the same canonical telemetry/widget model as the
    built-in Dashboard and therefore renders through the same compositor.
    """
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]]=[];used:set[str]=set()
    for idx,src in enumerate(raw[:64]):
        if not isinstance(src,dict):
            continue
        bid=str(src.get("id") or f"board_{idx+1}").strip().lower().replace(" ","_")
        if not _BOARD_ID_RE.fullmatch(bid) or bid in used:
            continue
        label=str(src.get("label") or bid).strip()[:22] or bid
        widgets=validate_dashboard_widgets(src.get("widgets") or [],catalog=catalog)
        if not widgets:
            continue
        used.add(bid);out.append({"id":bid,"label":label,"widgets":widgets})
    return out

# Context Decks are curated launcher views, not hard limits on what Beast can
# contain. Any implemented app remains reachable from ALL; decks merely keep
# high-frequency workflows clean as the application universe grows.
DEFAULT_CONTEXT_DECKS: tuple[dict[str, Any], ...] = (
    {"id":"field","label":"FIELD","apps":["home","overview","dashboard","recon","networks","map","expedition","field_library","telemetry","hardware","storage"]},
    {"id":"radio","label":"RADIO","apps":["recon","networks","spectrum","captures","capture_vault","beastdex","telemetry","performance"]},
    {"id":"system","label":"SYSTEM","apps":["overview","system","operations","topology","performance","diagnostics","incidents","services","tasks","hardware","storage","backups","plugins","beast_studio"]},
    {"id":"studio","label":"STUDIO","apps":["themes","visualizers","beast_studio","dashboard","telemetry","correlation","plugins"]},
)

_DECK_ID_RE = re.compile(r"^[a-z0-9_-]{1,32}$")
_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
PALETTE_SLOTS: tuple[str, ...] = (
    "bg","ink","panel","panel2","edge","grid","primary","secondary",
    "accent","info","warn","danger","text","dim","scanline",
)


def validate_context_decks(raw: Any, *, app_ids: list[str] | tuple[str, ...] | set[str] | None = None) -> list[dict[str, Any]]:
    """Validate user launcher decks without imposing a product feature limit.

    Unknown/deleted app ids are ignored. A deck may contain any number of
    currently implemented apps; ordering is preserved and duplicates collapse.
    """
    allowed = set(str(x) for x in (app_ids or ()))
    incoming = raw if isinstance(raw, list) else [dict(x) for x in DEFAULT_CONTEXT_DECKS]
    out: list[dict[str, Any]] = []
    used: set[str] = set()
    for idx, row in enumerate(incoming):
        if not isinstance(row, dict):
            continue
        did = str(row.get("id") or f"deck{idx+1}").strip().lower().replace(" ", "_")
        if not _DECK_ID_RE.fullmatch(did) or did in used:
            continue
        label = str(row.get("label") or did).strip().upper()[:18] or did.upper()
        apps: list[str] = []
        for app in row.get("apps") or []:
            aid = str(app).strip()
            if not aid or aid in apps:
                continue
            if allowed and aid not in allowed:
                continue
            apps.append(aid)
        if not apps:
            continue
        used.add(did)
        out.append({"id": did, "label": label, "apps": apps})
    # Never let a malformed preferences file erase the concept entirely.
    if not out and raw is not None:
        return validate_context_decks(None, app_ids=app_ids)
    return out


def validate_palette_overrides(raw: Any, *, theme_ids: list[str] | tuple[str, ...] | set[str] | None = None) -> dict[str, dict[str, str]]:
    allowed_themes = set(str(x) for x in (theme_ids or ()))
    if not isinstance(raw, dict):
        return {}
    out: dict[str, dict[str, str]] = {}
    for tid, values in raw.items():
        tid = str(tid)
        if allowed_themes and tid not in allowed_themes:
            continue
        if not isinstance(values, dict):
            continue
        clean: dict[str, str] = {}
        for slot, color in values.items():
            slot = str(slot)
            color = str(color).strip()
            if slot in PALETTE_SLOTS and _COLOR_RE.fullmatch(color):
                clean[slot] = color.lower()
        if clean:
            out[tid] = clean
    return out


def validate_correlation_keys(raw: Any, *, catalog: list[dict[str, Any]] | None = None) -> list[str]:
    default = ["system.cpu.total", "system.temp.cpu_c"]
    allowed = {str(x.get("key")) for x in (catalog or []) if isinstance(x, dict) and x.get("key")}
    vals = raw if isinstance(raw, (list, tuple)) else default
    out: list[str] = []
    for value in vals:
        key = str(value or "")
        if not _KEY_RE.fullmatch(key):
            continue
        if allowed and key not in allowed:
            continue
        if key not in out:
            out.append(key)
        if len(out) == 2:
            break
    for key in default:
        if len(out) >= 2:
            break
        if (not allowed or key in allowed) and key not in out:
            out.append(key)
    return out[:2]


def dashboard_widget_box(widget: dict[str, Any], *, bounds: tuple[int,int,int,int]=(8,43,472,268), gap: int=4) -> tuple[int,int,int,int]:
    """Map a validated 12x8 dashboard geometry into TFT pixel coordinates."""
    x1,y1,x2,y2=bounds
    width=max(1,x2-x1);height=max(1,y2-y1)
    gx=max(0,min(DASHBOARD_GRID_COLS-1,int(widget.get("x",0))))
    gy=max(0,min(DASHBOARD_GRID_ROWS-1,int(widget.get("y",0))))
    gw=max(1,min(DASHBOARD_GRID_COLS-gx,int(widget.get("w",4))))
    gh=max(1,min(DASHBOARD_GRID_ROWS-gy,int(widget.get("h",3))))
    left=x1+round(width*gx/DASHBOARD_GRID_COLS)
    top=y1+round(height*gy/DASHBOARD_GRID_ROWS)
    right=x1+round(width*(gx+gw)/DASHBOARD_GRID_COLS)-gap
    bottom=y1+round(height*(gy+gh)/DASHBOARD_GRID_ROWS)-gap
    return (left,top,max(left+28,right),max(top+24,bottom))

def dashboard_widget_boxes(widgets: list[dict[str, Any]]) -> list[tuple[int,int,int,int]]:
    return [dashboard_widget_box(w) for w in widgets if isinstance(w,dict) and bool(w.get("visible",True))]
