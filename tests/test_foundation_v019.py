from pathlib import Path

from beastcore.presentation import PresentationBroker, normalize_owner
from beastui.design import TOKENS, PRIMARY_PAGES, PAGE_GROUPS


class _S:
    def __init__(self, d=None):
        self.d = dict(d or {})

    def get(self, key, default=None):
        return self.d.get(key, default)


def test_v019_design_tokens_preserve_validated_reference_geometry():
    assert (TOKENS.canvas_w, TOKENS.canvas_h) == (480, 320)
    assert TOKENS.header_h == 34 and TOKENS.footer_y == 278
    assert TOKENS.touch_min >= 48 and TOKENS.touch_primary >= TOKENS.touch_normal
    assert TOKENS.motion_page_s > TOKENS.motion_fast_s > 0


def test_v019_page_model_preserves_beast_and_operational_pages():
    assert PRIMARY_PAGES[0] == "home"
    assert "beast" in PRIMARY_PAGES
    assert "captures" in PRIMARY_PAGES
    assert "map" in PRIMARY_PAGES
    assert "system" in PRIMARY_PAGES
    assert PAGE_GROUPS["identity"] == ("home", "beast")


def test_presentation_owner_aliases_are_explicit():
    assert normalize_owner("pwn-native") == "native"
    assert normalize_owner("theme-manager") == "theme_manager"
    assert normalize_owner("beast-ui") == "beast"


def test_presentation_broker_persists_requested_owner_without_executing_handoff(tmp_path):
    p = tmp_path / "presentation.json"
    s = _S({"pwnagotchi.service.state": "active", "platform.services": [], "plugins.catalog": []})
    b = PresentationBroker(s, path=str(p), clock=lambda: 100.0)
    first = b.tick()
    assert first["presentation.desired_owner"] == "native"
    assert first["presentation.executor_enabled"] is False

    row = b.request("beast-ui", requested_by="test")
    assert row["desired_owner"] == "beast"
    assert row["status"] == "requested"

    reloaded = PresentationBroker(s, path=str(p), clock=lambda: 101.0).tick()
    assert reloaded["presentation.desired_owner"] == "beast"
    assert reloaded["presentation.executor_enabled"] is False


def test_presentation_broker_surfaces_legacy_theme_manager_conflict(tmp_path):
    s = _S({
        "pwnagotchi.service.state": "active",
        "platform.services": [{"unit": "beast-ui.service", "active": "active"}],
        "plugins.catalog": [{"name": "theme_manager", "enabled": True}],
    })
    b = PresentationBroker(s, path=str(tmp_path / "p.json"), clock=lambda: 1.0)
    b.mark_active("beast")
    row = b.tick()
    assert row["presentation.theme_manager.installed"] is True
    assert row["presentation.theme_manager.enabled"] is True
    assert row["presentation.conflict_count"] == 1
    assert row["presentation.executor_enabled"] is False


def test_presentation_state_file_is_private(tmp_path):
    p = tmp_path / "p.json"
    b = PresentationBroker(_S(), path=str(p), clock=lambda: 1.0)
    b.request("native")
    assert p.exists()
    assert (p.stat().st_mode & 0o777) == 0o600


