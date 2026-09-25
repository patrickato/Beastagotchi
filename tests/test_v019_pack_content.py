from __future__ import annotations

import json
from pathlib import Path

from beastui.pack_content import discover_enabled_pack_boards, discover_enabled_pack_layouts


def _pack(root: Path, pack_id: str, pack_type: str):
    p=root/pack_id
    p.mkdir(parents=True)
    (p/"manifest.json").write_text(json.dumps({
        "id":pack_id,"label":pack_id,"version":"1","pack_type":pack_type,
        "resource_class":"none","thermal_class":"static"
    }))
    (p/"state.json").write_text(json.dumps({"state":"enabled","enabled":True}))
    return p


def _widgets():
    return [{"id":"cpu","key":"system.cpu.total","label":"CPU","style":"radial","x":0,"y":0,"w":4,"h":3,"min":0,"max":100}]


def test_board_pack_becomes_scoped_readonly_destination(tmp_path: Path):
    root=tmp_path/"installed";p=_pack(root,"field.boards","board")
    (p/"boards").mkdir()
    (p/"boards"/"field.json").write_text(json.dumps({"id":"field","label":"Field Board","widgets":_widgets()}))
    rows=discover_enabled_pack_boards(root)
    assert len(rows)==1
    assert rows[0]["readonly"] is True
    assert rows[0]["source_pack"]=="field.boards"
    assert rows[0]["id"].startswith("pack_field_boards_")


def test_disabled_board_pack_is_not_discovered(tmp_path: Path):
    root=tmp_path/"installed";p=_pack(root,"field.boards","board")
    (p/"boards").mkdir()
    (p/"boards"/"field.json").write_text(json.dumps({"id":"field","label":"Field Board","widgets":_widgets()}))
    (p/"state.json").write_text(json.dumps({"state":"disabled","enabled":False}))
    assert discover_enabled_pack_boards(root)==[]


def test_layout_pack_is_template_not_board_destination(tmp_path: Path):
    root=tmp_path/"installed";p=_pack(root,"layouts.one","layout")
    (p/"layouts").mkdir()
    (p/"layouts"/"triad.json").write_text(json.dumps({
        "id":"triad","label":"Triad","description":"Three-instrument starting point","widgets":_widgets()
    }))
    layouts=discover_enabled_pack_layouts(root)
    assert len(layouts)==1
    assert layouts[0]["source_kind"]=="pack_layout"
    assert layouts[0]["readonly"] is True
    assert discover_enabled_pack_boards(root)==[]


def test_invalid_pack_json_is_ignored_without_breaking_catalog(tmp_path: Path):
    root=tmp_path/"installed";p=_pack(root,"broken","board")
    (p/"boards").mkdir()
    (p/"boards"/"broken.json").write_text("{nope")
    assert discover_enabled_pack_boards(root)==[]
