from pathlib import Path

from PIL import Image

from beastui.scene_compositor import alpha_panel, ambient_glow, paste_scene_asset, scene_particles


def test_scene_layers_mutate_canvas_without_resizing(tmp_path: Path):
    base = Image.new("RGB", (480, 320), (4, 5, 6))
    before = base.tobytes()
    ambient_glow(base, (120, 120), 80, (0, 255, 255), strength=0.3)
    alpha_panel(base, (280, 50, 460, 210), fill=(10, 20, 30), outline=(0, 255, 255), alpha=150)
    scene_particles(base, 1.25, (255, 0, 255), count=8)
    assert base.size == (480, 320)
    assert base.tobytes() != before


def test_scene_asset_is_optional_and_supports_full_scene_composition(tmp_path: Path):
    base = Image.new("RGB", (480, 320), (0, 0, 0))
    missing = tmp_path / "missing.png"
    assert paste_scene_asset(base, missing, (0, 0, 240, 240)) is False

    asset = tmp_path / "asset.png"
    Image.new("RGB", (64, 64), (200, 40, 80)).save(asset)
    assert paste_scene_asset(
        base,
        asset,
        (8, 38, 278, 269),
        phase=1.0,
        edge_fade=40,
        tint=(0, 255, 255),
        tint_strength=0.04,
    ) is True
    assert base.getbbox() is not None
