from pathlib import Path
from PIL import Image

from beastui.backgrounds import matrix_column_state
from beastui.engine import BeastUI

ROOT = Path(__file__).resolve().parents[1] / 'beastui'


def test_matrix_streams_never_move_horizontally_and_speeds_vary():
    opts={'column_spacing':10,'speed':84,'glyph_step':10,'x_offset':4,'min_trail':6,'max_trail':16}
    a=[matrix_column_state(i,100.0,opts) for i in range(30)]
    b=[matrix_column_state(i,100.25,opts) for i in range(30)]
    assert [r['x'] for r in a] == [r['x'] for r in b]
    assert any(abs(a[i]['head']-b[i]['head']) > 1 for i in range(30))
    assert len({round(r['speed'],2) for r in a}) > 20


def test_beast_page_uses_readable_body_font_and_no_text_inside_xp_bar():
    ui=BeastUI(root=ROOT,output='/tmp/beast-v082-test.png',theme_id='classic')
    assert ui.fonts['body'].size >= 11
    src=(ROOT/'pages.py').read_text()
    assert "font=f['body']" in src
    # XP label is drawn before bar; old unreadable micro text inside the bar is gone.
    assert "NEXT {next_xp}" not in src


def test_matrix_reaction_has_no_horizontal_fragment_rectangles():
    src=(ROOT/'engine.py').read_text()
    block=src.split("elif style=='glitch':",1)[1].split("elif style=='sweep':",1)[0]
    assert 'localized VERTICAL' in block
    assert 'span=' not in block


def test_scanline_is_one_full_width_line():
    src=(ROOT/'engine.py').read_text()
    assert "d.rectangle((0,y,479,y+width-1)" in src
    ui=BeastUI(root=ROOT,output='/tmp/beast-v082-test.png',theme_id='matrix')
    assert ui.theme.scanline_width == 1
