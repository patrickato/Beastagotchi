from __future__ import annotations

import json
from pathlib import Path

from beastcore.pack_activation import PackActivationManager
from beastui.theme import discover_enabled_pack_themes


class State:
    def get(self, key, default=None):
        return default


def _installed_theme(root: Path, pack_id="nice-theme"):
    p=root/pack_id
    (p/"themes").mkdir(parents=True)
    (p/"manifest.json").write_text(json.dumps({
        "id":pack_id,"label":"Nice Theme Pack","version":"1.0",
        "pack_type":"theme","resource_class":"none","thermal_class":"static",
    }))
    (p/"state.json").write_text(json.dumps({
        "state":"installed","enabled":False,"activation_state":"inactive"
    }))
    (p/"themes"/"orchard.json").write_text(json.dumps({
        "id":"orchard","label":"Orchard","colors":{"bg":"#101010","text":"#eeeeee","primary":"#88aa44"}
    }))
    return p


def test_content_theme_activation_is_registry_only(tmp_path: Path):
    root=tmp_path/"installed";p=_installed_theme(root)
    mgr=PackActivationManager(State(),installed_root=root,clock=lambda:100.0)
    plan=mgr.plan("nice-theme",True)
    assert plan["allowed"] is True and plan["executes_code"] is False
    out=mgr.set_enabled("nice-theme",True)
    assert out["enabled"] is True
    row=json.loads((p/"state.json").read_text())
    assert row["state"]=="enabled" and row["activation_tier"]=="content_only"


def test_code_file_blocks_content_only_activation(tmp_path: Path):
    root=tmp_path/"installed";p=_installed_theme(root)
    (p/"evil.py").write_text("print('no')")
    plan=PackActivationManager(State(),installed_root=root).plan("nice-theme",True)
    assert plan["allowed"] is False
    assert any("code-like" in x for x in plan["blockers"])


def test_theme_pack_cannot_declare_services_or_permissions(tmp_path: Path):
    root=tmp_path/"installed";p=_installed_theme(root)
    obj=json.loads((p/"manifest.json").read_text())
    obj["services"]=["thing.service"];obj["permissions"]=["root"]
    (p/"manifest.json").write_text(json.dumps(obj))
    plan=PackActivationManager(State(),installed_root=root).plan("nice-theme",True)
    assert plan["allowed"] is False


def test_enabled_pack_theme_discovery(tmp_path: Path):
    root=tmp_path/"installed";p=_installed_theme(root)
    assert discover_enabled_pack_themes(root)=={}
    PackActivationManager(State(),installed_root=root).set_enabled("nice-theme",True)
    found=discover_enabled_pack_themes(root)
    assert found["orchard"] == p/"themes"/"orchard.json"
