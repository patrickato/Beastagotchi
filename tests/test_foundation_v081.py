import time
from pathlib import Path
from PIL import Image, ImageDraw

from beastui.engine import BeastUI

ROOT = Path(__file__).resolve().parents[1] / 'beastui'


def _reaction_image(theme_id):
    ui = BeastUI(root=ROOT, output='/tmp/beast-v081-test.png', theme_id=theme_id)
    ui.phase = 123.456
    ui.events = [{'type':'pwnagotchi.handshake','ts':time.time(),'data':{}}]
    im = Image.new('RGB',(480,320),ui.theme.c('bg'))
    d = ImageDraw.Draw(im)
    ui._event_reaction(d)
    return ui, im


def test_matrix_reaction_never_draws_another_full_width_scanline():
    ui, im = _reaction_image('matrix')
    col = ui.theme.c('accent')
    # Event reaction may create short fragments, but never a near-full-width row.
    longest = 0
    for y in range(34,278):
        count = sum(1 for x in range(480) if im.getpixel((x,y)) == col)
        longest = max(longest, count)
    assert longest < 180


def test_starcore_reaction_never_draws_a_full_height_vertical_scanbar():
    ui, im = _reaction_image('starcore')
    col = ui.theme.c('accent')
    longest = 0
    for x in range(480):
        count = sum(1 for y in range(34,278) if im.getpixel((x,y)) == col)
        longest = max(longest, count)
    assert longest < 80


def test_matrix_rain_hotfix_is_denser_and_fast_but_scanline_stays_single_pixel_width():
    ui = BeastUI(root=ROOT, output='/tmp/beast-v081-test.png', theme_id='matrix')
    opts = ui.theme.background_options
    assert opts['column_spacing'] <= 10
    assert opts['trail'] == 8
    assert opts['speed'] >= 84
    assert ui.theme.scanline_width == 1