def test_v019_home_visual_smoke_across_theme_families(tmp_path):
    from PIL import Image
    from beastui.engine import BeastUI

    root = Path(__file__).resolve().parents[1] / "beastui"
    state = {
        "progression.level": 27,
        "progression.max_level": 100,
        "progression.stage": "Stalker",
        "progression.aura": "spark",
        "progression.level_progress_pct": 63.0,
        "progression.xp_current_level": 420,
        "progression.xp_next_level": 245,
        "beast.expression": "curious",
        "pwnagotchi.mood": "awake",
        "context.mode.effective": "pwn",
        "wifi.ap_count": 18,
        "wifi.client_count": 4,
        "wifi.encounters.session_unique": 42,
        "wifi.encounters.lifetime_unique": 1337,
        "radio.primary.channel": 11,
        "system.cpu.total": 21.0,
        "system.temp.cpu_c": 58.0,
        "pwnagotchi.handshakes": 3,
        "gps.fix": True,
        "health.core.state": "healthy",
        "dock.state": "field",
        "governor.mode": "FULL",
    }

    for theme in ("classic", "blackice", "hunter", "synthwave", "lcars"):
        out = tmp_path / f"home-{theme}.png"
        ui = BeastUI(root=root, output=str(out), theme_id=theme)
        ui.state = dict(state)
        ui.page = ui.pages.IDS.index("home")
        ui.render()
        assert out.is_file(), theme
        with Image.open(out) as im:
            assert im.size == (480, 320)
            assert im.getbbox() == (0, 0, 480, 320)


def test_platform_bundle_exposes_resource_and_presentation_truth():
    from beastcore.api import LocalAPI

    class Store:
        def library_summary(self, limit): return {"total": 2, "items": []}
        def recent_jobs(self, limit): return []
        def recent_incidents(self, limit): return [{"title": "Recovered restart", "status": "resolved"}]

    state = _S({
        "overview.state": "healthy",
        "platform.services": [{"unit": "beast-ui.service", "active": "active"}],
        "performance.processes": [{"id": "beast_ui", "label": "Beast UI", "cpu_pct": 4.5, "rss_mb": 72.0, "pids": [101]}],
        "performance.beast.cpu_pct": 7.0,
        "performance.platform_services.cpu_pct": 11.0,
        "performance.tracked.rss_mb": 155.0,
        "performance.process_count": 3,
        "performance.ui.avg_render_ms": 12.5,
        "performance.fb.write_ratio_pct": 21.0,
        "system.temp.cpu_c": 58.5,
        "system.cpu.total": 23.0,
        "system.memory.used_pct": 31.0,
        "system.throttle.flags": "0x0",
        "system.clock.arm_mhz": 1800.0,
        "governor.mode": "FULL",
        "governor.budget_pct": 100,
        "governor.throttle_current": False,
        "presentation.desired_owner": "beast",
        "presentation.active_owner": "beast",
        "presentation.status": "stable",
        "presentation.available_owners": ["native", "theme_manager", "beast"],
        "presentation.theme_manager.installed": True,
        "presentation.theme_manager.enabled": False,
        "presentation.conflict_count": 0,
        "presentation.executor_enabled": False,
    })
    api = LocalAPI(state, object(), Store())
    bundle = api.platform_bundle()

    assert bundle["thermal"]["cpu_temp_c"] == 58.5
    assert bundle["performance"]["beast_cpu_pct"] == 7.0
    assert bundle["performance"]["processes"][0]["id"] == "beast_ui"
    assert bundle["governor"]["mode"] == "FULL"
    assert bundle["presentation"]["active_owner"] == "beast"
    assert bundle["presentation"]["theme_manager_installed"] is True
    assert bundle["presentation"]["executor_enabled"] is False
    assert bundle["incidents"]["items"][0]["status"] == "resolved"


def test_pack_registry_validates_and_reports_capability_blockers(tmp_path):
    import json
    from beastcore.packs import PackRegistryEngine

    root = tmp_path / "installed"
    pack = root / "maps-plus"
    pack.mkdir(parents=True)
    (pack / "manifest.json").write_text(json.dumps({
        "id": "maps-plus",
        "label": "Maps Plus",
        "version": "1.2.3",
        "pack_type": "map",
        "capabilities": ["gps", "rtl_sdr"],
        "resource_class": "medium",
        "thermal_class": "compute",
        "source": {"type": "github_release", "url": "https://user:secret@example.com/project/releases"},
    }))
    state = _S({"capabilities.present": ["gps"]})
    engine = PackRegistryEngine(state, roots={"installed": root})
    patch = engine.tick()

    assert patch["packs.count"] == 1
    row = patch["packs.items"][0]
    assert row["id"] == "maps-plus"
    assert row["requirements_met"] is False
    assert row["missing_capabilities"] == ["rtl_sdr"]
    assert "secret@" not in row["source"]["url"]
    assert patch["packs.executor_enabled"] is True
    assert patch["packs.executor_scope"] == "verified_registry_install_only"
    assert patch["packs.activation_enabled"] is False


