from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Any, Mapping

from PIL import Image, ImageDraw

from .beast_presentation import BeastPalette, draw_beast_presence
from .beast_shell import format_reading, reading
from .experience_atlas import atlas_home_metadata
from .experience_atlas_fieldbook import SIZE, _font, _register, _shell, _valid_aps
from .scene_runtime import SceneLayerSpec, SceneRuntime


@dataclass(frozen=True)
class AtlasPalette:
    bg: tuple[int, int, int] = (20, 24, 20)
    header: tuple[int, int, int] = (25, 30, 25)
    world: tuple[int, int, int] = (42, 49, 37)
    world_deep: tuple[int, int, int] = (28, 34, 28)
    panel: tuple[int, int, int] = (25, 33, 30)
    edge: tuple[int, int, int] = (82, 91, 66)
    grid: tuple[int, int, int] = (63, 72, 54)
    primary: tuple[int, int, int] = (214, 181, 83)
    secondary: tuple[int, int, int] = (77, 137, 139)
    text: tuple[int, int, int] = (241, 235, 203)
    paper: tuple[int, int, int] = (226, 219, 183)
    dim: tuple[int, int, int] = (159, 164, 132)
    warn: tuple[int, int, int] = (213, 112, 77)

    def beast_palette(self) -> BeastPalette:
        return BeastPalette(
            body_dark=(14, 22, 20), body_mid=self.secondary, highlight=self.paper,
            accent=self.primary, alert=self.warn, dim=self.grid,
        )


def _rgb(value: Any) -> tuple[int, int, int] | None:
    if isinstance(value, (list, tuple)) and len(value) == 3:
        try:
            return tuple(max(0, min(255, int(v))) for v in value)  # type: ignore[return-value]
        except (TypeError, ValueError):
            return None
    text = str(value or "").strip().lstrip("#")
    if len(text) == 6:
        try:
            return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
        except ValueError:
            return None
    return None


def resolve_atlas_palette(overrides: Mapping[str, Any] | None = None) -> AtlasPalette:
    """Resolve semantic Atlas colors; future Studio/user overrides feed this seam."""
    palette = AtlasPalette()
    allowed = set(AtlasPalette.__dataclass_fields__)
    for key, value in dict(overrides or {}).items():
        if key not in allowed:
            continue
        color = _rgb(value)
        if color is not None:
            palette = replace(palette, **{key: color})
    return palette


def _text_right(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, *, font, fill) -> None:
    bb = draw.textbbox((0, 0), str(text), font=font)
    draw.text((x - (bb[2] - bb[0]), y), str(text), font=font, fill=fill)


def _header(draw: ImageDraw.ImageDraw, page: str, shell, palette: AtlasPalette, rt=None) -> None:
    draw.rectangle((0, 0, 479, 32), fill=palette.header)
    draw.line((0, 32, 479, 32), fill=palette.edge)
    draw.text((10, 6), "ATLAS", font=_font(14), fill=palette.primary)
    draw.text((70, 8), "FIELD // HOME" if page == "home" else "SIGNAL // RECON", font=_font(10), fill=palette.paper)
    status = str(shell.status_sentence or "FIELD ACTIVE").upper()[:23]
    _text_right(draw, 469, 8, status, font=_font(9), fill=palette.dim)
    level = str(shell.attention.level or "notice")
    col = palette.warn if level in {"critical", "warning"} else palette.primary if level == "normal" else palette.dim
    draw.rectangle((301, 12, 307, 18), fill=col)
    _register(rt, SceneLayerSpec(
        f"atlas_v30.{page}.header", "text", (0, 0, 480, 33),
        signals=("health.core.state", "system.temp.cpu_c", "dock.state"), update_class="live",
    ))


