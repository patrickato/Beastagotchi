import json
from pathlib import Path
from beastui.engine import BeastUI

PKG=Path(__file__).resolve().parents[1]
ROOT=PKG/'beastui'


def test_touchlab_recommended_calibration_is_affine_and_precise():
    d=json.loads((PKG/'config'/'touch_recommended_v092.json').read_text())
    assert len(d['transform']['x'])==3
    assert len(d['transform']['y'])==3
    assert d['validation']['stylus_targets']==75
    assert d['validation']['median_residual_px'] < 3
    assert d['validation']['p95_residual_px'] < 6


def test_matrix_theme_detail_uses_two_large_rows_per_page(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'detail.png'),theme_id='matrix')
    ui._open_theme_detail('matrix')
    before=ui.options_for_theme('matrix')['density']
    # Density is the second 52px row on page one.
    ui.on_input('tap',{'x':420,'y':180})
    assert ui.options_for_theme('matrix')['density'] != before
    # NEXT is a 54px-high primary target.
    ui.on_input('tap',{'x':350,'y':240})
    assert ui.theme_detail_page==1
    speed=ui.options_for_theme('matrix')['speed_mode']
    ui.on_input('tap',{'x':420,'y':130})
    assert ui.options_for_theme('matrix')['speed_mode'] != speed


def test_theme_library_bottom_controls_have_large_vertical_hit_area(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'library.png'),theme_id='classic')
    ui.theme_library=True
    ui.theme_library_offset=0
    ui.on_input('tap',{'x':410,'y':220})
    assert ui.theme_library_offset==2
