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
        background_options=dict(obj.get('background_options') or {}),
        scanline_speed=float(obj.get('scanline_speed',31.0) or 31.0),
        scanline_width=max(1,int(obj.get('scanline_width',1) or 1)),
        mood_colors={k:_hex(v) for k,v in (obj.get('mood_colors') or {}).items()},
    )
