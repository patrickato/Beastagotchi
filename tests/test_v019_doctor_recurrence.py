from beastcore.db import Store
from beastcore.doctor_patient import DoctorPatientChart


def test_patient_recurrence_is_derived_from_incident_history(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        store.open_incident({
            "id": "i1",
            "kind": "service.bettercap",
            "severity": "critical",
            "opened_at": 10,
            "last_seen": 12,
            "summary": "Bettercap service unavailable",
            "detail": "state=failed",
            "snapshot": {},
        })
        assert store.resolve_incident("service.bettercap", 20) == 1
        store.open_incident({
            "id": "i2",
            "kind": "service.bettercap",
            "severity": "critical",
            "opened_at": 30,
            "last_seen": 31,
            "summary": "Bettercap service unavailable again",
            "detail": "state=failed",
            "snapshot": {},
        })

        chart = DoctorPatientChart(store, clock=lambda: 40)
        assert chart.refresh_recurrence() is True
        row = chart.summary()["recurrence"]["service.bettercap"]
        assert row["episodes"] == 2
        assert row["recurrent"] is True
        assert row["active"] is True
        assert row["first_seen"] == 10
        assert row["last_seen"] == 31
        assert row["last_resolved"] == 20
        assert row["severity"] == "critical"

        # Identical IncidentEngine history does not cause another chart write.
        assert chart.refresh_recurrence() is False

        reloaded = DoctorPatientChart(store)
        persisted = reloaded.summary()["recurrence"]["service.bettercap"]
        assert persisted["episodes"] == 2
        assert persisted["active"] is True
    finally:
        store.close()


def test_recurrence_memory_is_bounded_to_64_kinds(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        for idx in range(70):
            store.open_incident({
                "id": f"i{idx}",
                "kind": f"test.kind_{idx:02d}",
                "severity": "warning",
                "opened_at": idx + 1,
                "last_seen": idx + 1,
                "summary": f"Incident {idx}",
                "detail": "",
                "snapshot": {},
            })
        chart = DoctorPatientChart(store)
        chart.refresh_recurrence()
        recurrence = chart.summary()["recurrence"]
        assert len(recurrence) == 64
        assert "test.kind_69" in recurrence
        assert "test.kind_00" not in recurrence
    finally:
        store.close()
