from pathlib import Path

import pytest
from PIL import Image, ImageChops, ImageDraw, ImageFont

from beastui.home_scenes import render_home_scene, _paste_concept_creature
from beastui.concept_creatures import concept_creature
from beastui.scene_compositor import (
    ambient_glow,
    clear_compositor_caches,
    compositor_cache_telemetry,
    paste_scene_asset,
)
from beastui.scene_runtime import SceneLayerSpec, SceneRuntime


class _Theme:
    id = "classic"
    home_scene = "hero"

    _colors = {
        "bg": (2, 4, 8),
        "ink": (3, 6, 10),
        "panel": (10, 18, 28),
        "panel2": (14, 22, 34),
        "primary": (90, 220, 255),
        "secondary": (170, 110, 255),
        "accent": (255, 190, 70),
        "dim": (105, 125, 145),
        "edge": (36, 68, 88),
        "text": (235, 245, 255),
        "info": (100, 210, 255),
        "warn": (255, 190, 70),
        "danger": (255, 80, 90),
        "grid": (20, 42, 52),
    }

    def c(self, name, fallback=None):
        return self._colors.get(name, fallback or (255, 255, 255))


class _UI:
    def __init__(self, root: Path):
        self.root = root
        self.theme = _Theme()
        self.phase = 1.25
        font = ImageFont.load_default()
        self.fonts = {
            "micro": font, "tiny": font, "small": font, "medium": font,
            "large": font, "body": font, "title": font,
        }
        self.scene_runtime = SceneRuntime()
        self.scene_runtime.begin(page_id="home", scene_id="page:home", theme_id="classic")


def test_scene_runtime_records_semantic_layer_contract():
    rt = SceneRuntime()
    rt.begin(page_id="home", scene_id="home:hero", theme_id="classic")
    with rt.layer(
        "home.hud", "instrument", (280, 40, 470, 216),
        signals=("wifi.ap_count",), update_class="live", resource_class="light",
    ):
        pass
    rt.end()
    snap = rt.snapshot()
    assert snap["scene"] == "home:hero"
    assert snap["layer_count"] == 1
    row = snap["layers"][0]
    assert row["id"] == "home.hud"
    assert row["signals"] == ["wifi.ap_count"]
    assert row["render_ms"] >= 0


def test_scene_runtime_rejects_semantic_id_reuse_with_different_metadata():
    rt = SceneRuntime()
    rt.begin(page_id="home")
    rt.register(SceneLayerSpec("x", "text", (0, 0, 10, 10)))
    with pytest.raises(ValueError):
        rt.register(SceneLayerSpec("x", "graph", (0, 0, 20, 20)))


def test_home_hero_publishes_layer_registry(tmp_path: Path):
    ui = _UI(tmp_path)
    image = Image.new("RGB", (480, 320), ui.theme.c("bg"))
    draw = ImageDraw.Draw(image)
    state = {
        "progression.beast.name": "BEAST",
        "progression.level": 12,
        "progression.stage": "Scout",
        "pwnagotchi.mood": "awake",
        "beast.expression": "focused",
        "context.mode.effective": "pwn",
        "radio.primary.channel": 11,
        "wifi.ap_count": 17,
        "wifi.client_count": 6,
        "pwnagotchi.handshakes": 3,
        "captures.pmkid_count": 1,
        "pwnagotchi.status": "Watching the field",
        "wifi.encounters.session_unique": 22,
        "gps.fix": True,
        "system.cpu.total": 18.0,
        "system.temp.cpu_c": 53.0,
    }
    assert render_home_scene(draw, state, ui) is True
    snap = ui.scene_runtime.snapshot()
    assert snap["scene"] == "home:hero"
    ids = {row["id"] for row in snap["layers"]}
    assert {
        "home.environment",
        "home.creature.art",
        "home.live_field",
        "home.identity_status",
    }.issubset(ids)
    hud = next(row for row in snap["layers"] if row["id"] == "home.live_field")
    assert "wifi.ap_count" in hud["signals"]
    env = next(row for row in snap["layers"] if row["id"] == "home.environment")
    assert env["decorative"] is True


