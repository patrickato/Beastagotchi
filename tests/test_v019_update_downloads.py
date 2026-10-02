from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from beastcore.update_downloads import UpdateStageError, VerifiedUpdateStager


class FakeState:
    def __init__(self, rows):
        self.rows = rows

    def get(self, key, default=None):
        return self.rows if key == "updates.components" else default


class FakeChecker:
    def __init__(self, release):
        self.release = release
        self.calls = []

    def latest(self, repo):
        self.calls.append(repo)
        return self.release


class FakeFetcher:
    def __init__(self, mapping):
        self.mapping = dict(mapping)
        self.calls = []

    def fetch_bytes(self, url, *, max_bytes):
        self.calls.append(url)
        data = self.mapping[url]
        if len(data) > max_bytes:
            raise UpdateStageError("too large")
        return data


def component(repo="patrickato/Beastagotchi"):
    return [{
        "id": "beastagotchi",
        "label": "Beastagotchi",
        "installed_version": "0.19.0",
        "available_version": "v0.20.0",
        "update_available": True,
        "source_type": "github_release",
        "source": repo,
        "repository": repo,
        "source_trusted": True,
    }]


def release_for(data: bytes, *, direct=True):
    digest = hashlib.sha256(data).hexdigest()
    asset = {
        "id": 1,
        "name": "Beastagotchi_v0.20.0.tar.gz",
        "size_bytes": len(data),
        "digest": f"sha256:{digest}" if direct else "",
        "download_url": "https://github.com/patrickato/Beastagotchi/releases/download/v0.20.0/Beastagotchi_v0.20.0.tar.gz",
    }
    rows = [asset]
    if not direct:
        rows.append({
            "id": 2,
            "name": "Beastagotchi_v0.20.0.tar.gz.sha256",
            "size_bytes": 100,
            "digest": "",
            "download_url": "https://github.com/patrickato/Beastagotchi/releases/download/v0.20.0/Beastagotchi_v0.20.0.tar.gz.sha256",
        })
    return {"repository":"patrickato/Beastagotchi","version":"v0.20.0","assets":rows}


def test_verified_update_stager_accepts_direct_github_sha256(tmp_path: Path):
    data = b"verified release bytes"
    rel = release_for(data, direct=True)
    url = rel["assets"][0]["download_url"]
    stager = VerifiedUpdateStager(
        FakeState(component()),
        root=tmp_path/"staged",
        trust_path=tmp_path/"trust.json",
        checker=FakeChecker(rel),
        fetcher=FakeFetcher({url:data}),
    )
    plan = stager.plan("beastagotchi")
    assert plan["allowed"] is True and plan["direct_sha256"] is True
    out = stager.stage("beastagotchi")
    assert out["ok"] is True and out["verified"] is True
    assert out["installed"] is False and out["executed"] is False
    meta = json.loads((Path(out["path"])/"metadata.json").read_text())
    assert meta["sha256"] == hashlib.sha256(data).hexdigest()


def test_verified_update_stager_accepts_matching_sidecar(tmp_path: Path):
    data = b"release with sidecar"
    rel = release_for(data, direct=False)
    artifact, sidecar = rel["assets"]
    digest = hashlib.sha256(data).hexdigest()
    sidecar_data = f"{digest}  {artifact['name']}\n".encode()
    stager = VerifiedUpdateStager(
        FakeState(component()),
        root=tmp_path/"staged",
        trust_path=tmp_path/"trust.json",
        checker=FakeChecker(rel),
        fetcher=FakeFetcher({artifact["download_url"]:data, sidecar["download_url"]:sidecar_data}),
    )
    assert stager.stage("beastagotchi")["verified"] is True


def test_verified_update_stager_rejects_hash_mismatch(tmp_path: Path):
    expected = b"expected"
    actual = b"tampered"
    rel = release_for(expected, direct=True)
    url = rel["assets"][0]["download_url"]
    stager = VerifiedUpdateStager(
        FakeState(component()),
        root=tmp_path/"staged",
        trust_path=tmp_path/"trust.json",
        checker=FakeChecker(rel),
        fetcher=FakeFetcher({url:actual}),
    )
    with pytest.raises(UpdateStageError):
        stager.stage("beastagotchi")


def test_verified_update_stager_refuses_untrusted_repo(tmp_path: Path):
    data = b"something"
    rel = {
        "repository":"randomperson/random",
        "version":"v2",
        "assets":[{
            "id":1,"name":"random.zip","size_bytes":len(data),
            "digest":"sha256:"+hashlib.sha256(data).hexdigest(),
            "download_url":"https://github.com/randomperson/random/releases/download/v2/random.zip",
        }]
    }
    rows = component("randomperson/random")
    stager = VerifiedUpdateStager(
        FakeState(rows), root=tmp_path/"staged", trust_path=tmp_path/"trust.json",
        checker=FakeChecker(rel), fetcher=FakeFetcher({rel["assets"][0]["download_url"]:data}),
    )
    plan = stager.plan("beastagotchi")
    assert plan["allowed"] is False
    assert any("not trusted" in x for x in plan["blockers"])


def test_pwnagotchi_platform_update_requires_dedicated_adapter(tmp_path: Path):
    rows=[{
        "id":"pwnagotchi","installed_version":"2.9","available_version":"3.0",
        "update_available":True,"source_type":"github_release",
        "source":"jayofelony/pwnagotchi","repository":"jayofelony/pwnagotchi","source_trusted":True,
    }]
    rel={"repository":"jayofelony/pwnagotchi","version":"3.0","assets":[]}
    stager=VerifiedUpdateStager(FakeState(rows),root=tmp_path/"staged",trust_path=tmp_path/"trust.json",checker=FakeChecker(rel),fetcher=FakeFetcher({}))
    plan=stager.plan("pwnagotchi")
    assert plan["allowed"] is False
    assert any("dedicated platform-update adapter" in x for x in plan["blockers"])
