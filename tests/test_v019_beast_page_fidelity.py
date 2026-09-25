from PIL import Image, ImageDraw, ImageFont

from beastui.pages import Pages


class _Theme:
    COLORS = {
        "bg": (0, 0, 0),
        "panel": (8, 15, 17),
        "panel2": (10, 18, 20),
        "edge": (30, 70, 75),
        "primary": (0, 220, 230),
        "secondary": (80, 220, 120),
        "accent": (130, 255, 60),
        "info": (70, 190, 255),
        "text": (230, 235, 230),
        "dim": (115, 135, 135),
        "warn": (240, 180, 60),
    }

    def c(self, key, default=None):
        return self.COLORS.get(key, default if default is not None else (255, 255, 255))


class _Face:
    def __init__(self):
        self.box = None

    def draw(self, d, box, theme, state, phase):
        self.box = tuple(box)
        d.rectangle(box, outline=theme.c("primary"))


class _UI:
    def __init__(self):
        self.theme = _Theme()
        font = ImageFont.load_default()
        self.fonts = {key: font for key in ("micro", "tiny", "small", "body", "medium", "large", "title")}
        self.phase = 1.0


def _state():
    return {
        "progression.beast.name": "BEAST",
        "progression.beast.kind": "beast",
        "progression.beast.lineage": "standard",
        "progression.beast.generation": 0,
        "progression.roster.summary": {"total": 1, "monsters": 0},
        "progression.level": 7,
        "progression.max_level": 100,
        "progression.stage": "cub",
        "progression.xp": 0,
        "progression.xp_next_level": 10,
        "progression.level_progress_pct": 73.5,
        "progression.aura": "none",
        "pwnagotchi.mood": "awake",
        "context.mode.effective": "pwn",
        "progression.discovery.beast_unique_aps": 4,
        "progression.discovery.device_first_witnessed": 2,
        "progression.achievements.count": 3,
    }


def test_beast_page_gives_creature_majority_and_uses_open_profile_rail():
    face = _Face()
    pages = Pages(face)
    ui = _UI()
    im = Image.new("RGB", (480, 320), ui.theme.c("bg"))
    d = ImageDraw.Draw(im)

    pages.beast(d, _state(), ui)

    # Creature region is materially larger than the old 202x163 face box.
    assert face.box == (37, 61, 282, 210)
    assert (face.box[2] - face.box[0]) > 220

    # Open right-side profile rail exists without requiring a full enclosing card.
    assert im.getpixel((311, 50)) == ui.theme.c("edge")
    assert im.getpixel((311, 260)) == ui.theme.c("edge")

    # Canonical progress drives visible accent geometry.
    assert any(
        im.getpixel((x, y)) == ui.theme.c("accent")
        for x in range(18, 301, 8)
        for y in range(47, 248, 8)
    )
