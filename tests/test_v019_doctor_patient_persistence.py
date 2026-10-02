from beastcore.db import Store
from beastcore.doctor import BeastDoctor


class _State:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def get(self, key, default=None):
        return self.values.get(key, default)


def _values():
    return {
        "system.model": "Raspberry Pi 4 Model B",
        "system.architecture": "aarch64",
        "system.kernel": "6.6",
        "system.python.version": "3.13.1",
        "system.os.id": "debian",
        "system.os.version_id": "12",
        "pwnagotchi.version": "2.9.5.9",
        "system.temp.cpu_c": 50.0,
        "storage.root.readonly": False,
        "storage.root.used_pct": 21.0,
        "display.framebuffers": [{"name": "fb_ili9486"}],
        "radio.primary.state": "available",
        "gps.state": "connected_no_fix",
        "power.telemetry.available": False,
        "network.route.available": True,
        "network.interfaces": [],
        "pwnagotchi.service.state": "active",
        "bettercap.state": "active",
        "plugins.requirements_summary": {},
        "plugins.provider_decisions": {},
    }


def test_patient_identity_coverage_persist_and_reload(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        doctor = BeastDoctor(_State(_values()), store)
        first = doctor.snapshot()["patient"]["memory"]
        assert first["identity"]["model"] == "Raspberry Pi 4 Model B"
        assert first["coverage"]["count"] == 10
        assert first["updated_at"] is not None

        reloaded = BeastDoctor(_State(_values()), store)
        memory = reloaded.patient.summary()
        assert memory["identity"] == first["identity"]
        assert memory["coverage"] == first["coverage"]
        assert memory["updated_at"] == first["updated_at"]
    finally:
        store.close()


def test_patient_does_not_write_on_identical_doctor_scans():
    class _Store:
        def __init__(self):
            self.value = None
            self.writes = 0

        def get_meta_json(self, key, default=None):
            return self.value if self.value is not None else default

        def set_meta_json(self, key, value):
            import copy
            self.writes += 1
            self.value = copy.deepcopy(value)
            return True

    store = _Store()
    doctor = BeastDoctor(_State(_values()), store)

    doctor.snapshot()
    assert store.writes == 1
    first_updated = doctor.patient.summary()["updated_at"]

    for _ in range(5):
        doctor.snapshot()

    assert store.writes == 1
    assert doctor.patient.summary()["updated_at"] == first_updated


def test_patient_writes_once_when_coverage_materially_changes():
    class _Store:
        def __init__(self):
            self.value = None
            self.writes = 0

        def get_meta_json(self, key, default=None):
            return self.value if self.value is not None else default

        def set_meta_json(self, key, value):
            import copy
            self.writes += 1
            self.value = copy.deepcopy(value)
            return True

    values = _values()
    state = _State(values)
    store = _Store()
    doctor = BeastDoctor(state, store)
    doctor.snapshot()
    assert store.writes == 1

    values["radio.primary.state"] = "missing"
    state.values = values
    doctor.snapshot()
    assert store.writes == 2
    radio = {
        row["area"]: row
        for row in doctor.patient.summary()["coverage"]["items"]
    }["radio"]
    assert radio["status"] == "unavailable"
