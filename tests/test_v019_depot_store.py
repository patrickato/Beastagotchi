from __future__ import annotations

import json
from pathlib import Path

from beastcore.depot_catalog import DepotCatalogStore, DepotCatalogError


def catalog(label="Field Layouts"):
    return {
        "schema":1,
        "channel":"stable",
        "packs":[{
            "id":"field-layouts","label":label,"version":"1.0.0","pack_type":"layout",
            "description":"Reusable field telemetry layouts","author":"Example","tags":["field","dashboard"],
            "resource_class":"none","thermal_class":"static",
            "source":{"type":"github_release","repository":"example/field-layouts","asset":"field-layouts-*.zip","sha256_asset":"field-layouts-*.zip.sha256"}
        }]
    }


def test_catalog_store_normalizes_and_persists(tmp_path: Path):
    store=DepotCatalogStore(tmp_path/"catalogs",clock=lambda:123.0)
    out=store.save("community.json",json.dumps(catalog()).encode())
    assert out["ok"] is True and out["count"]==1
    saved=json.loads((tmp_path/"catalogs"/"community.json").read_text())
    assert saved["imported_at"]==123.0
    assert saved["packs"][0]["id"]=="field-layouts"


def test_combined_catalog_search_and_type_filter(tmp_path: Path):
    store=DepotCatalogStore(tmp_path/"catalogs")
    store.save("a.json",json.dumps(catalog()).encode())
    assert store.combined(query="telemetry")["count"]==1
    assert store.combined(pack_type="theme")["count"]==0
    out=store.combined(pack_type="layout")
    assert out["count"]==1
    assert out["grants_trust"] is False and out["installs_packs"] is False
    assert out["remote_refresh_enabled"] is False


def test_duplicate_ids_are_reported_not_silently_resolved(tmp_path: Path):
    store=DepotCatalogStore(tmp_path/"catalogs")
    store.save("a.json",json.dumps(catalog("A")).encode())
    store.save("b.json",json.dumps(catalog("B")).encode())
    out=store.combined()
    assert out["count"]==2
    assert out["conflicts"][0]["id"]=="field-layouts"


def test_catalog_upload_rejects_non_json_name(tmp_path: Path):
    store=DepotCatalogStore(tmp_path/"catalogs")
    try:store.save("catalog.txt",json.dumps(catalog()).encode())
    except DepotCatalogError:pass
    else:raise AssertionError("non-json Depot filename must be rejected")