def _footer(draw: ImageDraw.ImageDraw, shell, palette: AtlasPalette, rt=None) -> None:
    nav = shell.navigation
    y = nav.footer_y
    draw.rectangle((0, y, 479, 319), fill=palette.header)
    draw.line((0, y, 479, y), fill=palette.edge)
    if nav.previous_enabled:
        draw.text((12, y + 14), f"‹  {nav.previous_page.upper()}", font=_font(11), fill=palette.primary)
        _register(rt, SceneLayerSpec(
            f"atlas_v30.{nav.page_id}.nav_previous", "interaction", nav.previous_box,
            touch=f"experience_page:{nav.previous_page}", update_class="interaction",
        ))
    else:
        draw.text((12, y + 17), "FIELD START", font=_font(8), fill=palette.edge)
    mid = f"{nav.position_text}  •  ATLAS"
    bb = draw.textbbox((0, 0), mid, font=_font(9))
    draw.text((240 - (bb[2] - bb[0]) // 2, y + 16), mid, font=_font(9), fill=palette.dim)
    if nav.next_enabled:
        text = f"{nav.next_page.upper()}  ›"
        _text_right(draw, 468, y + 14, text, font=_font(11), fill=palette.primary)
        _register(rt, SceneLayerSpec(
            f"atlas_v30.{nav.page_id}.nav_next", "interaction", nav.next_box,
            touch=f"experience_page:{nav.next_page}", update_class="interaction",
        ))
    else:
        _text_right(draw, 468, y + 17, "FIELD END", font=_font(8), fill=palette.edge)


def _terrain(draw: ImageDraw.ImageDraw, phase: float, palette: AtlasPalette) -> None:
    for i, (base, amp) in enumerate(((105, 14), (151, 18), (208, 22))):
        pts = []
        for x in range(0, 350, 9):
            y = base + int(math.sin(x * .024 + i * 1.7 + phase * .05) * amp + math.sin(x * .057 - i * .4) * 4)
            pts.append((x, y))
        fill = tuple(min(255, c + i * 4) for c in palette.world_deep)
        draw.polygon(pts + [(350, 278), (0, 278)], fill=fill)
        for start in range((i * 5) % 12, len(pts) - 6, 15):
            draw.line(pts[start:start + 6], fill=palette.grid, width=1)


def _metric(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value: str, sub: str, palette: AtlasPalette, *, accent=False) -> None:
    draw.text((x, y), label, font=_font(8), fill=palette.dim)
    draw.text((x, y + 12), value[:13], font=_font(16), fill=palette.primary if accent else palette.text)
    if sub:
        draw.text((x, y + 31), sub[:16], font=_font(8), fill=palette.dim)


def _identity_plate(draw: ImageDraw.ImageDraw, identity, palette: AtlasPalette) -> None:
    draw.rectangle((13, 217, 211, 268), fill=(22, 27, 23))
    draw.rectangle((13, 217, 18, 268), fill=palette.primary)
    draw.text((29, 222), "FIELD PARTNER", font=_font(8), fill=palette.dim)
    draw.text((29, 235), identity.name.upper()[:14], font=_font(15), fill=palette.text)
    level = "—" if identity.level is None else str(identity.level)
    tail = f"{identity.stage.upper()[:9]}  •  LV {level}  •  {identity.expression.upper().replace('_', ' ')[:10]}"
    draw.text((29, 253), tail, font=_font(9), fill=palette.primary)


def _home_world(draw: ImageDraw.ImageDraw, state: dict[str, Any], meta: dict[str, Any], phase: float, palette: AtlasPalette) -> None:
    draw.rectangle((0, 33, 479, 278), fill=palette.world)
    _terrain(draw, phase, palette)
    draw.line((10, 45, 10, 265), fill=palette.primary, width=2)
    for y in range(54, 260, 18):
        draw.line((7, y, 16 if y % 54 == 0 else 13, y), fill=palette.primary if y % 54 == 0 else palette.edge)

    if bool(meta["draw_route"]):
        route = [(36, 196), (76, 177), (118, 185), (169, 144), (230, 151), (287, 111), (326, 121)]
        draw.line(route, fill=palette.primary, width=3)
        for x, y in route:
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=palette.paper)
        draw.text((220, 91), "ROUTE / LIVE", font=_font(9), fill=palette.primary)
    else:
        status_col = palette.warn if meta["gps_fix"] is False else palette.dim
        draw.text((213, 84), str(meta["gps_status"]), font=_font(10), fill=status_col)
        draw.text((213, 99), "ROUTE HOLDS UNTIL FIX", font=_font(8), fill=palette.dim)

    cx, cy = 271, 145
    for radius in (35, 62, 91):
        draw.arc((cx-radius, cy-int(radius*.52), cx+radius, cy+int(radius*.52)), 195, 345, fill=palette.grid, width=1)
    for idx, (ap, ch, rssi) in enumerate(_valid_aps(state)[:10]):
        angle = math.radians(205 + ((ch * 17 + idx * 31) % 135))
        radius = max(22, min(88, int((abs(rssi) - 25) * 1.1)))
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius * .52)
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=palette.secondary if bool(ap.get("handshake")) else palette.paper)


