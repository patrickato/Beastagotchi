from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from beastcore.pack_activation import PackActivationManager
from beastui.face import FaceEngine
from beastui.facepacks import discover_enabled_face_profiles


class State:
    def get(self, key, default=None):
        return default


class Theme:
    colors={
        "bg":(0,0,0),"panel":(6,12,18),"primary":(40,230,210),"secondary":(140,120,255),
        "accent":(190,255,120),"info":(80,170,255),"warn":(255,190,70),"danger":(255,80,90),
        "text":(230,240,245),"dim":(100,120,130),"edge":(30,55,70),"grid":(20,45,55),
        "ink":(5,8,10),"panel2":(10,20,28),"scanline":(15,30,35),
    }
    face_style="classic"
    mood_colors={}
    def c(self,key):
        return self.colors.get(key,self.colors["primary"])


def _face_pack(root: Path, *, enabled=True, renderer="vector"):
    p=root/"orbit-faces";(p/"faces").mkdir(parents=True)
    (p/"manifest.json").write_text(json.dumps({
        "id":"orbit-faces","label":"Orbit Faces","version":"1.0","pack_type":"face",
        "resource_class":"none","thermal_class":"static"
    }))
    (p/"state.json").write_text(json.dumps({"state":"enabled" if enabled else "disabled","enabled":enabled}))
    if renderer=="glyph":
        definition={"id":"orbital","label":"Orbital Glyph","renderer":"glyph","expressions":{"awake":"< o_o >","alert":"< ! ! >"}}
    else:
        definition={
            "id":"orbital","label":"Orbital Vector","renderer":"vector","background":"panel",
            "expressions":{
                "awake":[
                    {"type":"ellipse","box":[120,100,880,900],"stroke":"primary","width":3},
                    {"type":"ellipse","box":[280,350,410,500],"fill":"accent","stroke":"accent"},
                    {"type":"ellipse","box":[590,350,720,500],"fill":"accent","stroke":"accent"},
                    {"type":"arc","box":[330,480,670,780],"start":20,"end":160,"stroke":"primary","width":3}
                ],
                "alert":[
                    {"type":"polygon","points":[[120,500],[500,100],[880,500],[500,900]],"stroke":"danger","width":3},
                    {"type":"line","points":[[310,380],[430,500]],"stroke":"danger","width":3},
                    {"type":"line","points":[[690,380],[570,500]],"stroke":"danger","width":3}
                ]
            }
        }
    (p/"faces"/"orbital.json").write_text(json.dumps(definition))
    return p


def test_enabled_face_pack_is_discovered_and_scoped(tmp_path: Path):
    root=tmp_path/"installed";_face_pack(root)
    rows=discover_enabled_face_profiles(root)
    assert len(rows)==1
    pid=next(iter(rows))
    assert pid.startswith("pack_orbit-faces_")
    assert rows[pid]["renderer"]=="vector"


def test_disabled_face_pack_is_not_discovered(tmp_path: Path):
    root=tmp_path/"installed";_face_pack(root,enabled=False)
    assert discover_enabled_face_profiles(root)=={}


def test_vector_face_pack_renders_without_code(tmp_path: Path):
    root=tmp_path/"installed";_face_pack(root)
    pid=next(iter(discover_enabled_face_profiles(root)))
    face=FaceEngine(pid,installed_root=root)
    im=Image.new("RGB",(220,140),(0,0,0));d=ImageDraw.Draw(im)
    face.draw(d,(10,10,210,130),Theme(),{"beast.expression":"idle","health.core.state":"healthy"},0.25)
    assert len(im.getcolors(maxcolors=100000) or []) > 2


def test_glyph_face_pack_renders(tmp_path: Path):
    root=tmp_path/"installed";_face_pack(root,renderer="glyph")
    pid=next(iter(discover_enabled_face_profiles(root)))
    face=FaceEngine(pid,installed_root=root)
    im=Image.new("RGB",(220,140),(0,0,0));d=ImageDraw.Draw(im)
    face.draw(d,(10,10,210,130),Theme(),{"pwnagotchi.mood":"awake","health.core.state":"healthy"},0.25)
    assert len(im.getcolors(maxcolors=100000) or []) > 1


def test_face_activation_rejects_unknown_renderer(tmp_path: Path):
    root=tmp_path/"installed";p=_face_pack(root)
    obj=json.loads((p/"faces"/"orbital.json").read_text());obj["renderer"]="python"
    (p/"faces"/"orbital.json").write_text(json.dumps(obj))
    plan=PackActivationManager(State(),installed_root=root).plan("orbit-faces",True)
    assert plan["allowed"] is False
    assert any("renderer" in x for x in plan["blockers"])
