from beastcore.db import Store
from beastcore.doctor_patient import DoctorPatientChart
from beastcore.doctor import BeastDoctor


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


class _State:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def get(self, key, default=None):
        return self.values.get(key, default)



def test_doctor_known_good_fingerprint_is_privacy_light():
    values = {
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
            {"name": "foo", "enabled": False, "configured": True, "installed_custom": True},
        ],
        "packs.items": [
            {"id": "field", "version": "1.2", "origin": "installed",
             "enabled": True, "requirements_met": True},
        ],
        "providers.preferences": {"gps": "gpsd"},
        # Must not enter the fingerprint:
        "system.hostname": "secret-host",
        "network.default.gateway": "192.0.2.1",
        "gps.latitude": 42.123,
        "gps.longitude": -83.456,
        "wifi.aps": [{"ssid": "PrivateWifi", "bssid": "00:11:22:33:44:55"}],
    }
    row = BeastDoctor(_State(values)).known_good_fingerprint()
    raw = repr(row)
    assert row["beast_version"] == "0.19.0"
    assert row["plugins"][0]["name"] == "doctor"
    assert row["packs"][0]["id"] == "field"
    assert row["provider_preferences"] == {"gps": "gpsd"}
    for secret in ("secret-host", "192.0.2.1", "42.123", "PrivateWifi", "00:11:22:33:44:55"):
        assert secret not in raw


def test_doctor_save_known_good_then_reports_live_drift(tmp_path):
    store = Store(str(tmp_path / "beast.db"))
    try:
        values = {
            "system.model": "Raspberry Pi 4",
            "system.architecture": "aarch64",
            "system.kernel": "6.6",
            "system.python.version": "3.13.1",
            "system.os.id": "debian",
            "pwnagotchi.version": "2.9.5.9",
            "system.beast_version": "0.19.0",
            "display.backend.current": "fbdev_rgb565",
            "platform.plugins": [
                {"name": "doctor", "enabled": True, "configured": True, "installed_custom": True},
            ],
            "packs.items": [],
            "providers.preferences": {"gps": "gpsd"},
        }
        state = _State(values)
        doctor = BeastDoctor(state, store)
        saved = doctor.save_known_good("healthy baseline")
        assert saved["saved"] is True
        assert doctor.known_good_diff()["changed"] is False

        state.values["platform.plugins"] = [
            {"name": "doctor", "enabled": True, "configured": True, "installed_custom": True},
            {"name": "foo", "enabled": True, "configured": True, "installed_custom": True},
        ]
        state.values["providers.preferences"] = {"gps": "serial"}
        drift = doctor.known_good_diff()
        assert drift["changed"] is True
        assert set(drift["changes"]) == {"plugins", "provider_preferences"}

        snap = doctor.snapshot()
        assert snap["patient"]["known_good"]["history"][0]["label"] == "healthy baseline"
        assert snap["patient"]["known_good"]["drift"]["change_count"] == 2
    finally:
        store.close()
