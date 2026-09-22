from __future__ import annotations

import json
from pathlib import Path

from beaststudio.server import StudioState, HTML
from beastui.apps import AppRegistry
from beastui.customization import validate_dashboard_widgets, validate_custom_boards
from beastui.engine import BeastUI

ROOT=Path(__file__).resolve().parents[1]
UIROOT=ROOT/'beastui'


def test_dashboard_is_spatial_not_six_slot_limited():
    raw=[]
    for i in range(11):
        raw.append({'id':f'w{i}','key':'system.cpu.total','label':f'CPU {i}','style':'metric','x':i%10,'y':(i//5)*2,'w':2,'h':2,'z':i,'visible':i!=7})
    clean=validate_dashboard_widgets(raw)
    assert len(clean)==11
    assert clean[7]['visible'] is False
    assert clean[10]['z']==10


def test_custom_boards_validate_as_expandable_compositions():
    boards=validate_custom_boards([
        {'id':'field_ops','label':'Field Ops','widgets':[{'key':'gps.satellites_used','label':'GPS','style':'bar','x':0,'y':0,'w':4,'h':3}]},
        {'id':'bad id!','label':'skip','widgets':[{'key':'system.cpu.total'}]},
    ])
    assert len(boards)==1
    assert boards[0]['id']=='field_ops'
    assert boards[0]['widgets'][0]['key']=='gps.satellites_used'


def test_engine_registers_custom_boards_as_apps_and_opens_them(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.custom_boards=validate_custom_boards([{'id':'field_ops','label':'Field Ops','widgets':[{'key':'system.cpu.total','label':'CPU','style':'metric'}]}])
    ui.apps=ui._build_app_registry()
    app=ui.apps.get('board:field_ops')
    assert app is not None and app.kind=='board'
    ui._open_app('board:field_ops')
    assert ui.pages.IDS[ui.page]=='dashboard'
    assert ui.active_board_id=='field_ops'
    assert ui._active_dashboard_widgets()[0]['label']=='CPU'
    im=ui._compose(ui.page)
    assert im.size==(480,320)


def test_board_is_cleared_when_navigating_to_other_main_page(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.custom_boards=validate_custom_boards([{'id':'x','label':'X','widgets':[{'key':'system.cpu.total'}]}])
    ui.apps=ui._build_app_registry();ui._open_app('board:x')
    assert ui.active_board_id=='x'
    ui._change_page(1,wrap=False)
    assert ui.active_board_id==''


def test_studio_persists_custom_boards_and_preview_selection(tmp_path):
    prefs=tmp_path/'preferences.json';token=tmp_path/'studio.token'
    st=StudioState(str(UIROOT),str(prefs),str(token))
    draft=st.preferences()
    draft['custom_boards']=[{'id':'radio_lab','label':'Radio Lab','widgets':[{'key':'wifi.ap_count','label':'APS','style':'microtrend','x':0,'y':0,'w':6,'h':4}]}]
    draft['preview_board_id']='radio_lab';draft['page']='dashboard'
    cfg=st.validate(draft)
    assert cfg['preview_board_id']=='radio_lab'
    assert cfg['custom_boards'][0]['widgets'][0]['style']=='microtrend'
    result=st.apply(draft);assert result['ok']
    saved=json.loads(prefs.read_text())
    assert saved['custom_boards'][0]['id']=='radio_lab'
    assert 'preview_board_id' not in saved


def test_studio_v015_has_direct_spatial_composer_controls():
    for text in ('LIVE DASHBOARD COMPOSER','+ ADD INSTRUMENT','+ NEW BOARD','layoutOverlay','startLayoutDrag','BRING FRONT'):
        assert text in HTML
