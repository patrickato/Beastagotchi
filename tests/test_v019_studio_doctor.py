from beaststudio.server import HTML, StudioState


class _Actions:
    def __init__(self):
        self.calls = []

    def plan(self, action, payload=None):
        self.calls.append(("plan", action, dict(payload or {})))
        return {"ok": True, "plan": {"allowed": True, "operation": action}}

    def perform(self, action, payload=None):
        self.calls.append(("perform", action, dict(payload or {})))
        return {
            "ok": True,
            "action_row": {
                "status": "success",
                "action": action,
                "target": "doctor.patient",
                "result": {"ok": True, "saved": True},
            },
        }


def _studio(tmp_path):
    prefs = tmp_path / "preferences.json"
    prefs.write_text("{}")
    st = StudioState(
        str(tmp_path),
        str(prefs),
        str(tmp_path / "studio.token"),
    )
    st.actions = _Actions()
    return st


def test_studio_exposes_doctor_known_good_command_center_control():
    assert 'id="opsDoctor"' in HTML
    assert "SAVE KNOWN-GOOD BASELINE" in HTML
    assert "saveDoctorKnownGood" in HTML
    assert "/api/doctor-known-good-plan" in HTML
    assert "/api/doctor-known-good-save" in HTML
    assert "privacy-light build/configuration identity only" in HTML


def test_studio_doctor_known_good_uses_audited_action_client(tmp_path):
    st = _studio(tmp_path)

    plan = st.doctor_known_good_plan({"label": "healthy baseline"})
    saved = st.doctor_known_good_save({"label": "healthy baseline"})

    assert plan["plan"]["allowed"] is True
    assert saved["action_row"]["target"] == "doctor.patient"
    assert st.actions.calls == [
        ("plan", "doctor.known_good_save", {"label": "healthy baseline"}),
        ("perform", "doctor.known_good_save", {"label": "healthy baseline"}),
    ]


def test_studio_doctor_known_good_label_is_bounded(tmp_path):
    st = _studio(tmp_path)
    label = "x" * 200

    st.doctor_known_good_plan({"label": label})
    assert st.actions.calls[0][2]["label"] == "x" * 80
