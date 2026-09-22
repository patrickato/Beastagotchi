#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
from beastui.engine import BeastUI
from beastui.customization import validate_dashboard_widgets


def render(root,out,theme,state,page='home',setup=None,aux=None,events=None):
    ui=BeastUI(root=root,output=str(out),theme_id=theme);ui.state=dict(state)
    ui.histories={
        'wifi.ap_count':[state.get('wifi.ap_count')] if isinstance(state.get('wifi.ap_count'),(int,float)) else [],
        'system.cpu.total':[state.get('system.cpu.total')] if isinstance(state.get('system.cpu.total'),(int,float)) else [],
        'system.temp.cpu_c':[state.get('system.temp.cpu_c')] if isinstance(state.get('system.temp.cpu_c'),(int,float)) else [],
    }
    ui.aux=dict(aux or {});ui.events=list(events or [])
    if page in ui.pages.IDS:ui.page=ui.pages.IDS.index(page)
    if setup:setup(ui)
    ui.render()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='/opt/beast-ui');ap.add_argument('--state',required=True);ap.add_argument('--events');ap.add_argument('--out',required=True);a=ap.parse_args()
    root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);state=json.loads(Path(a.state).read_text());events=[]
    if a.events:
        try:events=json.loads(Path(a.events).read_text())
        except Exception:events=[]

    # No synthetic measurements are introduced here. Missing target values stay
    # missing so the validation gallery also checks honest unavailable states.
    for theme in ('classic','synthwave','amber_tactical','ghost_minimal','cyberpunk','wopr_norad','lcars','retro_crt'):
        render(root,out/f'dashboard-{theme}.png',theme,state,page='dashboard')

    render(root,out/'apps-all.png','classic',state,setup=lambda u:setattr(u,'app_launcher',True))
    def system_apps(u):
        u.app_launcher=True;u.app_category_idx=u._app_categories().index('System')
    render(root,out/'apps-system.png','ghost_minimal',state,setup=system_apps)

    for mode in ('timeline','notifications','diagnostics','services','hardware','connectivity','storage','backups','field_library','tasks','incidents','operations','topology'):
        render(root,out/f'app-{mode}.png','classic',state,setup=lambda u,m=mode:setattr(u,'platform_overlay',m),events=events)


    if state.get('display.external_connected'):
        render(root,out/'app-command-center.png','classic',state,setup=lambda u:setattr(u,'platform_overlay','command_center'))
    if state.get('ai.local.available'):
        render(root,out/'app-beast-operator.png','classic',state,setup=lambda u:setattr(u,'platform_overlay','ai_operator'))

    render(root,out/'plugins.png','amber_tactical',state,setup=lambda u:setattr(u,'plugins_overlay',True))
    render(root,out/'telemetry.png','synthwave',state,setup=lambda u:setattr(u,'telemetry_overlay',True),aux={'telemetry':[]})
    render(root,out/'performance.png','ghost_minimal',state,setup=lambda u:setattr(u,'performance_overlay',True))
    render(root,out/'beast-studio-status.png','classic',state,setup=lambda u:setattr(u,'studio_overlay',True))

    # Explicit Dashboard customization smoke scene: bindings point at real
    # canonical state keys; target state determines whether values are present.
    def custom(u):
        u.dashboard_widgets=validate_dashboard_widgets([
            {'key':'system.temp.cpu_c','label':'TEMP','style':'bar','min':25,'max':85},
            {'key':'system.cpu.total','label':'CPU','style':'radial','min':0,'max':100},
            {'key':'wifi.ap_count','label':'APS','style':'microtrend'},
            {'key':'radio.primary.channel','label':'CHANNEL','style':'metric'},
            {'key':'gps.satellites_used','label':'GPS SAT','style':'bar','min':0,'max':16},
            {'key':'performance.fb.write_ratio_pct','label':'FB WRITE','style':'bar','min':0,'max':100},
        ])
    render(root,out/'dashboard-custom-bindings.png','synthwave',state,page='dashboard',setup=custom)

    def spatial(u):
        u.dashboard_widgets=validate_dashboard_widgets([
            {'id':'cpu','key':'system.cpu.total','label':'CPU','style':'radial','x':0,'y':0,'w':4,'h':4,'z':0},
            {'id':'temp','key':'system.temp.cpu_c','label':'TEMP','style':'bar','x':4,'y':0,'w':5,'h':3,'z':1},
            {'id':'aps','key':'wifi.ap_count','label':'APS','style':'microtrend','x':9,'y':0,'w':3,'h':5,'z':2},
            {'id':'gps','key':'gps.satellites_used','label':'GPS','style':'metric','x':4,'y':3,'w':5,'h':2,'z':3},
            {'id':'trip','key':'expedition.distance_m','label':'TRIP','style':'metric','x':0,'y':4,'w':6,'h':4,'z':4},
            {'id':'hidden','key':'system.memory.used_pct','label':'HIDDEN','style':'metric','x':6,'y':5,'w':3,'h':3,'z':5,'visible':False},
            {'id':'channel','key':'radio.primary.channel','label':'CHANNEL','style':'metric','x':9,'y':5,'w':3,'h':3,'z':6},
        ])
    render(root,out/'dashboard-spatial.png','cyberpunk',state,page='dashboard',setup=spatial)

    def board(u):
        from beastui.customization import validate_custom_boards
        u.custom_boards=validate_custom_boards([{'id':'field_ops','label':'Field Ops','widgets':[
            {'key':'gps.satellites_used','label':'GPS SAT','style':'bar','x':0,'y':0,'w':4,'h':3},
            {'key':'expedition.distance_m','label':'DISTANCE','style':'metric','x':4,'y':0,'w':4,'h':3},
            {'key':'wifi.ap_count','label':'APS','style':'microtrend','x':8,'y':0,'w':4,'h':3},
            {'key':'system.temp.cpu_c','label':'TEMP','style':'bar','x':0,'y':4,'w':6,'h':3},
            {'key':'system.cpu.total','label':'CPU','style':'radial','x':6,'y':4,'w':6,'h':3},
        ]}]);u.apps=u._build_app_registry();u.active_board_id='field_ops'
    render(root,out/'board-field-ops.png','ghost_minimal',state,page='dashboard',setup=board)

if __name__=='__main__':main()
