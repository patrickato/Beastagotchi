from beastcore.db import Store
from beastcore.doctor_patient import DoctorPatientChart


def test_known_good_generations_are_bounded_deduped_and_persistent(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        chart = DoctorPatientChart(store, clock=lambda: 100.0, max_known_good=3)
        fp1 = {"identity": {"kernel": "6.6"}, "plugins": ["a"], "packs": []}
        fp2 = {"identity": {"kernel": "6.6"}, "plugins": ["a", "b"], "packs": []}
        fp3 = {"identity": {"kernel": "6.7"}, "plugins": ["a", "b"], "packs": []}
        fp4 = {"identity": {"kernel": "6.8"}, "plugins": ["a", "b"], "packs": []}

        first = chart.save_known_good(fp1, label="healthy", now=1)
        assert first["saved"] is True
        duplicate = chart.save_known_good(fp1, label="same", now=2)
        assert duplicate["saved"] is False
        assert duplicate["reason"] == "unchanged"

        chart.save_known_good(fp2, now=3)
        chart.save_known_good(fp3, now=4)
        chart.save_known_good(fp4, now=5)

        assert chart.summary()["known_good_count"] == 3
        history = chart.known_good_history()
        assert len(history) == 3
        assert history[0]["saved_at"] == 5
        assert history[-1]["saved_at"] == 3

        reloaded = DoctorPatientChart(store, max_known_good=3)
        assert reloaded.summary()["known_good_count"] == 3
        assert reloaded.known_good_history()[0]["saved_at"] == 5
    finally:
        store.close()


def test_known_good_diff_reports_only_changed_top_level_sections(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        chart = DoctorPatientChart(store)
        baseline = {
            "identity": {"kernel": "6.6", "python": "3.13"},
            "plugins": [{"name": "doctor", "enabled": True}],
            "packs": [{"id": "field", "version": "1"}],
            "provider_preferences": {"gps": "gpsd"},
        }
        chart.save_known_good(baseline, now=10)

        same = chart.diff_known_good(baseline)
        assert same["found"] is True
        assert same["changed"] is False
        assert same["change_count"] == 0

        current = dict(baseline)
        current["plugins"] = [{"name": "doctor", "enabled": True}, {"name": "foo", "enabled": True}]
        current["provider_preferences"] = {"gps": "serial"}

        drift = chart.diff_known_good(current)
        assert drift["changed"] is True
        assert drift["change_count"] == 2
        assert set(drift["changes"]) == {"plugins", "provider_preferences"}
        assert drift["checkpoint"]["saved_at"] == 10
    finally:
        store.close()
