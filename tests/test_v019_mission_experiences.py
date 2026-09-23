from __future__ import annotations

import json
from pathlib import Path

from beastcore.missions import MissionPackEngine
from beastcore.pack_activation import PackActivationManager


class State:
    def __init__(self,data=None):self.data=dict(data or {})
    def get(self,key,default=None):return self.data.get(key,default)


def _mission_pack(root: Path,enabled=True):
    p=root/"field-experience";(p/"missions").mkdir(parents=True)
    (p/"manifest.json").write_text(json.dumps({
        "id":"field-experience","label":"Field Experience","version":"1",
        "pack_type":"mission","resource_class":"none","thermal_class":"static",
        "dependencies":["example-orchard-theme","example-orbit-faces","example-gentle-motion"]
    }))
    (p/"state.json").write_text(json.dumps({"state":"enabled" if enabled else "disabled","enabled":enabled}))
    (p/"missions"/"field.json").write_text(json.dumps({
        "id":"field","label":"Field Companion","description":"A composed field identity",
        "theme":"orchard_example",
        "face_profile":"pack_example-orbit-faces_orbital",
        "animation_profile":"pack_example-gentle-motion_float",
        "board":"pack_example-field-board_field",
        "deck":"field",
        "apps":["home","map","expedition"],
        "capabilities":["display"],
        "checklist":["Check GPS","Start Expedition"]
    }))
    return p


def test_enabled_mission_pack_discovers_namespaced_experience(tmp_path: Path):
    root=tmp_path/"installed";_mission_pack(root)
    state=State({
        "capabilities.present":["display"],
        "packs.items":[{"id":"field-experience","origin":"installed","enabled":True,"requirements_met":True}]
    })
    engine=MissionPackEngine(state,root=str(tmp_path/"missions"),pack_root=str(root))
    patch=engine.tick()
    rows=[r for r in patch["missions.items"] if r.get("source_pack")]
    assert len(rows)==1
    assert rows[0]["id"].startswith("pack_field-experience_")
    assert rows[0]["experience"] is True
    assert rows[0]["theme"]=="orchard_example"
    assert rows[0]["requirements_met"] is True
    assert patch["missions.experience_apply_enabled"] is False


def test_disabled_mission_pack_is_not_discovered(tmp_path: Path):
    root=tmp_path/"installed";_mission_pack(root,False)
    engine=MissionPackEngine(State({"capabilities.present":[]}),root=str(tmp_path/"missions"),pack_root=str(root))
    assert not [r for r in engine.catalog() if r.get("source_pack")]


def test_mission_pack_activation_is_content_only(tmp_path: Path):
    root=tmp_path/"installed";_mission_pack(root)
    plan=PackActivationManager(State(),installed_root=root).plan("field-experience",True)
    assert plan["allowed"] is True
    assert plan["executes_code"] is False
    assert plan["activation_tier"]=="content_only"


def test_pack_requirements_flow_into_experience_readiness(tmp_path: Path):
    root=tmp_path/"installed";_mission_pack(root)
    state=State({
        "capabilities.present":["display"],
        "packs.items":[{"id":"field-experience","origin":"installed","enabled":True,"requirements_met":False}]
    })
    row=next(r for r in MissionPackEngine(state,root=str(tmp_path/"missions"),pack_root=str(root)).tick()["missions.items"] if r.get("source_pack"))
    assert row["requirements_met"] is False
    assert row["pack_requirements_met"] is False
