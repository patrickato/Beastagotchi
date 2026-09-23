from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from beastcore.pack_activation import PackActivationManager
from beastui.face import FaceEngine
from beastui.animationpacks import discover_enabled_animation_profiles


class State:
    def get(self,key,default=None):return default


class Theme:
    colors={"panel":(6,12,18),"primary":(40,230,210),"accent":(190,255,120),"danger":(255,80,90),"dim":(100,120,130),"edge":(30,55,70)}
    face_style="classic";mood_colors={}
    def c(self,key):return self.colors.get(key,(220,230,240))


def _animation_pack(root: Path, enabled=True):
    p=root/"gentle-motion";(p/"animations").mkdir(parents=True)
    (p/"manifest.json").write_text(json.dumps({"id":"gentle-motion","label":"Gentle Motion","version":"1","pack_type":"animation","resource_class":"none","thermal_class":"static"}))
    (p/"state.json").write_text(json.dumps({"state":"enabled" if enabled else "disabled","enabled":enabled}))
    (p/"animations"/"float.json").write_text(json.dumps({
        "id":"float","label":"Gentle Float","target":"face",
        "motion":{"bob_px":4,"bob_period_s":2.5,"sway_px":2,"sway_period_s":4.5,"breath_px":1,"breath_period_s":3.5},
        "orbit":{"count":2,"radius_pct":48,"speed_rps":0.08,"dot_radius_px":2,"color_role":"accent"},
        "reactive":{"alert":1.8,"sleep":0.4}
    }))
    return p


def test_enabled_animation_pack_is_discovered(tmp_path: Path):
    root=tmp_path/"installed";_animation_pack(root)
    rows=discover_enabled_animation_profiles(root)
    assert len(rows)==1
    row=next(iter(rows.values()))
    assert row["motion"]["bob_px"]==4
    assert row["orbit"]["count"]==2


def test_disabled_animation_pack_is_not_discovered(tmp_path: Path):
    root=tmp_path/"installed";_animation_pack(root,False)
    assert discover_enabled_animation_profiles(root)=={}


def test_animation_profile_changes_render_over_time(tmp_path: Path):
    root=tmp_path/"installed";_animation_pack(root)
    pid=next(iter(discover_enabled_animation_profiles(root)))
    face=FaceEngine(animation_profile_id=pid,installed_root=root)
    a=Image.new("RGB",(220,140),(0,0,0));b=Image.new("RGB",(220,140),(0,0,0))
    state={"beast.expression":"idle","health.core.state":"healthy"}
    face.draw(ImageDraw.Draw(a),(20,20,200,120),Theme(),state,0.0)
    face.draw(ImageDraw.Draw(b),(20,20,200,120),Theme(),state,0.7)
    assert ImageChops.difference(a,b).getbbox() is not None


def test_animation_activation_rejects_non_face_target(tmp_path: Path):
    root=tmp_path/"installed";p=_animation_pack(root)
    fp=p/"animations"/"float.json";obj=json.loads(fp.read_text());obj["target"]="global";fp.write_text(json.dumps(obj))
    plan=PackActivationManager(State(),installed_root=root).plan("gentle-motion",True)
    assert plan["allowed"] is False
    assert any("target" in x for x in plan["blockers"])