def test_update_policy_engine_records_intent_without_enabling_executor(tmp_path):
    import json
    from beastcore.updates import UpdatePolicyEngine

    policy = tmp_path / "update_policies.json"
    policy.write_text(json.dumps({"schema": 1, "policies": {
        "beastagotchi": "notify",
        "theme_manager": "auto_stage",
        "pack:maps-plus": "auto_install",
    }}))
    state = _S({
        "system.beast_version": "0.19.0-dev.2",
        "plugins.catalog": [{"name": "theme_manager", "enabled": False}],
        "packs.items": [{
            "id": "maps-plus", "label": "Maps Plus", "version": "1.2.3",
            "origin": "installed", "requirements_met": True, "blockers": [],
            "source": {"type": "github_release", "url": "https://example.com/maps"},
        }],
        "dock.docked": True,
        "network.internet.state": "unknown",
    })
    patch = UpdatePolicyEngine(state, path=str(policy)).tick()
    by_id = {r["id"]: r for r in patch["updates.components"]}

    assert by_id["beastagotchi"]["policy"] == "notify"
    assert by_id["theme_manager"]["policy"] == "auto_stage"
    assert by_id["pack:maps-plus"]["policy"] == "auto_install"
    assert by_id["pack:maps-plus"]["auto_install_eligible"] is False
    assert patch["updates.auto_trigger_ready"] is False
    assert patch["updates.executor_enabled"] is False


def test_studio_update_policy_store_is_private_and_validated(tmp_path):
    from beaststudio.update_policies import UpdatePolicyStore, UpdatePolicyError

    path = tmp_path / "update_policies.json"
    store = UpdatePolicyStore(path)
    row = store.set_policy("pack:maps-plus", "auto_stage")
    assert row["policies"]["pack:maps-plus"] == "auto_stage"
    assert (path.stat().st_mode & 0o777) == 0o600
    try:
        store.set_policy("../../bad", "auto_install")
    except UpdatePolicyError:
        pass
    else:
        raise AssertionError("unsafe component id must be rejected")