def test_compositor_reuses_glow_and_asset_preprocessing(tmp_path: Path):
    clear_compositor_caches()
    base = Image.new("RGB", (480, 320), (0, 0, 0))
    ambient_glow(base, (120, 100), 70, (0, 255, 255), strength=0.2)
    first = compositor_cache_telemetry()
    assert first["glow_misses"] == 1
    ambient_glow(base, (120, 100), 70, (0, 255, 255), strength=0.2)
    second = compositor_cache_telemetry()
    assert second["glow_hits"] == 1

    asset = tmp_path / "portrait.png"
    Image.new("RGB", (64, 64), (180, 40, 90)).save(asset)
    assert paste_scene_asset(base, asset, (8, 38, 278, 269), phase=0.1, edge_fade=30)
    third = compositor_cache_telemetry()
    assert third["asset_misses"] == 1
    assert paste_scene_asset(base, asset, (8, 38, 278, 269), phase=0.9, edge_fade=30)
    fourth = compositor_cache_telemetry()
    assert fourth["asset_hits"] == 1


def test_flagship_concept_creatures_decode_with_alpha():
    for name in ("classic", "cyberpunk", "blackice"):
        image = concept_creature(name)
        assert image is not None
        assert image.mode == "RGBA"
        assert image.width >= 60 and image.height >= 60
        assert image.width * image.height >= 4500
        assert image.getchannel("A").getbbox() is not None


def test_scene_runtime_signal_dirty_layers_are_semantic_not_global():
    rt = SceneRuntime()
    rt.begin(page_id="home", scene_id="home:hero", theme_id="classic")
    rt.register(SceneLayerSpec(
        "env", "environment", (0, 34, 480, 278),
        update_class="ambient", decorative=True,
    ))
    rt.register(SceneLayerSpec(
        "hud", "instrument", (280, 40, 470, 216),
        signals=("wifi.ap_count", "radio.primary.channel"),
        update_class="live",
    ))
    rt.register(SceneLayerSpec(
        "status", "text", (10, 230, 470, 270),
        signals=("pwnagotchi.status",),
        update_class="live",
    ))
    rt.register(SceneLayerSpec(
        "static", "shape", (0, 0, 20, 20),
        update_class="static",
    ))

    assert rt.update_signals({"wifi.ap_count": 5, "pwnagotchi.status": "ready"}) == {
        "wifi.ap_count", "pwnagotchi.status"
    }
    dirty = rt.dirty_layer_ids(include_ambient=False, include_interaction=False)
    assert dirty == ["hud", "status"]
    assert rt.dirty_bounds(include_ambient=False, include_interaction=False) == [
        (280, 40, 470, 216), (10, 230, 470, 270)
    ]

    assert rt.update_signals({"wifi.ap_count": 5, "pwnagotchi.status": "ready"}) == set()
    assert rt.dirty_layer_ids(include_ambient=False, include_interaction=False) == []
    assert rt.dirty_layer_ids(include_ambient=True, include_interaction=False) == ["env"]


def test_scene_runtime_partial_signal_snapshot_does_not_dirty_missing_keys():
    rt = SceneRuntime()
    rt.begin(page_id="home")
    rt.register(SceneLayerSpec(
        "hud", "instrument", (0, 0, 100, 100),
        signals=("wifi.ap_count", "system.cpu.total"),
        update_class="live",
    ))
    rt.update_signals({"wifi.ap_count": 3, "system.cpu.total": 20})
    rt.update_signals({"wifi.ap_count": 3})
    assert rt.dirty_layer_ids(include_ambient=False, include_interaction=False) == []


def test_scene_runtime_snapshot_exposes_truthful_dirty_metadata():
    rt = SceneRuntime()
    rt.begin(page_id="home")
    rt.register(SceneLayerSpec(
        "hud", "instrument", (5, 5, 100, 80),
        signals=("wifi.ap_count",),
        update_class="live",
    ))
    rt.update_signals({"wifi.ap_count": 9})
    snap = rt.snapshot()
    assert snap["changed_signals"] == ["wifi.ap_count"]
    assert snap["dirty_layers"] == ["hud"]
    assert snap["dirty_bounds"] == [[5, 5, 100, 80]]


def test_concept_creature_is_upscaled_to_scene_scale_not_native_thumbnail():
    base = Image.new("RGB", (480, 320), (0, 0, 0))
    before = base.copy()
    assert _paste_concept_creature(
        base, "classic", (8, 48, 258, 230), phase=0.0,
        opacity=255, edge_feather=0,
    ) is True
    diff = ImageChops.difference(before, base)
    bbox = diff.getbbox()
    assert bbox is not None
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    # The prior thumbnail() bug left the compact source near native size.
    # Flagship concept art must materially own its assigned scene region.
    assert width >= 150
    assert height >= 120
