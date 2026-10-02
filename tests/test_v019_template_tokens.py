from beastcore.api import LocalAPI
from beastcore.state import StateRegistry
from beastcore.template_tokens import TemplateTokenRegistry


class _Events:
    pass


class _Store:
    pass


def test_template_tokens_use_only_canonical_state_and_preserve_meta():
    state = StateRegistry()
    state.update_many(
        "system",
        {
            "system.temp.cpu_c": 48.24,
            "system.cpu.total": 60.2,
            "gps.fix": False,
            "progression.level": 7,
            "expedition.distance_m": 1420.0,
        },
        priority=50,
    )
    tokens = TemplateTokenRegistry(state, clock=lambda: 123.0)

    temp = tokens.resolve("system.temp")
    assert temp["known"] is True
    assert temp["value"] == 48.24
    assert temp["text"] == "48.2C"
    assert temp["source"] == "system"
    assert temp["status"] == "live"

    assert tokens.resolve("cpu")["token"] == "system.cpu"
    assert tokens.resolve("{gps}")["text"] == "NO FIX"
    assert tokens.resolve("beast.level")["text"] == "7"
    assert tokens.resolve("expedition.distance")["text"] == "1.42 km"


def test_template_tokens_never_invent_missing_values():
    state = StateRegistry()
    tokens = TemplateTokenRegistry(state)

    row = tokens.resolve("power.battery")
    assert row["known"] is True
    assert row["status"] == "unavailable"
    assert row["value"] is None
    assert row["text"] == "--"

    unknown = tokens.resolve("wifi.secret")
    assert unknown["known"] is False
    assert unknown["status"] == "unknown"
    assert unknown["text"] == "--"


def test_template_token_catalog_carries_privacy_publication_and_alias_metadata():
    state = StateRegistry()
    tokens = TemplateTokenRegistry(state)
    catalog = {row["token"]: row for row in tokens.catalog()}

    assert catalog["beast.name"]["privacy"] == "profile"
    assert catalog["beast.name"]["publication"] == "policy"
    assert catalog["system.temp"]["publication"] == "never"
    assert "temp" in catalog["system.temp"]["aliases"]
    assert catalog["gps.fix"]["state_key"] == "gps.fix"


def test_template_renderer_is_bounded_and_reports_unavailable_tokens():
    state = StateRegistry()
    state.update_many(
        "test",
        {
            "progression.beast.name": "Hex",
            "progression.level": 27,
            "system.temp.cpu_c": 51.25,
        },
    )
    tokens = TemplateTokenRegistry(state)

    rendered = tokens.render("{beast.name} LV {beast.level} // {system.temp} // {battery}")
    assert rendered["text"] == "Hex LV 27 // 51.2C // --"
    assert rendered["token_count"] == 4
    assert rendered["unresolved"] == ["battery"]

    try:
        tokens.render("x" * 1025)
    except ValueError:
        pass
    else:
        raise AssertionError("oversized templates must be rejected")


def test_local_api_exposes_bounded_template_token_bundle_without_new_pollers():
    state = StateRegistry()
    state.update_many("system", {"system.temp.cpu_c": 49.0, "system.cpu.total": 21.0})
    api = LocalAPI(state, _Events(), _Store())
    api.template_tokens = TemplateTokenRegistry(state)

    bundle = api.template_token_bundle(["system.temp", "cpu", "not.allowed"])
    assert bundle["count"] == 3
    assert bundle["known_count"] == 2
    by_requested = {row["requested"]: row for row in bundle["items"]}
    assert by_requested["system.temp"]["text"] == "49.0C"
    assert by_requested["cpu"]["text"] == "21%"
    assert by_requested["not.allowed"]["status"] == "unknown"
