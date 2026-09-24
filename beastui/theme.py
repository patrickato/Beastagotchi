from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


def _hex(s: str) -> tuple[int, int, int]:
    s = str(s).strip().lstrip('#')
    if len(s) != 6:
        return (255,255,255)
    try: return tuple(int(s[i:i+2],16) for i in (0,2,4))
    except Exception: return (255,255,255)


@dataclass
class Theme:
    id: str
    label: str
    colors: dict[str, tuple[int,int,int]]
    geometry: str = 'classic'
    background: str = 'grid'
    face_style: str = 'classic'
    footer_style: str = 'classic'
    reaction_style: str = 'pulse'
    scanlines: bool = True
    glow: str = 'low'
    motion: str = 'normal'
    home_scene: str | None = None
    background_options: dict | None = None
    scanline_speed: float = 31.0
    scanline_width: int = 1
    mood_colors: dict[str, tuple[int,int,int]] | None = None

    def c(self,name: str,fallback=(255,255,255)):
        return self.colors.get(name,fallback)


def load_theme(path: str|Path)->Theme:
    obj=json.loads(Path(path).read_text())
    return Theme(
        id=obj.get('id','classic'), label=obj.get('label',obj.get('id','Classic')),
        colors={k:_hex(v) for k,v in (obj.get('colors') or {}).items()},
        geometry=obj.get('geometry','classic'), background=obj.get('background','grid'),
        face_style=obj.get('face_style','classic'), footer_style=obj.get('footer_style','classic'),
        reaction_style=obj.get('reaction_style','pulse'), scanlines=bool(obj.get('scanlines',True)),
        glow=obj.get('glow','low'), motion=obj.get('motion','normal'),
        home_scene=str(obj.get('home_scene') or '').strip() or None,
        background_options=dict(obj.get('background_options') or {}),
        scanline_speed=float(obj.get('scanline_speed',31.0) or 31.0),
        scanline_width=max(1,int(obj.get('scanline_width',1) or 1)),
        mood_colors={k:_hex(v) for k,v in (obj.get('mood_colors') or {}).items()},
    )


def discover_enabled_pack_themes(
    installed_root: str | Path = "/var/lib/beastagotchi/packs/installed",
) -> dict[str, Path]:
    """Return enabled theme definitions from managed content-only Pack roots."""
    root = Path(installed_root)
    out: dict[str, Path] = {}
    try:
        packs = sorted(root.iterdir())
    except OSError:
        return out
    for pack in packs:
        if not pack.is_dir():
            continue
        try:
            state = json.loads((pack / "state.json").read_text())
            manifest = json.loads((pack / "manifest.json").read_text())
            if not bool(state.get("enabled")):
                continue
            if str(manifest.get("pack_type") or manifest.get("type") or "").lower() != "theme":
                continue
            for fp in sorted((pack / "themes").glob("*.json"))[:64]:
                obj = json.loads(fp.read_text())
                tid = str(obj.get("id") or "").strip()
                if tid and fp.stem == tid and tid not in out:
                    load_theme(fp)
                    out[tid] = fp
        except Exception:
            continue
    return out
