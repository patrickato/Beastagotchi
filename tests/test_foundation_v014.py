from __future__ import annotations

import json
from pathlib import Path

from beaststudio.server import StudioState, HTML
from beastui.apps import AppRegistry
from beastui.customization import (
    validate_context_decks, validate_palette_overrides, validate_correlation_keys,
)
from beastui.engine import BeastUI

ROOT=Path(__file__).resolve().parents[1]
UIROOT=ROOT/'beastui'


def test_context_decks_are_curated_views_not_app_limits(tmp_path):
    ids=[a.id for a in AppRegistry().all()]
    decks=validate_context_decks([
        {'id':'my_field','label':'My Field','apps':['map','expedition','telemetry','map','does_not_exist']}
    ],app_ids=ids)
    assert decks==[{'id':'my_field','label':'MY FIELD','apps':['map','expedition','telemetry']}]
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.context_decks=decks;ui.active_context_deck='my_field'
    cats=ui._app_categories();assert '★ MY FIELD' in cats and 'ALL' in cats
    ui.app_category_idx=cats.index('★ MY FIELD')
    assert [a.id for a in ui._apps_current()]==['map','expedition','telemetry']
    # Registry remains larger than the deck; the deck never removes capability.
    assert len(ui.apps.all())>len(ui._apps_current())


def test_palette_overrides_are_semantic_and_applied_to_real_theme(tmp_path):
    raw={'classic':{'primary':'#123456','bg':'#010203','not-a-slot':'#ffffff'},'bad':{'primary':'nope'}}
    clean=validate_palette_overrides(raw,theme_ids=['classic'])
    assert clean=={'classic':{'primary':'#123456','bg':'#010203'}}
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.palette_overrides=clean;ui._apply_palette_overrides()
    assert ui.theme.c('primary')==(0x12,0x34,0x56)
    assert ui.theme.c('bg')==(1,2,3)
    im=ui._compose(ui.page);assert im.size==(480,320)


def test_widget_long_press_opens_source_inspector_not_drawer(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.page=ui.pages.IDS.index('dashboard')
    ui.dashboard_widgets[0]={'key':'system.cpu.total','label':'CPU','style':'metric'}
    ui.aux={'telemetry':[{'key':'system.cpu.total','label':'CPU','value':42,'quality':'live','source':'system','age_sec':.2,'unit':'%','kind':'live','category':'System'}]}
    ui.on_input('long_press',{'x':60,'y':70,'duration':1.0})
    assert ui.widget_inspector_overlay and ui.widget_inspector_key=='system.cpu.total'
    assert not ui.drawer
    im=ui._compose(ui.page);assert im.size==(480,320)


def test_correlation_lab_uses_real_histories(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.correlation_keys=['system.cpu.total','system.temp.cpu_c']
    ui.histories={'system.cpu.total':[10,20,30,40,50],'system.temp.cpu_c':[50,55,60,65,70]}
    assert round(ui._pearson(ui.histories['system.cpu.total'],ui.histories['system.temp.cpu_c']),3)==1.0
    ui.correlation_overlay=True
    im=ui._compose(ui.page);assert im.size==(480,320)
    assert validate_correlation_keys(['system.cpu.total','system.temp.cpu_c'])==['system.cpu.total','system.temp.cpu_c']


def test_studio_persists_decks_palette_correlation_and_named_variants(tmp_path):
    prefs=tmp_path/'preferences.json';token=tmp_path/'studio.token'
    st=StudioState(str(UIROOT),str(prefs),str(token))
    draft=st.preferences()
    draft['theme']='classic';draft['palette_overrides']={'classic':{'primary':'#112233'}}
    draft['context_decks']=[{'id':'fieldx','label':'FIELD X','apps':['map','expedition','telemetry']}]
    draft['active_context_deck']='fieldx'
    draft['correlation_keys']=['system.cpu.total','system.temp.cpu_c']
    result=st.apply(draft);assert result['ok']
    saved=json.loads(prefs.read_text())
    assert saved['palette_overrides']['classic']['primary']=='#112233'
    assert saved['active_context_deck']=='fieldx'
    assert saved['context_decks'][0]['apps']==['map','expedition','telemetry']
    sv=st.save_variant('Field Alpha',draft);assert sv['ok']
    rows=st.variants();assert rows and rows[0]['name']=='Field Alpha'
    loaded=st.load_variant(sv['id']);assert loaded['theme']=='classic' and loaded['active_context_deck']=='fieldx'
    assert st.delete_variant(sv['id'])['ok'] and not st.variants()


def test_studio_v014_surface_exposes_new_composer_controls():
    assert 'CONTEXT DECKS' in HTML
    assert 'PALETTE OVERRIDES' in HTML
    assert 'CORRELATION LAB' in HTML
    assert 'NAMED VARIANTS' in HTML
    assert 'variant-save' in HTML
