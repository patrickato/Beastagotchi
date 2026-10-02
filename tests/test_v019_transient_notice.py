import threading
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from beastui.components import transient_notice
from beastui.design import TOKENS
from beastui.engine import BeastUI


class _Theme:
    COLORS = {
        "panel2": (25, 25, 25),
        "text": (235, 235, 235),
        "dim": (140, 140, 140),
        "info": (90, 150, 220),
        "primary": (100, 180, 220),
        "accent": (120, 200, 130),
        "warn": (220, 170, 70),
        "danger": (220, 80, 70),
    }

    def c(self, key, default=None):
        return self.COLORS.get(key, default if default is not None else (255, 255, 255))


def _fonts():
    font = ImageFont.load_default()
    return {key: font for key in ("micro", "tiny", "small", "body", "medium", "large", "title")}


def test_shared_transient_notice_renders_all_semantic_kinds():
    for kind in ("info", "success", "warn", "error", "loading"):
        im = Image.new("RGB", (480, 320), (0, 0, 0))
        d = ImageDraw.Draw(im)
        box = transient_notice(
            d,
            {"title": "TEST NOTICE", "detail": "Shared transient feedback", "kind": kind},
            _fonts(),
            _Theme(),
            phase=1.25,
        )
        assert box == (54, 42, 426, 100)
        # At least some pixels inside the notice differ from the untouched background.
        assert im.getpixel((72, 52)) != (0, 0, 0)


def test_notice_lifecycle_is_bounded_and_cleanup_safe():
    ui = BeastUI.__new__(BeastUI)
    ui.dirty = threading.Event()
    ui.notice = None
    ui.notice_started = 0.0
    ui.notice_duration = TOKENS.notice_default_s

    row = BeastUI.show_notice(ui, "Saved", kind="success", detail="Known-good baseline")
    assert row["kind"] == "success"
    assert ui.dirty.is_set()

    ui.notice_started = 10.0
    ui.notice_duration = 2.0
    assert BeastUI._notice_active(ui, now=11.99) is True
    assert BeastUI._notice_active(ui, now=12.0) is False
    assert ui.notice is None


class _Feed:
    def __init__(self, error):
        self.error = error

    def snapshot(self):
        return {}, [], {}, {}, self.error


def _minimal_ui_for_feed(tmp_path):
    ui = BeastUI.__new__(BeastUI)
    ui.feed = _Feed(None)
    ui.state = {}
    ui.events = []
    ui.histories = {}
    ui.aux = {}
    ui.data_error = None
    ui._last_data_error = None
    ui.notice = None
    ui.notice_started = 0.0
    ui.notice_duration = TOKENS.notice_default_s
    ui.dirty = threading.Event()
    ui.rare_preview_path = Path(tmp_path) / "missing-rare-preview.json"
    return ui


def test_data_feed_error_notice_does_not_repeat_until_state_changes(tmp_path):
    ui = _minimal_ui_for_feed(tmp_path)
    ui.feed.error = "core unavailable"

    BeastUI._sync_feed(ui)
    assert ui.notice["kind"] == "error"
    assert ui.notice["title"] == "DATA FEED ERROR"
    first_started = ui.notice_started

    # Same error on the next poll must not reset the notice timer.
    BeastUI._sync_feed(ui)
    assert ui.notice_started == first_started

    ui.feed.error = None
    BeastUI._sync_feed(ui)
    assert ui.notice["kind"] == "success"
    assert ui.notice["title"] == "DATA FEED RESTORED"
