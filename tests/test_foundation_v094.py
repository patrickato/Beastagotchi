from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from beastcore.progression import ProgressionEngine
from beastcore.state import StateRegistry
from beastcore.rare import RareMomentEngine
from beastui.backgrounds import _runtime_matrix_options, _matrix_stream_color
from beastui.engine import BeastUI
from beastui.hitbox import expanded_hitbox
from beastui.native_effects import apply_native_effects
from beastui.rare_overlay import render_rare_overlay
from beastui.theme import load_theme

PKG=Path(__file__).resolve().parents[1]
ROOT=PKG/'beastui'


def _checkpoint_profile():
    return {
        'schema':1,'xp':405,'max_level':100,'lifetime_runtime_sec':36861.15,
        'runtime_award_remainder_sec':261.15,
        'seen_vendors':['ARRIS','AirTies','Arcadyan','Continental','Jabil','MITSUMI','Motorola','NETGEAR','TP-Link'],
        'achievements':['first_signal','first_vendor','signal_scout','first_gps_lock','runtime_hour','first_capture','signals_10','gps_10','runtime_10h'],
        'last_achievement':'Long Day',
        'counters':{'gps_locks':15,'handshakes':1,'lifetime_new_aps':47,'runtime_awards':61,'vendors':9},
    }


def test_touch_hitbox_expands_small_visuals_and_clamps_edges():
    b=expanded_hitbox('x',(0,0,20,20),minimum=56)
    assert b.width >= 56 and b.height >= 56
    assert b.x1 == 0 and b.y1 == 0
    assert b.x2 < 480 and b.y2 < 320


def test_matrix_single_color_green_does_not_invent_red_accents():
    th=load_theme(ROOT/'themes/matrix.json')
    o=_runtime_matrix_options(th,{'palette_mode':'green','accent_mix':'off'})
    colors={_matrix_stream_color(th,o,2,k,14,1.0) for k in range(14)}
    # Green preset may vary brightness but must never introduce a red-dominant hue.
    assert all(c[1] >= c[0] and c[1] >= c[2] for c in colors)


def test_matrix_custom_palette_can_be_exactly_one_color_family():
    th=load_theme(ROOT/'themes/matrix.json')
    o=_runtime_matrix_options(th,{
        'palette_mode':'custom','primary_color':'cyan','secondary_color':'off',
        'tertiary_color':'off','quaternary_color':'off','accent_mix':'off'
    })
    colors=[_matrix_stream_color(th,o,3,k,12,2.0) for k in range(12)]
    # Cyan stays cyan-family; no unrelated red/orange channel may dominate.
    assert all(c[1] >= c[0] and c[2] >= c[0] for c in colors)


def test_matrix_custom_palette_exposes_four_independent_slots(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='matrix')
    ui.theme_options['matrix']={'palette_mode':'custom'}
    keys=[r[0] for r in ui._matrix_option_rows()]
    for key in ('primary_color','secondary_color','tertiary_color','quaternary_color'):
        assert key in keys
    # Returning to a preset collapses the custom color editor without losing the values.
    ui.theme_options['matrix']['palette_mode']='green'
    assert 'secondary_color' not in [r[0] for r in ui._matrix_option_rows()]


def test_matrix_density_speed_and_trail_ranges_are_meaningfully_distinct():
    th=load_theme(ROOT/'themes/matrix.json')
    sparse=_runtime_matrix_options(th,{'density':'sparse','speed_mode':'drift','trail_mode':'short'})
    deluge=_runtime_matrix_options(th,{'density':'deluge','speed_mode':'torrent','trail_mode':'extreme'})
    assert sparse['column_spacing'] >= deluge['column_spacing'] * 3
    assert deluge['speed'] >= sparse['speed'] * 4
    assert deluge['max_trail'] >= sparse['max_trail'] * 3


def test_checkpoint_profile_generates_interactive_progress_catalog(tmp_path):
    path=tmp_path/'profile.json';path.write_text(json.dumps(_checkpoint_profile()))
    state=StateRegistry();state.update_many('test',{'wifi.encounters.session_unique':13},priority=100)
    ProgressionEngine(state,str(path))
    snap=state.snapshot(include_meta=False)
    rows=snap['progression.achievements.catalog']
    assert len(rows) >= 38
    signal50=next(r for r in rows if r['id']=='signals_50')
    assert signal50['current']==47.0 and signal50['target']==50
    assert 93 <= signal50['progress_pct'] <= 95
    assert signal50['unlocked'] is False
    assert snap['progression.awards.count'] >= 2


def test_achievement_explorer_filters_and_opens_detail(tmp_path):
    path=tmp_path/'profile.json';path.write_text(json.dumps(_checkpoint_profile()))
    state=StateRegistry();state.update_many('test',{'wifi.encounters.session_unique':13},priority=100)
    ProgressionEngine(state,str(path));snap=state.snapshot(include_meta=False)
    ui=BeastUI(root=ROOT,output=str(tmp_path/'ach.png'),theme_id='classic')
    ui.state=snap;ui.achievements_overlay=True
    ui.achievement_filter='near'
    rows=ui._achievement_rows()
    assert any(r['id']=='signals_50' for r in rows)
    ui.achievement_filter='all';ui.achievement_sort='rarity'
    rows=ui._achievement_rows();assert rows
    ui.on_input('tap',{'x':200,'y':140})
    assert ui.achievement_detail is not None


def test_rare_schedule_has_presentation_metadata(tmp_path):
    state=StateRegistry()
    eng=RareMomentEngine(state,root=str(tmp_path))
    rows=eng.schedule_for_year(2026)
    assert 1 <= len(rows) <= 4
    allowed={'fade','drift','cross','orbit','ghost','storm','apparition','cinematic'}
    assert all(r.get('presentation') in allowed for r in rows)


def test_rare_overlay_supports_moving_and_cinematic_presentations():
    th=load_theme(ROOT/'themes/classic.json')
    base=Image.new('RGB',(480,320),(0,0,0))
    fonts=BeastUI(root=ROOT,output='/tmp/beast-v095-font-probe.png',theme_id='classic').fonts
    st={'rare.omen.active':True,'rare.moment.active':False,'rare.moment.sigil':'eye','rare.moment.rarity':'epic','rare.moment.presentation':'cross'}
    a=render_rare_overlay(base,st,1.0,th,fonts)
    b=render_rare_overlay(base,st,3.0,th,fonts)
    assert a.tobytes()!=b.tobytes()
    st.update({'rare.omen.active':False,'rare.moment.active':True,'rare.moment.rarity':'mythic','rare.moment.presentation':'cinematic'})
    c=render_rare_overlay(base,st,2.0,th,fonts)
    assert c.getbbox() is not None and c.tobytes()!=base.tobytes()


def test_native_chroma_effects_keep_frame_size_and_add_variation():
    im=Image.new('RGB',(480,320),(0,0,0));d=ImageDraw.Draw(im);d.text((40,80),'(o_o)',fill=(0,255,90))
    clean=apply_native_effects(im,1.0,{'effect':'clean'},ink=(0,255,90))
    fx=apply_native_effects(im,1.0,{'effect':'scanlines'},ink=(0,255,90))
    assert clean.size==fx.size==(480,320)
    assert clean.tobytes()!=fx.tobytes()