def test_v019_field_cockpit_pages_render_empty_and_live_states(tmp_path):
    from PIL import Image
    from beastui.engine import BeastUI

    root = Path(__file__).resolve().parents[1] / "beastui"
    empty_state = {
        "health.core.state": "healthy",
        "context.mode.effective": "pwn",
        "wifi.aps": [],
        "wifi.ap_count": 0,
        "radio.primary.channel": 1,
        "radio.primary.band": "2.4GHz",
        "gps.fix": False,
        "gps.satellites_used": 0,
        "gps.satellites_visible": 0,
        "captures.total": 0,
        "pwnagotchi.handshakes": 0,
        "wifi.handshake_ap_count": 0,
        "expedition.active": False,
        "expedition.route_points": 0,
        "expedition.ap_unique": 0,
        "expedition.captures_delta": 0,
    }
    live_state = dict(empty_state)
    live_state.update({
        "wifi.aps": [
            {"ssid": "field-one", "hostname": "field-one", "channel": 1, "rssi": -42, "encryption": "WPA2"},
            {"ssid": "field-two", "hostname": "field-two", "channel": 6, "rssi": -58, "encryption": "WPA2"},
            {"ssid": "field-three", "hostname": "field-three", "channel": 149, "rssi": -67, "encryption": "WPA3"},
        ],
        "wifi.ap_count": 3,
        "radio.primary.channel": 6,
        "gps.fix": True,
        "gps.satellites_used": 7,
        "gps.satellites_visible": 11,
        "context.motion.speed_mph": 2.4,
        "captures.total": 8,
        "pwnagotchi.handshakes": 2,
        "wifi.handshake_ap_count": 3,
        "expedition.active": True,
        "expedition.id": "field-test",
        "expedition.duration_sec": 754,
        "expedition.distance_m": 1420.0,
        "expedition.route_points": 3,
        "expedition.ap_unique": 17,
        "expedition.captures_delta": 2,
        "expedition.xp_delta": 51,
        "expedition.max_temp_c": 57.4,
        "expedition.max_cpu_pct": 44.0,
        "expedition.min_battery_pct": 73.0,
    })

    for label, state in (("empty", empty_state), ("live", live_state)):
        for page in ("recon", "spectrum", "captures", "map", "expedition"):
            out = tmp_path / f"{label}-{page}.png"
            ui = BeastUI(root=root, output=str(out), theme_id="classic")
            ui.state = dict(state)
            ui.histories = {"wifi.ap_count": [1, 2, 3], "system.cpu.total": [10, 20], "system.temp.cpu_c": [50, 52]}
            ui.aux = {}
            if label == "live":
                ui.aux = {
                    "channel_history": [
                        {"channels": [{"channel": 1, "ap_count": 1}, {"channel": 6, "ap_count": 2}]},
                        {"channels": [{"channel": 1, "ap_count": 2}, {"channel": 6, "ap_count": 1}]},
                    ],
                    "expedition": {
                        "points": [
                            {"latitude": 42.0, "longitude": -83.0},
                            {"latitude": 42.001, "longitude": -83.002},
                            {"latitude": 42.003, "longitude": -83.001},
                        ]
                    },
                }
            ui.page = ui.pages.IDS.index(page)
            ui.render()
            assert out.is_file(), (label, page)
            with Image.open(out) as im:
                assert im.size == (480, 320)
                assert im.getbbox() == (0, 0, 480, 320)



def test_v019_app_launcher_geometry_respects_touch_minimum():
    from beastui.engine import BeastUI
    from beastui.design import TOKENS

    boxes = list(BeastUI.APP_CARD_BOXES) + list(BeastUI.CONTROL_QUICK_BOXES) + [
        BeastUI.APP_CAT_PREV,
        BeastUI.APP_CAT_NEXT,
        BeastUI.APP_NAV_PREV,
        BeastUI.APP_NAV_CLOSE,
        BeastUI.APP_NAV_NEXT,
        BeastUI.CONTROL_APP_BOX,
    ]
    assert BeastUI.APP_PAGE_SIZE == 4
    for x1, y1, x2, y2 in boxes:
        assert (x2 - x1) >= TOKENS.touch_min
        assert (y2 - y1) >= TOKENS.touch_min

    # The 2x2 card grid must not overlap the category or bottom navigation
    # controls on the 480x320 logical canvas.
    assert max(box[3] for box in BeastUI.APP_CARD_BOXES) < BeastUI.APP_NAV_PREV[1]
    assert min(box[1] for box in BeastUI.APP_CARD_BOXES) > BeastUI.APP_CAT_PREV[3]
    assert len(BeastUI.CONTROL_QUICK_BOXES) == 4
    assert max(box[3] for box in BeastUI.CONTROL_QUICK_BOXES) < TOKENS.footer_y


