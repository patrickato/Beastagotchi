from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

from beastcore.pack_intake import PackIntakeManager
from beastcore.pack_install import PackInstallManager
from beaststudio.pack_files import PackFileManager


class FakeState:
    def __init__(self, data=None):
        self.data = dict(data or {})

    def get(self, key, default=None):
        return self.data.get(key, default)


def make_archive(path: Path, version: str, *, dependencies=None, compatibility=None) -> None:
    manifest = {
        "id": "demo-theme",
        "label": "Demo Theme",
        "version": version,
        "pack_type": "theme",
        "resource_class": "none",
        "thermal_class": "static",
        "dependencies": list(dependencies or []),
        "compatibility": compatibility or {},
    }
    with tarfile.open(path, "w:gz") as tf:
        for name, body in {
            "demo-theme/manifest.json": json.dumps(manifest).encode(),
            "demo-theme/theme.json": json.dumps({"version": version}).encode(),
        }.items():
            info = tarfile.TarInfo(name)
            info.size = len(body)
            tf.addfile(info, io.BytesIO(body))


def setup_staged(tmp_path: Path, version: str = "1.0", **kwargs):
    inbox = tmp_path / "inbox"
    staged = tmp_path / "staged"
    inbox.mkdir(exist_ok=True)
    archive = inbox / "demo.tar.gz"
    make_archive(archive, version, **kwargs)
    PackIntakeManager(inbox, staged).stage(archive.name, replace=True)
    return inbox, staged


def test_transactional_pack_install_is_inert_and_verified(tmp_path: Path):
    _, staged = setup_staged(tmp_path, "1.0")
    state = FakeState({"capabilities.present": [], "packs.items": [], "system.beast_version": "0.19.0", "pwnagotchi.version": "2.9.5.9"})
    mgr = PackInstallManager(state, staged_root=staged, installed_root=tmp_path/"installed", transactions_root=tmp_path/"tx")
    plan = mgr.plan_install("demo-theme")
    assert plan["allowed"] is True and plan["activation_included"] is False
    out = mgr.install("demo-theme")
    assert out["ok"] is True and out["enabled"] is False and out["activation_performed"] is False
    verify = mgr.verify_installed("demo-theme", expected_transaction=out["transaction_id"])
    assert verify["ok"] is True
    assert verify["state"]["activation_state"] == "inactive"
    assert mgr.history()[0]["status"] == "installed"


def test_pack_update_can_roll_back_previous_registry_copy(tmp_path: Path):
    _, staged = setup_staged(tmp_path, "1.0")
    state = FakeState({"capabilities.present": [], "packs.items": [], "system.beast_version": "0.19.0", "pwnagotchi.version": "2.9.5.9"})
    mgr = PackInstallManager(state, staged_root=staged, installed_root=tmp_path/"installed", transactions_root=tmp_path/"tx")
    first = mgr.install("demo-theme")
    assert first["ok"]

    # Replace the verified staged copy with v2, then install over v1.
    setup_staged(tmp_path, "2.0")
    second = mgr.install("demo-theme")
    assert second["rollback_available"] is True
    assert mgr.verify_installed("demo-theme")["pack"]["version"] == "2.0"
    rb = mgr.rollback(second["transaction_id"])
    assert rb["ok"] is True and rb["restored_previous"] is True
    assert mgr.verify_installed("demo-theme")["pack"]["version"] == "1.0"


def test_pack_install_blocks_missing_dependency(tmp_path: Path):
    _, staged = setup_staged(tmp_path, "1.0", dependencies=["required-pack"])
    state = FakeState({"capabilities.present": [], "packs.items": [], "system.beast_version": "0.19.0", "pwnagotchi.version": "2.9.5.9"})
    mgr = PackInstallManager(state, staged_root=staged, installed_root=tmp_path/"installed", transactions_root=tmp_path/"tx")
    plan = mgr.plan_install("demo-theme")
    assert plan["allowed"] is False
    assert plan["missing_dependencies"] == ["required-pack"]


def test_pack_install_checks_declared_version_bounds(tmp_path: Path):
    _, staged = setup_staged(tmp_path, "1.0", compatibility={"beast_min": "0.20.0"})
    state = FakeState({"capabilities.present": [], "packs.items": [], "system.beast_version": "0.19.0", "pwnagotchi.version": "2.9.5.9"})
    mgr = PackInstallManager(state, staged_root=staged, installed_root=tmp_path/"installed", transactions_root=tmp_path/"tx")
    plan = mgr.plan_install("demo-theme")
    assert plan["allowed"] is False
    assert any("below required" in x for x in plan["blockers"])


def test_stale_transaction_cannot_overwrite_newer_install(tmp_path: Path):
    _, staged = setup_staged(tmp_path, "1.0")
    state = FakeState({"capabilities.present": [], "packs.items": [], "system.beast_version": "0.19.0", "pwnagotchi.version": "2.9.5.9"})
    mgr = PackInstallManager(state, staged_root=staged, installed_root=tmp_path/"installed", transactions_root=tmp_path/"tx")
    first = mgr.install("demo-theme")
    setup_staged(tmp_path, "2.0")
    mgr.install("demo-theme")
    assert mgr.plan_rollback(first["transaction_id"])["allowed"] is False


def test_pack_file_manager_only_accepts_pack_archives(tmp_path: Path):
    mgr = PackFileManager(tmp_path)
    row = mgr.save("theme.zip", b"PK-demo")
    assert row["ok"] and (tmp_path/"theme.zip").is_file()
    try:
        mgr.save("theme.py", b"print('x')")
    except Exception:
        pass
    else:
        raise AssertionError("non-archive upload must be rejected")
