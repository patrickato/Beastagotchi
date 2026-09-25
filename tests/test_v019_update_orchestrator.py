from __future__ import annotations

from pathlib import Path

from beastcore.update_orchestrator import PackUpdateOrchestrator, UpdateProbationEvaluator


class State:
    def __init__(self, data):
        self.data = dict(data)
    def get(self, key, default=None):
        return self.data.get(key, default)


class FakeStager:
    def __init__(self, artifact: Path):
        self.artifact = artifact
    def plan(self, component_id):
        return {"allowed": True, "component": component_id, "blockers": []}
    def stage(self, component_id):
        return {"ok": True, "artifact": str(self.artifact), "component": component_id, "verified": True}


class FakeIntake:
    def __init__(self, pack_id="demo-theme", version="2.0"):
        self.pack_id = pack_id
        self.version = version
        self.staged = False
    def inspect(self, name):
        return {"ok": True, "manifest": {"id": self.pack_id, "version": self.version}}
    def stage(self, name, replace=False):
        self.staged = True
        return {"ok": True, "staged": True}


class FakeInstaller:
    def __init__(self):
        self.rolled_back = []
    def install(self, pack_id):
        return {"ok": True, "transaction_id": "pack-123", "pack": {"id": pack_id}}
    def rollback(self, tx):
        self.rolled_back.append(tx)
        return {"ok": True, "rolled_back": True}


def base_state():
    return State({
        "updates.components": [{
            "id": "pack:demo-theme",
            "policy": "auto_install",
            "installed_version": "1.0",
            "available_version": "2.0",
            "update_available": True,
            "source_trusted": True,
            "compatibility": "compatible",
            "auto_stage_eligible": True,
        }],
        "updates.auto_trigger_ready": True,
        "health.core.state": "healthy",
        "pwnagotchi.service.state": "active",
        "bettercap.state": "ready",
        "storage.root.readonly": False,
        "presentation.conflicts": [],
    })


def test_pack_update_orchestrator_applies_verified_inert_update(tmp_path: Path):
    artifact = tmp_path / "demo.zip"
    artifact.write_bytes(b"archive")
    intake = FakeIntake()
    installer = FakeInstaller()
    orch = PackUpdateOrchestrator(
        base_state(), stager=FakeStager(artifact), intake=intake, installer=installer,
        inbox_root=tmp_path/"inbox", history_root=tmp_path/"history"
    )
    out = orch.apply("pack:demo-theme")
    assert out["ok"] is True
    assert out["to_version"] == "2.0"
    assert out["enabled"] is False
    assert intake.staged is True
    assert installer.rolled_back == []
    assert list((tmp_path/"history").glob("*.json"))


def test_pack_update_rejects_manifest_identity_mismatch(tmp_path: Path):
    artifact = tmp_path / "demo.zip"
    artifact.write_bytes(b"archive")
    orch = PackUpdateOrchestrator(
        base_state(), stager=FakeStager(artifact), intake=FakeIntake(pack_id="other-pack"),
        installer=FakeInstaller(), inbox_root=tmp_path/"inbox", history_root=tmp_path/"history"
    )
    try:
        orch.apply("pack:demo-theme")
    except Exception as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("mismatched pack identity must be rejected")


def test_probation_detects_platform_regression():
    st = State({
        "health.core.state": "critical",
        "pwnagotchi.service.state": "failed",
        "bettercap.state": "ready",
        "storage.root.readonly": False,
        "presentation.conflicts": [],
    })
    row = UpdateProbationEvaluator(st).snapshot()
    assert row["ok"] is False
    assert any("core health" in x for x in row["blockers"])


def test_auto_candidates_never_generic_auto_install_core():
    st = base_state()
    st.data["updates.components"].append({
        "id":"beastagotchi","policy":"auto_install","update_available":True,
        "auto_stage_eligible":True,"source_trusted":True,"compatibility":"compatible"
    })
    rows = PackUpdateOrchestrator(
        st, stager=FakeStager(Path("/tmp/nope")), intake=FakeIntake(), installer=FakeInstaller()
    ).auto_candidates()
    beast = next(x for x in rows if x["component"]=="beastagotchi")
    assert beast["action"] == "stage"
    assert "adapter not yet enabled" in beast["reason"]
