from __future__ import annotations

import json
from pathlib import Path

from beastcore.depot_catalog import DepotCatalog, clean_depot_entry, DepotCatalogError


def entry(**extra):
    row={
        "id":"field-layouts",
        "label":"Field Layouts",
        "version":"1.0.0",
        "pack_type":"layout",
        "resource_class":"none",
        "thermal_class":"static",
        "source":{
            "type":"github_release",
            "repository":"example/field-layouts",
            "asset":"field-layouts-*.zip",
            "sha256_asset":"field-layouts-*.zip.sha256",
        },
    }
    row.update(extra)
    return row


def test_depot_entry_normalizes_github_source():
    row=entry()
    out=clean_depot_entry(row)
    assert out["source"]["repository"]=="example/field-layouts"
    assert out["pack_type"]=="layout"


def test_depot_catalog_is_discovery_only(tmp_path: Path):
    fp=tmp_path/"catalog.json"
    fp.write_text(json.dumps({"schema":1,"channel":"stable","packs":[entry()]}))
    out=DepotCatalog(fp).load()
    assert out["count"]==1
    assert out["grants_trust"] is False
    assert out["installs_packs"] is False


def test_depot_catalog_isolates_bad_entries(tmp_path: Path):
    fp=tmp_path/"catalog.json"
    fp.write_text(json.dumps({"schema":1,"packs":[entry(),{"id":"bad"}]}))
    out=DepotCatalog(fp).load()
    assert out["count"]==1
    assert out["error_count"]==1


def test_catalog_rejects_non_github_release_source():
    try:
        clean_depot_entry(entry(source={"type":"url","url":"https://example.com/a.zip","asset":"a.zip"}))
    except DepotCatalogError:
        pass
    else:
        raise AssertionError("v1 Depot must stay on the bounded GitHub release source model")