def test_v019_beast_identity_changes_home_and_beast_render(tmp_path):
    from PIL import Image
    from beastui.engine import BeastUI

    root = Path(__file__).resolve().parents[1] / "beastui"
    base = {
        "progression.level": 43,
        "progression.max_level": 100,
        "progression.stage": "Hunter",
        "progression.aura": "glow",
        "progression.level_progress_pct": 71.0,
        "progression.xp": 12345,
        "progression.xp_next_level": 777,
        "progression.discovery.beast_unique_aps": 212,
        "progression.discovery.device_first_witnessed": 19,
        "progression.achievements.count": 28,
        "progression.roster.summary": {"total": 3, "beasts": 2, "monsters": 1, "legends": 0},
        "pwnagotchi.mood": "awake",
        "context.mode.effective": "pwn",
        "beast.expression": "curious",
        "wifi.ap_count": 5,
        "wifi.encounters.session_unique": 8,
        "wifi.encounters.lifetime_unique": 500,
        "radio.primary.channel": 6,
        "system.cpu.total": 20.0,
        "system.temp.cpu_c": 55.0,
        "pwnagotchi.handshakes": 1,
        "health.core.state": "healthy",
        "dock.state": "field",
    }
    identities = [
        ("hex", {"progression.beast.name": "Hex", "progression.beast.kind": "beast", "progression.beast.lineage": "black_ice", "progression.beast.generation": 0}),
        ("orbit", {"progression.beast.name": "Orbit", "progression.beast.kind": "monster", "progression.beast.lineage": "starcore", "progression.beast.generation": 1}),
    ]
    rendered = {}
    for ident, patch in identities:
        state = dict(base)
        state.update(patch)
        for page in ("home", "beast"):
            out = tmp_path / f"{ident}-{page}.png"
            ui = BeastUI(root=root, output=str(out), theme_id="classic")
            ui.state = state
            ui.page = ui.pages.IDS.index(page)
            ui.render()
            with Image.open(out) as im:
                assert im.size == (480, 320)
                rendered[(ident, page)] = im.tobytes()

    assert rendered[("hex", "home")] != rendered[("orbit", "home")]
    assert rendered[("hex", "beast")] != rendered[("orbit", "beast")]


def test_v019_widget_inspector_regions_follow_current_page_geometry(tmp_path):
    from beastui.engine import BeastUI

    root = Path(__file__).resolve().parents[1] / "beastui"
    ui = BeastUI(root=root, output=str(tmp_path / "zones.png"), theme_id="classic")

    assert ui._widget_key_at("system", 40, 75) == "health.core.state"
    assert ui._widget_key_at("system", 145, 75) == "system.temp.cpu_c"
    assert ui._widget_key_at("system", 205, 75) == "system.cpu.total"
    assert ui._widget_key_at("system", 260, 75) == "system.memory.used_pct"
    assert ui._widget_key_at("system", 380, 75) == "governor.mode"

    assert ui._widget_key_at("captures", 100, 75) == "captures.total"
    assert ui._widget_key_at("captures", 280, 75) == "pwnagotchi.handshakes"
    assert ui._widget_key_at("captures", 410, 75) == "wifi.handshake_ap_count"

    assert ui._widget_key_at("spectrum", 60, 65) == "radio.primary.channel"
    assert ui._widget_key_at("spectrum", 180, 65) == "radio.primary.band"
    assert ui._widget_key_at("spectrum", 410, 65) == "wifi.ap_count"

    assert ui._widget_key_at("expedition", 60, 135) == "expedition.distance_m"
    assert ui._widget_key_at("expedition", 180, 135) == "expedition.route_points"
    assert ui._widget_key_at("expedition", 300, 135) == "expedition.ap_unique"
    assert ui._widget_key_at("expedition", 410, 135) == "expedition.captures_delta"

    assert ui._widget_key_at("beast", 300, 80) == "progression.level"
    assert ui._widget_key_at("beast", 270, 170) == "pwnagotchi.mood"
    assert ui._widget_key_at("beast", 345, 170) == "progression.aura"
    assert ui._widget_key_at("beast", 430, 170) == "context.mode.effective"
    assert ui._widget_key_at("beast", 270, 225) == "progression.discovery.beast_unique_aps"
    assert ui._widget_key_at("beast", 350, 225) == "progression.discovery.device_first_witnessed"
    assert ui._widget_key_at("beast", 430, 225) == "progression.achievements.count"
