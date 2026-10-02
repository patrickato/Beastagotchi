from beastcore.actions import ActionBroker
from beastcore.db import Store
from beastcore.doctor import BeastDoctor
from beastcore.events import EventBus
from beastcore.state import StateRegistry


def _runtime(tmp_path):
    state = StateRegistry()
    state.update_many("test", {
        "system.model": "Raspberry Pi 4",
        "system.architecture": "aarch64",
        "system.kernel": "6.6",
        "system.python.version": "3.13.1",
        "system.os.id": "debian",
        "system.os.version_id": "12",
        "pwnagotchi.version": "2.9.5.9",
        "system.beast_version": "0.19.0",
        "display.backend.current": "fbdev_rgb565",
        "platform.plugins": [
            {"name": "doctor", "enabled": True, "configured": True, "installed_custom": True},
        ],
        "packs.items": [],
        "providers.preferences": {},
        "plugins.requirements_summary": {},
        "plugins.provider_decisions": {},
    })
    store = Store(str(tmp_path / "beast.db"))
    broker = ActionBroker(state, store, EventBus())
    broker.doctor = BeastDoctor(state, store)
    return state, store, broker


def test_doctor_known_good_action_is_planable_and_audited(tmp_path):
    state, store, broker = _runtime(tmp_path)
    try:
        plan = broker.plan("doctor.known_good_save", {"label": "healthy baseline"})
        assert plan["allowed"] is True
        assert plan["operation"] == "doctor.known_good_save"
        assert any("does not change" in warning for warning in plan["warnings"])

        row = broker.perform(
            "doctor.known_good_save",
            {"label": "healthy baseline"},
            actor="owner",
        )
        assert row["status"] == "success"
        assert row["target"] == "doctor.patient"
        assert row["result"]["saved"] is True
        assert state.get("doctor.patient.known_good_count") == 1
        assert state.get("doctor.patient.known_good_drift")["changed"] is False

        saved = store.recent_actions(10)
        match = next(x for x in saved if x["action"] == "doctor.known_good_save")
        assert match["target"] == "doctor.patient"
        assert match["status"] == "success"
    finally:
        store.close()


def test_doctor_known_good_action_dedupes_unchanged_checkpoint(tmp_path):
    _, store, broker = _runtime(tmp_path)
    try:
        first = broker.perform("doctor.known_good_save", {"label": "one"}, actor="owner")
        second = broker.perform("doctor.known_good_save", {"label": "two"}, actor="owner")
        assert first["result"]["saved"] is True
        assert second["result"]["saved"] is False
        assert second["result"]["reason"] == "unchanged"
        assert broker.doctor.patient.summary()["known_good_count"] == 1
    finally:
        store.close()


def test_doctor_known_good_action_is_blocked_without_doctor(tmp_path):
    state = StateRegistry()
    store = Store(str(tmp_path / "beast.db"))
    broker = ActionBroker(state, store, EventBus())
    try:
        plan = broker.plan("doctor.known_good_save", {})
        assert plan["allowed"] is False
        row = broker.perform("doctor.known_good_save", {}, actor="owner")
        assert row["status"] == "failed"
        assert row["result"]["ok"] is False
    finally:
        store.close()
