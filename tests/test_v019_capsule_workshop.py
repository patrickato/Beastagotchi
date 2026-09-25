import io

from PIL import Image
import pytest

from beastcore.capsules import BeastCapsuleCodec
from beaststudio.server import HTML, StudioState


class _FakeAPI:
    def __init__(self):
        self.kwargs = None

    def capsule_export(self, **kwargs):
        self.kwargs = dict(kwargs)
        env = BeastCapsuleCodec.build(
            "lineage",
            {
                "format": "lineage_v1",
                "creature_id": "creature-workshop-test",
                "name": "Hex" if kwargs.get("include_name") else None,
                "kind": "beast",
                "lineage": "black_ice",
                "generation": 0,
                "level": 43,
                "stage": "Hunter",
                "parents": [],
                "achievement_count": 7,
            },
            created_at=1.0,
            capsule_id="capsule-workshop-test",
            producer={"name": "Beastagotchi", "version": "test"},
            privacy={
                "local_ids_included": False,
                "credentials_included": False,
                "captures_included": False,
                "network_history_included": False,
                "exact_location_included": False,
                "logs_included": False,
                "name_included": bool(kwargs.get("include_name")),
            },
        )
        encoded = BeastCapsuleCodec.encode(env)
        frames = BeastCapsuleCodec.qr_frames(encoded, max_frame_chars=kwargs.get("qr_chars", 220))
        return {
            "ok": True,
            "capsule_type": "lineage",
            "envelope": env,
            "encoded": encoded,
            "encoded_chars": len(encoded),
            "qr": {"frames": frames, "frame_count": len(frames)},
            "import_performed": False,
        }


def _studio_with_fake_api():
    st = object.__new__(StudioState)
    st.api = _FakeAPI()
    return st


def test_capsule_workshop_is_first_class_studio_surface():
    assert 'data-tab="capsules"' in HTML
    assert 'id="capsules"' in HTML
    assert "CAPSULE WORKSHOP" in HTML
    assert "EXACT SHARE SNAPSHOT" in HTML
    assert "BUILD EXACT SHARE PREVIEW" in HTML
    assert "/api/capsule-preview" in HTML
    assert "/api/capsule-qr" in HTML
    assert "No import or publication was performed." in HTML


def test_capsule_workshop_preview_forwards_explicit_privacy_choices(monkeypatch):
    st = _studio_with_fake_api()
    monkeypatch.setattr(
        "beaststudio.server.qr_backend_status",
        lambda: {"available": True, "backend": "test"},
    )
    row = st.capsule_preview({
        "beast_id": "local-beast-id",
        "include_name": False,
        "include_appearance": True,
        "include_achievements": True,
        "qr_chars": 240,
    })

    assert row["ok"] is True
    assert row["import_performed"] is False
    assert row["publish_performed"] is False
    assert row["studio_qr"]["available"] is True
    assert st.api.kwargs == {
        "capsule_type": "lineage",
        "beast_id": "local-beast-id",
        "include_name": False,
        "include_achievements": True,
        "include_appearance": True,
        "qr_chars": 240,
    }
    assert row["envelope"]["privacy"]["credentials_included"] is False
    assert row["envelope"]["privacy"]["captures_included"] is False
    assert row["envelope"]["privacy"]["exact_location_included"] is False


def test_capsule_workshop_qr_endpoint_renders_exact_bcq1_frame():
    env = BeastCapsuleCodec.build(
        "lineage",
        {"format": "lineage_v1", "creature_id": "creature-qr-test", "name": "Hex"},
        created_at=1.0,
        capsule_id="capsule-qr-test",
    )
    frame = BeastCapsuleCodec.qr_frames(BeastCapsuleCodec.encode(env), max_frame_chars=220)[0]
    st = _studio_with_fake_api()

    png = st.capsule_qr_png({"frame": frame})
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    with Image.open(io.BytesIO(png)) as im:
        assert im.size == (512, 512)
        colors = im.convert("RGB").getcolors(maxcolors=1_000_000)
        assert colors is not None
        assert any(rgb == (0, 0, 0) for _count, rgb in colors)
        assert any(rgb == (255, 255, 255) for _count, rgb in colors)


@pytest.mark.parametrize("frame", ["", "not-a-capsule", "BC1.fake"])
def test_capsule_workshop_qr_endpoint_rejects_non_bcq1_text(frame):
    st = _studio_with_fake_api()
    with pytest.raises(ValueError, match="BCQ1"):
        st.capsule_qr_png({"frame": frame})