def render_atlas_home(
    state: dict[str, Any], *, phase: float = 0.0,
    scene_runtime: SceneRuntime | None = None,
    palette_overrides: Mapping[str, Any] | None = None,
    beast_traits: Mapping[str, Any] | None = None,
) -> Image.Image:
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    shell = _shell(state, "home")
    palette = resolve_atlas_palette(palette_overrides)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="home", scene_id="experience:atlas:home", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, palette.bg)
    draw = ImageDraw.Draw(im)
    _header(draw, "home", shell, palette, rt)
    _home_world(draw, state, meta, phase, palette)

    identity = draw_beast_presence(
        im, (18, 45, 228, 225), state, phase,
        palette=palette.beast_palette(), concept_style="classic", traits=beast_traits,
    )
    draw = ImageDraw.Draw(im)
    _identity_plate(draw, identity, palette)
    _register(rt, SceneLayerSpec(
        "atlas_v30.home.beast", "creature", (18, 45, 228, 268),
        signals=(
            "progression.beast.name", "progression.beast.kind", "progression.beast.lineage",
            "progression.stage", "progression.level", "progression.aura",
            "beast.expression", "pwnagotchi.mood",
        ), update_class="ambient", resource_class="moderate", reduced_motion="static_creature",
    ))
    _register(rt, SceneLayerSpec(
        "atlas_v30.home.world", "environment", (0, 33, 350, 279),
        signals=("gps.fix", "gps.satellites_used", "expedition.route_points", "wifi.aps"),
        update_class="live", decorative=False,
    ))

    draw.rectangle((348, 42, 470, 268), fill=palette.world_deep)
    draw.rectangle((348, 42, 352, 268), fill=palette.primary)
    draw.text((364, 49), "FIELD STATE", font=_font(9), fill=palette.primary)
    channel = "—" if meta["channel"] is None else str(meta["channel"])
    _metric(draw, 364, 67, "RADIO", f"CH {channel}", str(meta["band"] or "—").upper(), palette, accent=meta["channel"] is not None)
    unique = "—" if meta["ap_unique"] is None else str(meta["ap_unique"])
    _metric(draw, 364, 119, "OBSERVED", unique, "UNIQUE AP", palette)
    gps = "FIXED" if meta["gps_fix"] is True else "SEARCH" if meta["gps_fix"] is False else "—"
    sats = format_reading(reading(state, "gps.satellites_used"))
    _metric(draw, 364, 171, "POSITION", gps, f"{sats} SATS", palette, accent=meta["gps_fix"] is True)
    temp = format_reading(meta["temp_reading"])
    gov = format_reading(meta["governor_reading"])
    _metric(draw, 364, 223, "SYSTEM", temp, gov, palette)
    _register(rt, SceneLayerSpec(
        "atlas_v30.home.hud", "instrument", (348, 42, 471, 269),
        signals=(
            "radio.primary.channel", "radio.primary.band", "expedition.ap_unique",
            "gps.fix", "gps.satellites_used", "system.temp.cpu_c", "governor.mode",
        ), update_class="live",
    ))

    draw.text((225, 230), "EXPEDITION", font=_font(8), fill=palette.dim)
    active = "ACTIVE" if meta["expedition_active"] is True else "IDLE" if meta["expedition_active"] is False else "—"
    draw.text((225, 243), active, font=_font(11), fill=palette.primary if active == "ACTIVE" else palette.dim)
    caps = format_reading(reading(state, "expedition.captures_delta"))
    xp = format_reading(reading(state, "expedition.xp_delta"))
    draw.text((225, 259), f"CAP +{caps}   XP +{xp}", font=_font(9), fill=palette.text)
    _register(rt, SceneLayerSpec(
        "atlas_v30.home.expedition", "timeline", (220, 226, 345, 270),
        signals=("expedition.active", "expedition.captures_delta", "expedition.xp_delta"), update_class="live",
    ))

    _footer(draw, shell, palette, rt)
    return im


