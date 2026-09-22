from pathlib import Path

from beastcore.state import StateRegistry
from beastcore.rare import RareMomentEngine
from beastcore.ambient import AmbientContextEngine
from beastcore.progression import ACHIEVEMENT_DEFS, level_for_xp, xp_threshold
from beastui.backgrounds import matrix_column_state, _runtime_matrix_options
from beastui.engine import BeastUI

ROOT=Path(__file__).resolve().parents[1]/'beastui'


def test_rare_schedule_is_deterministic_and_scarce(tmp_path):
    st=StateRegistry(); eng=RareMomentEngine(st,root=str(tmp_path/'secrets'))
    eng.secret=b'x'*32
    a=eng.schedule_for_year(2027); b=eng.schedule_for_year(2027); c=eng.schedule_for_year(2028)
    assert a==b
    assert 1 <= len(a) <= 4
    assert a != c
    assert all(6 <= x['duration'] <= 60 for x in a)
    assert all(12 <= x['omen_lead'] <= 74 for x in a)


def test_ambient_context_has_season_and_moon():
    st=StateRegistry(); eng=AmbientContextEngine(st)
    row=eng.tick(1789776000.0)
    assert row['ambient.season'] in {'winter','spring','summer','autumn'}
    assert row['celestial.moon.phase']
    assert 0 <= row['celestial.moon.illumination_pct'] <= 100


def test_achievement_catalog_has_long_tail_and_rarity():
    assert len(ACHIEVEMENT_DEFS) >= 35
    assert ACHIEVEMENT_DEFS['signals_10000'][2] == 'mythic'
    assert ACHIEVEMENT_DEFS['rare_witness'][2] == 'legendary'
    assert level_for_xp(xp_threshold(100)) == 100


def test_matrix_runtime_options_support_layer_density_speed_and_palette():
    ui=BeastUI(root=ROOT,output='/tmp/v09-matrix.png',theme_id='matrix')
    o=_runtime_matrix_options(ui.theme,{'layer_mode':'mixed','density':'storm','speed_mode':'fury','palette_mode':'rainbow'})
    assert o['layer_mode']=='mixed'
    assert o['column_spacing']==6
    assert o['speed'] > ui.theme.background_options['speed']
    assert o['palette_mode']=='rainbow'
    a=matrix_column_state(3,1.0,o);b=matrix_column_state(3,2.0,o)
    assert a['x']==b['x']


def test_theme_studio_prefs_roundtrip_offscreen(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'a.png'),theme_id='matrix')
    ui.theme_options['matrix']={'layer_mode':'background','density':'normal','speed_mode':'normal','palette_mode':'cyan'}
    assert ui.options_for_theme('matrix')['palette_mode']=='cyan'
    ui.render()
    assert (tmp_path/'a.png').exists()

def test_theme_library_and_detail_render(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'library.png'),theme_id='classic')
    ui.theme_library=True;ui.render();assert (tmp_path/'library.png').exists()
    ui._open_theme_detail('matrix');ui.output=str(tmp_path/'detail.png');ui.fb.output=str(tmp_path/'detail.png');ui.render();assert (tmp_path/'detail.png').exists()


def test_rare_overlay_render_and_ack_path(tmp_path, monkeypatch):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'rare.png'),theme_id='classic')
    ui.state={'rare.moment.active':True,'rare.moment.id':'x','rare.moment.rarity':'legendary','rare.moment.sigil':'eye'}
    ui.render();assert (tmp_path/'rare.png').exists()
