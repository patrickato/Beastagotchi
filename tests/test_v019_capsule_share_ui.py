from pathlib import Path

from PIL import Image, ImageDraw

from beastcore.capsules import BeastCapsuleCodec
from beastui.apps import AppRegistry
from beastui.design import TOKENS
from beastui.engine import BeastUI
from beastui.qr_render import draw_qr, qr_backend_status, qr_matrix


def _representative_capsule():
    envelope = BeastCapsuleCodec.build(
        "lineage",
        {
            "format": "lineage_v1",
            "preview": True,
            "creature_id": "creature-gallery-1234567890abcdef1234",
            "name": "SANITIZED BEAST",
            "kind": "beast",
            "lineage": "standard",
            "generation": 1,
            "level": 43,
            "stage": "Hunter",
            "legend": False,
            "parents": ["creature-parent-1234567890abcdef"],
            "achievement_count": 28,
            "appearance": {
                "traits": {"eyes": "amber", "profile": "classic", "temperament": "curious"},
                "mutation": "spark",
            },
        },
        created_at=0.0,
        capsule_id="capsule-gallery-preview-test",
        producer={"name": "Beastagotchi", "format": "gallery_preview"},
        privacy={
            "local_ids_included": False,
            "credentials_included": False,
            "captures_included": False,
            "network_history_included": False,
            "exact_location_included": False,
            "logs_included": False,
            "gallery_preview": True,
        },
    )
    encoded = BeastCapsuleCodec.encode(envelope)
    frames = BeastCapsuleCodec.qr_frames(encoded, max_frame_chars=220)
    return envelope, encoded, frames


def test_capsule_qr_backend_renders_real_matrix_at_usable_reference_scale():
    status = qr_backend_status()
    assert status["available"] is True
    _, _, frames = _representative_capsule()
    assert frames

    matrix = qr_matrix(frames[0], error_correction="M")
    assert len(matrix) == len(matrix[0])
    assert len(matrix) >= 21
    assert any(any(row) for row in matrix)

    im = Image.new("RGB", (480, 320), "white")
    meta = draw_qr(ImageDraw.Draw(im), BeastUI.CAPSULE_QR_BOX, frames[0], error_correction="M")
    assert meta["modules"] == len(matrix)
    # 3 px/module is our off-screen acceptance target for this 206px-class
    # reference box. Physical camera/TFT scan reliability is still a separate gate.
    assert meta["scale_px"] >= 3
    assert meta["rendered_px"][0] <= (BeastUI.CAPSULE_QR_BOX[2] - BeastUI.CAPSULE_QR_BOX[0] + 1)


def test_capsule_share_controls_meet_reference_resistive_touch_minimum():
    for box in (BeastUI.CAPSULE_PREV, BeastUI.CAPSULE_CLOSE, BeastUI.CAPSULE_NEXT):
        x1, y1, x2, y2 = box
        assert (x2 - x1) >= TOKENS.touch_min
        assert (y2 - y1) >= TOKENS.touch_min
        assert y2 <= TOKENS.footer_y


def test_capsule_app_is_real_launcher_destination():
    app = AppRegistry().get("capsules")
    assert app is not None
    assert app.kind == "overlay"
    assert app.target == "capsule_share"
    assert app.category == "Identity"


def test_capsule_share_surface_renders_real_qr_and_navigates_frames(tmp_path):
    root = Path(__file__).resolve().parents[1] / "beastui"
    out = tmp_path / "capsule-share.png"
    envelope, encoded, frames = _representative_capsule()
    assert len(frames) > 1

    ui = BeastUI(root=root, output=str(out), theme_id="classic")
    ui.state = {
        "progression.beast.name": "SANITIZED BEAST",
        "progression.level": 43,
        "progression.stage": "Hunter",
        "health.core.state": "healthy",
    }
    ui.page = ui.pages.IDS.index("home")
    ui.capsule_share_overlay = True
    ui.capsule_share = {
        "ok": True,
        "capsule_type": "lineage",
        "envelope": envelope,
        "encoded": encoded,
        "qr": {
            "transport": "animated_qr_text_frames",
            "frame_count": len(frames),
            "max_frame_chars": 220,
            "frames": frames,
            "renderer_required": True,
            "renderer_bundled": False,
        },
        "import_performed": False,
    }
    ui.capsule_frame_idx = 0
    ui.render()

    assert out.is_file()
    with Image.open(out) as im:
        assert im.size == (480, 320)
        # QR quiet zone is white in the real transport region.
        assert im.getpixel((20, 60)) == (255, 255, 255)
        # Real QR contains black modules too.
        crop = im.crop(BeastUI.CAPSULE_QR_BOX)
        colors = crop.getcolors(maxcolors=1_000_000)
        assert colors is not None
        assert any(rgb == (0, 0, 0) for _count, rgb in colors)
        assert any(rgb == (255, 255, 255) for _count, rgb in colors)

    # Frame controls operate without re-fetching/importing anything.
    ui.on_input("tap", {"x": 425, "y": 248})
    assert ui.capsule_frame_idx == 1
    ui.on_input("tap", {"x": 266, "y": 248})
    assert ui.capsule_frame_idx == 0
    ui.on_input("tap", {"x": 345, "y": 248})
    assert ui.capsule_share_overlay is False
    assert ui.app_launcher is True


def test_capsule_share_unavailable_state_never_draws_fake_qr(tmp_path):
    root = Path(__file__).resolve().parents[1] / "beastui"
    out = tmp_path / "capsule-unavailable.png"
    ui = BeastUI(root=root, output=str(out), theme_id="classic")
    ui.state = {"health.core.state": "healthy"}
    ui.page = ui.pages.IDS.index("home")
    ui.capsule_share_overlay = True
    ui.capsule_share = {"ok": False, "error": "Capsule API unavailable"}
    ui.render()

    with Image.open(out) as im:
        crop = im.crop(BeastUI.CAPSULE_QR_BOX)
        # Failure state remains themed UI; it must not accidentally look like a
        # black/white machine-readable QR transport.
        colors = crop.getcolors(maxcolors=1_000_000)
        assert colors is not None
        pure_bw = sum(count for count, rgb in colors if rgb in {(0, 0, 0), (255, 255, 255)})
        assert pure_bw < crop.width * crop.height * 0.90
