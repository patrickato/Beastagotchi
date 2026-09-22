from pathlib import Path
from beastui.engine import BeastUI
from beastui.backgrounds import _runtime_matrix_options, matrix_column_state

ROOT=Path(__file__).resolve().parents[1]/'beastui'


def test_matrix_presets_have_more_real_separation(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='matrix')
    sparse=_runtime_matrix_options(ui.theme,{'density':'sparse','speed_mode':'drift'})
    deluge=_runtime_matrix_options(ui.theme,{'density':'deluge','speed_mode':'torrent'})
    assert sparse['column_spacing'] >= 14
    assert deluge['column_spacing'] == 5
    assert deluge['speed'] > sparse['speed'] * 2


def test_matrix_columns_remain_vertical_but_spacing_is_not_rigid(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='matrix')
    o=_runtime_matrix_options(ui.theme,{'density':'dense','speed_mode':'fast'})
    xs=[matrix_column_state(i,1.0,o)['x'] for i in range(12)]
    xs2=[matrix_column_state(i,2.0,o)['x'] for i in range(12)]
    assert xs==xs2
    diffs=[b-a for a,b in zip(xs,xs[1:])]
    assert len(set(diffs)) > 1


def test_theme_library_is_two_card_pager(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'lib.png'),theme_id='classic')
    ui.theme_library=True
    ui.render()
    assert (tmp_path/'lib.png').exists()
    # page-forward hit zone should advance two themes
    ui.on_input('tap',{'x':420,'y':252})
    assert ui.theme_library_offset==2


def test_matrix_theme_detail_stepper_works_both_directions(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'detail.png'),theme_id='matrix')
    ui._open_theme_detail('matrix')
    before=ui.options_for_theme('matrix')['density']
    ui.on_input('tap',{'x':420,'y':180})  # + density (v0.9.2 large-row layout)
    after=ui.options_for_theme('matrix')['density']
    assert after != before
    ui.on_input('tap',{'x':60,'y':180})   # - density
    assert ui.options_for_theme('matrix')['density']==before