def render_atlas_recon(
    state: dict[str, Any], *, phase: float = 0.0,
    scene_runtime: SceneRuntime | None = None,
    palette_overrides: Mapping[str, Any] | None = None,
    beast_traits: Mapping[str, Any] | None = None,
) -> Image.Image:
    state = dict(state or {})
    meta = atlas_home_metadata(state)
    shell = _shell(state, "recon")
    palette = resolve_atlas_palette(palette_overrides)
    rt = scene_runtime
    if rt is not None:
        rt.begin(page_id="recon", scene_id="experience:atlas:recon", theme_id="experience.atlas")
        rt.update_signals(state)

    im = Image.new("RGB", SIZE, palette.bg)
    draw = ImageDraw.Draw(im)
    _header(draw, "recon", shell, palette, rt)
    draw.rectangle((0, 33, 479, 278), fill=(19, 27, 25))

    cx, cy = 164, 178
    for radius in (42, 78, 116, 154, 193):
        draw.arc((cx-radius, cy-int(radius*.56), cx+radius, cy+int(radius*.56)), 205, 345, fill=(45, 77, 68), width=1)
    for deg in (-62, -42, -22, 0, 22, 42, 62):
        angle = math.radians(deg)
        draw.line((cx, cy, int(cx + math.cos(angle) * 250), int(cy + math.sin(angle) * 140)), fill=(38, 65, 58), width=1)

    sweep = -2.55 + ((phase * .22) % 1.9)
    for idx in range(5):
        angle = sweep - idx * .045
        col = tuple(min(255, c + idx * 5) for c in (56, 100, 94))
        draw.line((cx, cy, int(cx + math.cos(angle) * 245), int(cy + math.sin(angle) * 138)), fill=col, width=1)

    valid = _valid_aps(state)
    strongest = sorted(valid, key=lambda row: row[2], reverse=True)[:3]
    for idx, (ap, ch, rssi) in enumerate(valid[:24]):
        angle = math.radians(-66 + ((ch * 19 + idx * 37) % 132))
        radius = max(34, min(190, int((abs(rssi) - 25) * 2.1)))
        x = int(cx + math.cos(angle) * radius)
        y = int(cy + math.sin(angle) * radius * .56)
        col = palette.secondary if bool(ap.get("handshake")) else palette.paper
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(19, 27, 25), outline=col, width=2)
        if (ap, ch, rssi) in strongest or bool(ap.get("handshake")):
            draw.text((x + 7, y - 7), f"{ch} / {int(rssi)}", font=_font(8), fill=col)

    draw_beast_presence(
        im, (38, 102, 196, 229), state, phase,
        palette=palette.beast_palette(), concept_style="classic", traits=beast_traits,
    )
    draw = ImageDraw.Draw(im)
    draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), outline=palette.primary, width=2)
    draw.text((22, 54), "BEAST SENSE / RF FIELD", font=_font(11), fill=palette.primary)
    draw.text((22, 70), "RADIUS = RELATIVE RSSI  •  ANGLE ≠ POSITION", font=_font(8), fill=palette.dim)
    _register(rt, SceneLayerSpec(
        "atlas_v30.recon.beast", "creature", (38, 102, 197, 230),
        signals=(
            "progression.beast.name", "progression.stage", "progression.level", "progression.aura",
            "beast.expression", "pwnagotchi.mood",
        ), update_class="ambient", resource_class="moderate", reduced_motion="static_creature",
    ))
    _register(rt, SceneLayerSpec(
        "atlas_v30.recon.field", "graph", (0, 33, 349, 279),
        signals=("wifi.aps", "wifi.ap_count", "wifi.handshake_ap_count", "wifi.hidden_count"),
        update_class="live", decorative=False,
    ))

    draw.line((23, 91, 326, 91), fill=palette.edge, width=1)
    draw.text((23, 82), "2.4G", font=_font(8), fill=palette.dim)
    draw.text((279, 82), "5G", font=_font(8), fill=palette.dim)
    for ap, ch, rssi in valid:
        x = 58 + int((max(1, ch) - 1) / 13 * 116) if ch <= 14 else 205 + int((min(165, max(36, ch)) - 36) / 129 * 118)
        height = max(3, min(14, int((90 + max(-90, min(-30, rssi))) / 4)))
        draw.line((x, 91, x, 91 - height), fill=palette.secondary if bool(ap.get("handshake")) else palette.paper, width=2)

    draw.rectangle((349, 42, 470, 268), fill=palette.panel)
    draw.rectangle((349, 42, 353, 268), fill=palette.secondary)
    draw.text((364, 49), "SIGNAL READ", font=_font(9), fill=palette.secondary)
    count24 = sum(1 for _, ch, _ in valid if ch <= 14)
    count5 = sum(1 for _, ch, _ in valid if ch > 14)
    _metric(draw, 364, 67, "BANDS", f"{count24} / {count5}", "2.4G / 5G", palette)
    hs = format_reading(reading(state, "wifi.handshake_ap_count"))
    hidden = format_reading(reading(state, "wifi.hidden_count"))
    _metric(draw, 364, 119, "CAPTURE", f"HS {hs}", f"HIDDEN {hidden}", palette, accent=hs not in {"—", "0"})
    channel = "—" if meta["channel"] is None else str(meta["channel"])
    _metric(draw, 364, 171, "TUNED", f"CH {channel}", str(meta["band"] or "—").upper(), palette, accent=meta["channel"] is not None)
    if strongest:
        _, ch, rssi = strongest[0]
        _metric(draw, 364, 223, "STRONGEST", f"{int(rssi)} dB", f"CH {ch}", palette)
    else:
        _metric(draw, 364, 223, "STRONGEST", "—", "NO OBSERVATIONS", palette)
    _register(rt, SceneLayerSpec(
        "atlas_v30.recon.hud", "instrument", (349, 42, 471, 269),
        signals=(
            "wifi.aps", "wifi.handshake_ap_count", "wifi.hidden_count",
            "radio.primary.channel", "radio.primary.band",
        ), update_class="live",
    ))

    _footer(draw, shell, palette, rt)
    return im
