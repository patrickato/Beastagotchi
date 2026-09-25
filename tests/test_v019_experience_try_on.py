from beastcore.experience_try_on import ExperienceTryOnPlanner


class State:
    def __init__(self, data=None):
        self.data = dict(data or {})

    def get(self, key, default=None):
        return self.data.get(key, default)


def _state(*, native=True, offscreen=False, executor=False):
    render_target = {
        "display_class": "reference" if native else "medium",
        "requested_size": [480, 320] if native else [800, 480],
        "native_supported": native,
        "render_mode": "native_reference" if native else "native_variant_required",
        "reflow_required": not native,
    }
    return State({
        "experience.compiler.plan": {
            "items": [{
                "experience_id": "monolith",
                "label": "Monolith",
                "ready_for_preview": True,
                "page_coverage": {
                    "implemented": ["home", "overview"],
                    "preferred": ["home", "overview"],
                    "missing_preferred": [],
                },
                "render_target": render_target,
                "source": {"kind": "builtin"},
            }]
        },
        "experience.gate1.offscreen_accepted": offscreen,
        "presentation.executor_enabled": executor,
        "presentation.active_owner": "native",
        "pwnagotchi.service.state": "active",
        "platform.services": [
            {"unit": "pwnagotchi.service", "active": "active"},
            {"unit": "beast-ui.service", "active": "inactive"},
        ],
        "plugins.catalog": [],
        "display.handoff.backup_exists": False,
    })


def test_try_on_tft_plan_is_bounded_ephemeral_and_locked_by_gate():
    row = ExperienceTryOnPlanner(_state()).plan(
        "monolith", page_id="home", duration_sec=999
    )

    assert row["operation"] == "experience.try_on_tft"
    assert row["duration_sec"] == 300
    assert row["renderer_experience_id"] == "monolith"
    assert row["auto_rollback_required"] is True
    assert row["writes_preferences"] is False
    assert row["persists_experience_selection"] is False
    assert row["executor_enabled"] is False
    assert row["execution_allowed"] is False
    assert row["plan_ready"] is False
    assert "Gate 1 off-screen Experience acceptance is not recorded" in row["blockers"]
    assert "physical Presentation Broker executor remains disabled" in row["blockers"]
    ids = [step["id"] for step in row["steps"]]
    assert ids[0] == "snapshot.current_presentation"
    assert "experience.preview.ephemeral" in ids
    assert ids[-1] == "rollback.required"
    assert row["steps"][-1]["mutates"] is True


def test_try_on_tft_plan_rejects_non_native_target_even_when_page_exists():
    row = ExperienceTryOnPlanner(
        _state(native=False, offscreen=True, executor=True)
    ).plan("monolith", page_id="home", duration_sec=90)

    assert "current display target requires an explicit native Scene variant" in row["blockers"]
    assert row["render_target"]["requested_size"] == [800, 480]
    assert row["execution_allowed"] is False


def test_try_on_tft_planning_can_be_precondition_clean_but_still_has_no_executor():
    row = ExperienceTryOnPlanner(
        _state(native=True, offscreen=True, executor=True)
    ).plan("monolith", page_id="home", duration_sec=90)

    assert row["blockers"] == []
    assert row["plan_ready"] is True
    # This class only plans. A separate physically validated executor must be added later.
    assert row["executor_enabled"] is False
    assert row["execution_allowed"] is False
    assert row["auto_rollback_required"] is True


def test_try_on_tft_plan_rejects_unknown_or_unimplemented_experience_page():
    planner = ExperienceTryOnPlanner(_state())
    unknown = planner.plan("does-not-exist")
    assert "compiled Experience plan not found" in unknown["blockers"]

    missing = planner.plan("monolith", page_id="map")
    assert "page renderer unavailable: map" in missing["blockers"]
