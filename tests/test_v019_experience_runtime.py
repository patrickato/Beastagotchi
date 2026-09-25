from beastcore.api import LocalAPI
from beastcore.experience_runtime import ExperiencePlanPublisher


class _State:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def get(self, key, default=None):
        return self.values.get(key, default)


class _Profile:
    def snapshot(self):
        return {
            "compute_tier": "enhanced",
            "display_class": "reference",
        }


class _Resolver:
    def __init__(self):
        self.calls = []

    def resolve_components(self, components):
        self.calls.append(components)
        comp = components[0]
        optional = [
            {"requirement": req, "satisfied": False}
            for req in comp.get("optional_requirements", [])
        ]
        return {
            "provider_selection_enabled": False,
            "components": {
                comp["id"]: {
                    "requirements_resolution": "read_only",
                    "requirements_ready": True,
                    "requirements_status": "ready",
                    "required_results": [],
                    "optional_results": optional,
                    "technical_blockers": [],
                    "policy_blockers": [],
                }
            },
        }


class _Store:
    def library_summary(self, limit):
        return {"total": 0, "items": []}

    def recent_jobs(self, limit):
        return []

    def recent_incidents(self, limit):
        return []


def test_core_experience_publisher_uses_shared_resolver_and_real_surface_coverage():
    resolver = _Resolver()
    pub = ExperiencePlanPublisher(
        _State({"context.mode.effective": "walk"}),
        resolver=resolver,
        platform_profile=_Profile(),
    )

    row = pub.snapshot()
    by_id = {item["experience_id"]: item for item in row["items"]}

    assert row["mode"] == "read_only"
    assert row["context"] == "walk"
    assert row["count"] == 8
    assert row["preview_ready_count"] == 5
    assert row["production_navigation_ready_count"] == 1
    assert row["renderer_coverage"]["atlas"] == ["home", "recon"]
    assert row["renderer_coverage"]["monolith"] == ["home", "overview"]
    assert by_id["atlas"]["page_coverage"]["implemented"] == ["home", "recon"]
    assert by_id["monolith"]["ready_for_production_navigation"] is True
    assert len(resolver.calls) == row["count"]
    assert row["writes_preferences"] is False
    assert row["installs_dependencies"] is False
    assert row["selects_providers"] is False
    assert row["tft_activation_enabled"] is False


def test_core_experience_state_patch_is_bounded_and_non_mutating():
    pub = ExperiencePlanPublisher(
        _State(),
        resolver=_Resolver(),
        platform_profile=_Profile(),
    )
    patch = pub.state_patch()

    assert patch["experience.compiler.mode"] == "read_only"
    assert patch["experience.compiler.count"] == 8
    assert patch["experience.compiler.preview_ready_count"] == 5
    assert patch["experience.compiler.tft_activation_enabled"] is False
    assert patch["experience.compiler.plan"]["writes_preferences"] is False


def test_local_api_prefers_published_core_experience_plan_and_summarizes_it():
    plan = {
        "schema": 1,
        "mode": "read_only",
        "count": 8,
        "preview_ready_count": 5,
        "production_navigation_ready_count": 1,
        "items": [{"experience_id": "atlas"}],
        "writes_preferences": False,
        "installs_dependencies": False,
        "selects_providers": False,
        "tft_activation_enabled": False,
    }
    api = LocalAPI(
        _State({"experience.compiler.plan": plan}),
        object(),
        _Store(),
    )

    assert api.experience_bundle() == plan
    bundle = api.platform_bundle()
    assert bundle["experiences"] == {
        "schema": 1,
        "mode": "read_only",
        "count": 8,
        "preview_ready_count": 5,
        "production_navigation_ready_count": 1,
        "tft_activation_enabled": False,
    }
