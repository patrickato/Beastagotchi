from __future__ import annotations

from pathlib import Path

from beastcore.update_automation import UpdateAutomationEngine


class FakeState:
    def __init__(self, data):
        self.data = dict(data)

    def get(self, key, default=None):
        return self.data.get(key, default)


class FakeBroker:
    def __init__(self, ok=True):
        self.ok = ok
        self.calls = []

    def perform(self, action, payload, *, actor="local"):
        self.calls.append((action, dict(payload), actor))
        return {
            "id": "action-1",
            "status": "success" if self.ok else "failed",
            "result": {
                "ok": self.ok,
                "path": "/stage/example" if self.ok else None,
                "sha256": "a" * 64 if self.ok else None,
                "error": None if self.ok else "simulated failure",
            },
        }


def update_row(policy="auto_stage", eligible=True):
    return {
        "id": "beastagotchi",
        "policy": policy,
        "update_available": True,
        "available_version": "v0.20.0",
        "auto_stage_eligible": eligible,
    }


def test_auto_stage_runs_once_and_is_deduplicated(tmp_path: Path):
    state = FakeState({
        "updates.components": [update_row()],
        "updates.auto_trigger_ready": True,
    })
    broker = FakeBroker()
    engine = UpdateAutomationEngine(
        state, broker, path=tmp_path / "automation.json", clock=lambda: 1000.0
    )

    first = engine.tick()
    assert first["update_automation.status"] == "staged"
    assert len(broker.calls) == 1
    assert broker.calls[0][0] == "update.stage"
    assert broker.calls[0][2] == "automation:update"

    second = engine.tick()
    assert len(broker.calls) == 1
    assert second["update_automation.status"] == "idle"


def test_auto_stage_waits_until_docked_online(tmp_path: Path):
    state = FakeState({
        "updates.components": [update_row()],
        "updates.auto_trigger_ready": False,
    })
    broker = FakeBroker()
    patch = UpdateAutomationEngine(
        state, broker, path=tmp_path / "automation.json"
    ).tick()
    assert patch["update_automation.status"] == "waiting_for_dock_and_internet"
    assert broker.calls == []


def test_auto_install_policy_for_core_stages_but_does_not_apply(tmp_path: Path):
    state = FakeState({
        "updates.components": [update_row(policy="auto_install")],
        "updates.auto_trigger_ready": True,
    })
    broker = FakeBroker()
    patch = UpdateAutomationEngine(
        state, broker, path=tmp_path / "automation.json", clock=lambda: 1000.0
    ).tick()
    assert patch["update_automation.last"]["install_pending"] is True
    assert patch["update_automation.auto_install_scope"] == "inert_beast_packs_only"
    assert [x[0] for x in broker.calls] == ["update.stage"]


def test_auto_install_policy_applies_beast_pack_transaction(tmp_path: Path):
    row=update_row(policy="auto_install")
    row["id"]="pack:demo-theme"
    state=FakeState({"updates.components":[row],"updates.auto_trigger_ready":True})
    broker=FakeBroker()
    patch=UpdateAutomationEngine(state,broker,path=tmp_path/"automation.json",clock=lambda:1000.0).tick()
    assert [x[0] for x in broker.calls] == ["update.pack_apply"]
    assert patch["update_automation.last"]["status"] == "installed"
    assert patch["update_automation.last"]["pack_auto_installed"] is True
    assert patch["update_automation.last"]["install_pending"] is False


def test_ineligible_update_is_blocked_not_downloaded(tmp_path: Path):
    state = FakeState({
        "updates.components": [update_row(eligible=False)],
        "updates.auto_trigger_ready": True,
    })
    broker = FakeBroker()
    patch = UpdateAutomationEngine(
        state, broker, path=tmp_path / "automation.json"
    ).tick()
    assert patch["update_automation.status"] == "blocked"
    assert patch["update_automation.blocked_count"] == 1
    assert broker.calls == []


def test_failed_stage_has_retry_backoff(tmp_path: Path):
    now = [1000.0]
    state = FakeState({
        "updates.components": [update_row()],
        "updates.auto_trigger_ready": True,
    })
    broker = FakeBroker(ok=False)
    engine = UpdateAutomationEngine(
        state,
        broker,
        path=tmp_path / "automation.json",
        clock=lambda: now[0],
        retry_sec=3600,
    )
    assert engine.tick()["update_automation.status"] == "failed"
    assert len(broker.calls) == 1
    now[0] += 100
    engine.tick()
    assert len(broker.calls) == 1
    now[0] += 4000
    engine.tick()
    assert len(broker.calls) == 2
