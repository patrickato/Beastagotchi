from beastui.beast_shell import (
    SHELL_TYPE,
    QUALITY_STALE,
    QUALITY_UNKNOWN,
    attention_state,
    build_shell_model,
    format_reading,
    navigation_model,
    reading,
)


def test_shell_type_ramp_does_not_put_primary_meaning_in_microtext():
    assert SHELL_TYPE.caption >= 11
    assert SHELL_TYPE.body >= SHELL_TYPE.caption
    assert SHELL_TYPE.label >= SHELL_TYPE.body
    assert SHELL_TYPE.title >= SHELL_TYPE.label
    assert SHELL_TYPE.hero >= SHELL_TYPE.title


def test_missing_numeric_reading_stays_unknown_instead_of_zero():
    row = reading({}, "system.temp.cpu_c", unit=" C")
    assert row.quality == QUALITY_UNKNOWN
    assert row.value is None
    assert row.known is False
    assert format_reading(row) == "—"
    assert "0" not in format_reading(row)


def test_zero_is_preserved_when_zero_is_an_actual_observation():
    row = reading({"wifi.ap_count": 0}, "wifi.ap_count")
    assert row.known is True
    assert row.value == 0
    assert format_reading(row) == "0"


def test_stale_reading_keeps_value_and_quality_truth():
    state = {
        "radio.primary.channel": 44,
        "radio.primary.channel.quality": "stale",
        "radio.primary.channel.source": "bettercap",
        "radio.primary.channel.age_s": 12.5,
    }
    row = reading(state, "radio.primary.channel")
    assert row.quality == QUALITY_STALE
    assert row.known is True
    assert row.source == "bettercap"
    assert row.age_s == 12.5
    assert format_reading(row) == "44"


def test_shared_attention_detects_radio_stack_failure_even_if_health_is_stale_healthy():
    attn = attention_state({
        "health.core.state": "healthy",
        "pwnagotchi.service.state": "failed",
        "bettercap.service.state": "active",
    })
    assert attn.level == "warning"
    assert attn.summary == "RADIO STACK OFFLINE"


def test_shared_attention_promotes_critical_temperature():
    attn = attention_state({
        "health.core.state": "healthy",
        "system.temp.cpu_c": 81.0,
    })
    assert attn.level == "critical"
    assert attn.summary == "THERMAL CRITICAL"


def test_specific_critical_cause_beats_generic_aggregate_health_wording():
    attn = attention_state({
        "health.core.state": "critical",
        "system.temp.cpu_c": 81.0,
    })
    assert attn.level == "critical"
    assert attn.summary == "THERMAL CRITICAL"
    assert attn.source == "system.temp.cpu_c"


def test_navigation_model_is_wraparound_and_touch_sized_for_three_plus_pages():
    nav = navigation_model("atlas", "recon", ("home", "recon", "map"))
    assert nav.previous_page == "home"
    assert nav.next_page == "map"
    assert nav.previous_enabled is True
    assert nav.next_enabled is True
    assert nav.footer_h >= 48
    for box in (nav.previous_box, nav.home_box, nav.next_box):
        x1, y1, x2, y2 = box
        assert x2 - x1 >= 48
        assert y2 - y1 >= 48

    wrapped = navigation_model("atlas", "home", ("home", "recon", "map"))
    assert wrapped.previous_page == "map"


def test_two_page_navigation_does_not_repeat_same_destination_on_both_sides():
    home = navigation_model("monolith", "home", ("home", "overview"))
    assert home.previous_enabled is False
    assert home.next_enabled is True
    assert home.next_page == "overview"

    overview = navigation_model("monolith", "overview", ("home", "overview"))
    assert overview.previous_enabled is True
    assert overview.previous_page == "home"
    assert overview.next_enabled is False


def test_shell_status_sentence_is_attention_language_not_duplicate_body_metrics():
    shell = build_shell_model("monolith", "home", {
        "health.core.state": "healthy",
        "radio.primary.channel": 11,
        "wifi.ap_count": 18,
    }, ("home", "overview"))
    assert shell.status_sentence == "SYSTEM READY"
    assert "CH 11" not in shell.status_sentence
    assert "18 NEARBY" not in shell.status_sentence


def test_shell_unknown_state_is_explicit_not_nominal():
    shell = build_shell_model("monolith", "home", {}, ("home", "overview"))
    assert shell.attention.level == "notice"
    assert shell.status_sentence == "STATUS UNKNOWN"
