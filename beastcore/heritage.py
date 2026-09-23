from __future__ import annotations

import hashlib
from typing import Any


TRAIT_VOCAB = {
    "silhouette": ("orb","angular","feline","lupine","avian","spectral","mech","insectoid"),
    "eyes": ("round","slit","visor","tri","dot","ring","asym"),
    "mouth": ("neutral","smile","fang","beak","waveform","none"),
    "accent": ("none","horns","antenna","fins","ears","halo","spines","whiskers"),
    "aura": ("static","spark","mist","scan","flame","orbital","shadow"),
    "motion": ("calm","float","bob","stalk","pulse","orbit","twitch"),
    "palette": ("parent_a","parent_b","split","gradient","contrast","monochrome"),
    "emphasis": ("balanced","recon","system","map","spectrum","creature"),
}
TEMPERAMENT_AXES = ("curiosity","social","focus","boldness","nocturnal")
MUTATIONS = (
    ("chromatic_shift","rare"),
    ("echo_eyes","rare"),
    ("dual_aura","epic"),
    ("wild_motion","epic"),
    ("apex_crown","legendary"),
)


def _digest(seed: str, label: str) -> bytes:
    return hashlib.sha256(f"{seed}|{label}".encode()).digest()


def _index(seed: str, label: str, size: int) -> int:
    if size <= 0:return 0
    return int.from_bytes(_digest(seed,label)[:8],"big") % size


def _axis(seed: str, label: str) -> int:
    return int.from_bytes(_digest(seed,label)[:2],"big") % 101


def _lineage_defaults(lineage: str) -> dict[str,Any]:
    lineage=str(lineage or "standard")
    traits={}
    for key,choices in TRAIT_VOCAB.items():
        if key=="palette":
            continue
        traits[key]=choices[_index(lineage,key,len(choices))]
    traits["palette"]="parent_a"
    traits["temperament"]={axis:_axis(lineage,axis) for axis in TEMPERAMENT_AXES}
    return traits


def normalize_parent_traits(parent: dict[str,Any]) -> dict[str,Any]:
    lineage=str(parent.get("lineage_id") or "standard")
    out=_lineage_defaults(lineage)
    sources=[]
    ident=parent.get("identity") if isinstance(parent.get("identity"),dict) else {}
    appearance=parent.get("appearance") if isinstance(parent.get("appearance"),dict) else {}
    for source in (ident.get("traits"),appearance.get("traits")):
        if isinstance(source,dict):sources.append(source)
    for source in sources:
        for key,choices in TRAIT_VOCAB.items():
            value=str(source.get(key) or "").strip().lower()
            if value in choices:out[key]=value
        temp=source.get("temperament")
        if isinstance(temp,dict):
            for axis in TEMPERAMENT_AXES:
                try:out["temperament"][axis]=max(0,min(100,int(temp.get(axis))))
                except Exception:pass
    return out


def _pick_parent(seed: str, key: str, a: Any, b: Any) -> tuple[Any,str]:
    if a==b:return a,"shared"
    if _index(seed,"inherit:"+key,2)==0:return a,"parent_a"
    return b,"parent_b"


def mutation_chance_basis_points(parent_a: dict[str,Any], parent_b: dict[str,Any]) -> int:
    # 3.5% base; cross-lineage and level-100 ancestry modestly increase the
    # chance without making mutation a farmable/guaranteed result.
    chance=350
    if str(parent_a.get("lineage_id"))!=str(parent_b.get("lineage_id")):chance+=150
    if int(parent_a.get("level") or 1)>=100:chance+=250
    if int(parent_b.get("level") or 1)>=100:chance+=250
    return min(1000,chance)


def generate_heritage(parent_a: dict[str,Any], parent_b: dict[str,Any], seed: str) -> dict[str,Any]:
    a=normalize_parent_traits(parent_a);b=normalize_parent_traits(parent_b)
    inherited={};provenance={}
    for key in ("silhouette","eyes","mouth","accent","aura","motion","emphasis"):
        inherited[key],provenance[key]=_pick_parent(seed,key,a[key],b[key])

    # Palette may be explicitly blended even if neither parent's abstract
    # default is meaningful to render directly.
    palette_modes=TRAIT_VOCAB["palette"]
    inherited["palette"]=palette_modes[_index(seed,"palette-blend",len(palette_modes))]
    provenance["palette"]="blended"

    temperament={}
    temperament_sources={}
    for axis in TEMPERAMENT_AXES:
        av=int(a["temperament"][axis]);bv=int(b["temperament"][axis])
        # Small deterministic ±8 inherited variation, clamped. This makes
        # siblings theoretically distinct if later rules ever permit them.
        jitter=(_index(seed,"temperament:"+axis,17)-8)
        temperament[axis]=max(0,min(100,round((av+bv)/2)+jitter))
        temperament_sources[axis]={"parent_a":av,"parent_b":bv,"jitter":jitter}
    inherited["temperament"]=temperament
    provenance["temperament"]=temperament_sources

    chance=mutation_chance_basis_points(parent_a,parent_b)
    roll=_index(seed,"mutation-roll",10000)
    mutation=None
    if roll<chance:
        mid,rarity=MUTATIONS[_index(seed,"mutation-kind",len(MUTATIONS))]
        mutation={"id":mid,"rarity":rarity,"roll":roll,"chance_basis_points":chance}

    legacy=[]
    if int(parent_a.get("level") or 1)>=100:
        legacy.append({"from":"parent_a","id":"apex_lineage"})
    if int(parent_b.get("level") or 1)>=100:
        legacy.append({"from":"parent_b","id":"apex_lineage"})
    if str(parent_a.get("lineage_id"))!=str(parent_b.get("lineage_id")):
        legacy.append({"from":"pair","id":"cross_lineage"})

    return {
        "schema":1,
        "seed":str(seed),
        "traits":inherited,
        "provenance":provenance,
        "mutation":mutation,
        "mutation_roll":roll,
        "mutation_chance_basis_points":chance,
        "legacy_markers":legacy,
        "parent_traits":{"parent_a":a,"parent_b":b},
    }
