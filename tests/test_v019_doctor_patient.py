from beastcore.doctor import BeastDoctor


class _State:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def get(self, key, default=None):
        return self.values.get(key, default)


def test_doctor_patient_identity_is_privacy_light():
    state = _State({
        "system.model": "Raspberry Pi 4 Model B Rev 1.5",
        "system.architecture": "aarch64",
        "system.kernel": "6.6.31+rpt-rpi-v8",
        "system.python.version": "3.13.1",
        "system.os.id": "debian",
        "system.os.version_id": "12",
        "system.os.build_id": "bookworm-test",
        "pwnagotchi.version": "2.9.5.9",
        # Sensitive/live state exists, but must never enter the patient identity.
        "system.hostname": "beast-secret-host",
        "network.default.gateway": "192.0.2.1",
        "gps.latitude": 42.123,
        "gps.longitude": -83.456,
        "wifi.aps": [{"ssid": "private-network", "bssid": "00:11:22:33:44:55"}],
    })
    ident = BeastDoctor(state).patient_identity()

    assert ident == {
        "model": "Raspberry Pi 4 Model B Rev 1.5",
        "architecture": "aarch64",
        "kernel": "6.6.31+rpt-rpi-v8",
        "python_version": "3.13.1",
        "os_id": "debian",
        "os_version_id": "12",
        "os_build_id": "bookworm-test",
        "pwnagotchi_version": "2.9.5.9",
    }
    serialized = repr(ident)
    assert "beast-secret-host" not in serialized
    assert "192.0.2.1" not in serialized
    assert "42.123" not in serialized
    assert "private-network" not in serialized
    assert "00:11:22:33:44:55" not in serialized


def test_doctor_coverage_distinguishes_covered_unavailable_and_unknown():
    state = _State({
        "system.kernel": "6.6",
        "system.architecture": "aarch64",
        "system.temp.cpu_c": 52.0,
        "storage.root.readonly": False,
        "storage.root.used_pct": 33.0,
        "display.framebuffers": [{"name": "fb_ili9486"}],
        "radio.primary.state": "missing",
        "radio.primary.supported_channels": [],
        "gps.state": "unavailable",
        "gps.fix": False,
        "power.telemetry.available": False,
        "power.ups.state": "not_detected",
        "network.route.available": False,
        "network.interfaces": [],
        "pwnagotchi.service.state": "active",
        # Bettercap is intentionally absent -> unknown.
        "plugins.requirements_summary": {},
    })

    coverage = BeastDoctor(state).diagnostic_coverage()
    by_area = {row["area"]: row for row in coverage["items"]}

    assert coverage["count"] == 10
    assert by_area["system"]["status"] == "covered"
    assert by_area["storage"]["status"] == "covered"
    assert by_area["display"]["status"] == "covered"
    assert by_area["radio"]["status"] == "unavailable"
    assert by_area["gps"]["status"] == "unavailable"
    # False/negative observations are still evidence: Doctor can diagnose them.
    assert by_area["power_telemetry"]["status"] == "covered"
    assert by_area["network"]["status"] == "covered"
    assert by_area["pwnagotchi_service"]["status"] == "covered"
    assert by_area["bettercap_service"]["status"] == "unknown"
    assert by_area["plugins"]["status"] == "covered"
    assert coverage["counts"] == {"covered": 7, "unavailable": 2, "unknown": 1}
    assert coverage["complete"] is False


def test_doctor_snapshot_and_state_patch_publish_patient_awareness():
    state = _State({
        "system.model": "Raspberry Pi 4",
        "system.architecture": "aarch64",
        "system.kernel": "6.6",
        "system.python.version": "3.13.1",
        "system.os.id": "debian",
        "radio.primary.state": "available",
        "gps.state": "connected_no_fix",
        "storage.root.readonly": False,
        "display.framebuffers": [],
        "network.route.available": True,
        "power.telemetry.available": False,
        "pwnagotchi.service.state": "active",
        "bettercap.state": "active",
        "plugins.requirements_summary": {},
        "plugins.provider_decisions": {},
    })
    doctor = BeastDoctor(state)

    snap = doctor.snapshot()
    assert snap["patient"]["privacy_class"] == "technical_identity_only"
    assert snap["patient"]["identity"]["model"] == "Raspberry Pi 4"
    assert snap["patient"]["coverage"]["count"] == 10

    patch = doctor.state_patch()
    assert patch["doctor.patient.identity"]["architecture"] == "aarch64"
    assert patch["doctor.coverage"]["schema"] == 1
    assert (
        patch["doctor.coverage.covered_count"]
        + patch["doctor.coverage.unavailable_count"]
        + patch["doctor.coverage.unknown_count"]
        == 10
    )
