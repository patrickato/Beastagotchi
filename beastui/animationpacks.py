from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
COLOR_ROLES = {"primary","secondary","accent","info","warn","danger","text","dim","edge"}


class AnimationPackError(ValueError):
    pass


def _num(value: Any, default: float, lo: float, hi: float) -> float:
    try:value=float(value)
    except Exception:value=float(default)
    return max(lo,min(hi,value))


def clean_animation_profile(obj: dict[str, Any], *, source_pack: str = "", source_file: str = "") -> dict[str, Any]:
    if not isinstance(obj,dict):raise AnimationPackError("animation definition must be an object")
    local_id=str(obj.get("id") or "").strip().lower()
    if not _ID_RE.fullmatch(local_id):raise AnimationPackError("invalid animation id")
    label=str(obj.get("label") or local_id).strip()[:64] or local_id
    target=str(obj.get("target") or "face").strip().lower()
    if target!="face":raise AnimationPackError("v0.19 animation target must be face")

    raw_motion=obj.get("motion") if isinstance(obj.get("motion"),dict) else {}
    motion={
        "bob_px":_num(raw_motion.get("bob_px"),0,0,6),
        "bob_period_s":_num(raw_motion.get("bob_period_s"),4.0,.8,20),
        "sway_px":_num(raw_motion.get("sway_px"),0,0,6),
        "sway_period_s":_num(raw_motion.get("sway_period_s"),6.0,.8,20),
        "breath_px":_num(raw_motion.get("breath_px"),0,0,5),
        "breath_period_s":_num(raw_motion.get("breath_period_s"),5.0,1.0,20),
    }
    raw_orbit=obj.get("orbit") if isinstance(obj.get("orbit"),dict) else {}
    role=str(raw_orbit.get("color_role") or "accent").strip().lower()
    if role not in COLOR_ROLES:role="accent"
    orbit={
        "count":int(_num(raw_orbit.get("count"),0,0,4)),
        "radius_pct":_num(raw_orbit.get("radius_pct"),48,25,65),
        "speed_rps":_num(raw_orbit.get("speed_rps"),.06,-.25,.25),
        "dot_radius_px":int(_num(raw_orbit.get("dot_radius_px"),2,1,4)),
        "color_role":role,
    }
    raw_reactive=obj.get("reactive") if isinstance(obj.get("reactive"),dict) else {}
    reactive={}
    for mood,mul in list(raw_reactive.items())[:32]:
        mood=str(mood).strip().lower()[:32]
        if mood:reactive[mood]=_num(mul,1.0,.2,2.5)

    if not any((motion["bob_px"],motion["sway_px"],motion["breath_px"],orbit["count"])):
        raise AnimationPackError("animation profile has no visible motion")
    return {
        "local_id":local_id,"label":label,"target":"face","motion":motion,"orbit":orbit,
        "reactive":reactive,"source_pack":str(source_pack or ""),"source_file":str(source_file or ""),
    }


def _runtime_id(pack_id: str, local_id: str) -> str:
    raw=f"pack_{pack_id}_{local_id}".lower()
    safe=re.sub(r"[^a-z0-9_-]+","_",raw).strip("_")
    return safe[:64]


def discover_enabled_animation_profiles(
    installed_root: str | Path = "/var/lib/beastagotchi/packs/installed",
) -> dict[str,dict[str,Any]]:
    root=Path(installed_root);out={}
    try:packs=sorted(root.iterdir())
    except OSError:return out
    for pack in packs:
        if not pack.is_dir():continue
        try:
            state=json.loads((pack/"state.json").read_text());manifest=json.loads((pack/"manifest.json").read_text())
            if not bool(state.get("enabled")):continue
            if str(manifest.get("pack_type") or manifest.get("type") or "").lower()!="animation":continue
            pack_id=str(manifest.get("id") or pack.name)
            for fp in sorted((pack/"animations").glob("*.json"))[:64]:
                obj=json.loads(fp.read_text());profile=clean_animation_profile(obj,source_pack=pack_id,source_file=str(fp))
                if profile["local_id"]!=fp.stem:continue
                rid=_runtime_id(pack_id,profile["local_id"])
                if rid not in out:out[rid]={**profile,"id":rid}
        except Exception:continue
    return out
