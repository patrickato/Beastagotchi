from __future__ import annotations

import io
import json
import tarfile
import zipfile
from pathlib import Path

import pytest

from beastcore.pack_intake import PackIntakeError, PackIntakeManager


MANIFEST = {
    "id": "demo-theme",
    "label": "Demo Theme",
    "version": "0.1.0",
    "pack_type": "theme",
    "resource_class": "none",
    "thermal_class": "static",
}


def _tar_pack(path: Path, *, unsafe: bool = False) -> None:
    with tarfile.open(path, "w:gz") as tf:
        data = json.dumps(MANIFEST).encode()
        info = tarfile.TarInfo("demo-theme/manifest.json")
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))
        body = b"theme data"
        name = "../escape.txt" if unsafe else "demo-theme/theme.json"
        info = tarfile.TarInfo(name)
        info.size = len(body)
        tf.addfile(info, io.BytesIO(body))


def _zip_pack(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("demo-theme/manifest.json", json.dumps(MANIFEST))
        zf.writestr("demo-theme/theme.json", "{}")


def test_pack_intake_inspects_and_stages_without_installing(tmp_path: Path):
    inbox = tmp_path / "inbox"
    staged = tmp_path / "staged"
    inbox.mkdir()
    archive = inbox / "demo.tar.gz"
    _tar_pack(archive)
    mgr = PackIntakeManager(inbox, staged)

    check = mgr.inspect(archive.name)
    assert check["ok"] is True
    assert check["manifest"]["id"] == "demo-theme"
    assert check["executes_code"] is False
    assert check["installs_files"] is False

    out = mgr.stage(archive.name)
    assert out["ok"] is True and out["staged"] is True
    assert out["installed"] is False and out["enabled"] is False
    assert (staged / "demo-theme" / "manifest.json").is_file()
    state = json.loads((staged / "demo-theme" / "state.json").read_text())
    assert state["state"] == "verified"
    assert state["enabled"] is False


def test_pack_intake_rejects_path_traversal(tmp_path: Path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    archive = inbox / "bad.tar.gz"
    _tar_pack(archive, unsafe=True)
    mgr = PackIntakeManager(inbox, tmp_path / "staged")
    with pytest.raises(PackIntakeError):
        mgr.inspect(archive.name)


def test_pack_intake_zip_is_supported(tmp_path: Path):
    inbox = tmp_path / "inbox"
    staged = tmp_path / "staged"
    inbox.mkdir()
    archive = inbox / "demo.zip"
    _zip_pack(archive)
    mgr = PackIntakeManager(inbox, staged)
    assert mgr.inspect(archive.name)["archive_type"] == "zip"
    assert mgr.stage(archive.name)["pack"]["pack_type"] == "theme"


def test_pack_intake_requires_explicit_replace(tmp_path: Path):
    inbox = tmp_path / "inbox"
    staged = tmp_path / "staged"
    inbox.mkdir()
    archive = inbox / "demo.tar.gz"
    _tar_pack(archive)
    mgr = PackIntakeManager(inbox, staged)
    mgr.stage(archive.name)
    plan = mgr.plan_stage(archive.name)
    assert plan["allowed"] is False
    assert "explicit replace" in plan["blockers"][0]
    assert mgr.stage(archive.name, replace=True)["ok"] is True
