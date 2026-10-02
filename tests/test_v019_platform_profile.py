from beastcore.platform_profile import PlatformProfile
from beastcore.state import StateRegistry


def _state(ram_mb, model, width=480, height=320):
    s = StateRegistry()
    s.update_many("test", {
        "system.ram_mb": ram_mb,
        "system.model": model,
        "system.architecture": "aarch64",
        "display.framebuffers": [{"id":"fb1","device":"/dev/fb1","width":width,"height":height,"bpp":16}],
        "display.connected_outputs": 0,
    })
    return s


def test_zero2w_style_profile_is_constrained_without_hard_feature_denials():
    row = PlatformProfile(_state(512, "Raspberry Pi Zero 2 W Rev 1.0"), cpu_count_fn=lambda: 4).snapshot()
    assert row["compute_tier"] == "constrained"
    assert row["display_class"] == "reference"
    assert row["budget_hints"]["scene_complexity"] == "light"
    assert row["policy"]["unsupported_feature_hard_blocks"] == "technical_requirements_only"
    assert row["policy"]["owner_can_choose_lighter_or_richer_experience"] is True


def test_pi5_or_large_memory_profile_can_expand():
    row = PlatformProfile(_state(8192, "Raspberry Pi 5 Model B Rev 1.0", 1280, 800), cpu_count_fn=lambda: 4).snapshot()
    assert row["compute_tier"] == "enhanced"
    assert row["display_class"] == "large"
    assert row["budget_hints"]["scene_complexity"] == "expanded"


def test_generic_sbc_uses_resources_not_brand_name():
    row = PlatformProfile(_state(4096, "Generic ARM64 SBC", 800, 480), cpu_count_fn=lambda: 8).snapshot()
    assert row["compute_tier"] == "full"
    assert row["display_class"] == "medium"
    assert row["architecture"] == "aarch64"
