#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
from beastui.engine import BeastUI


def render(root,out,theme,state,page='home',setup=None):
    ui=BeastUI(root=root,output=str(out),theme_id=theme);ui.state=dict(state)
    ui.histories={
        'wifi.ap_count':[2,4,3,6,8,5,7,9],
        'system.cpu.total':[12,18,25,17,32,47,68,27,21],
        'system.temp.cpu_c':[56,58,61,63,65,70,76,79,72],
        'expedition.distance_m':[0,120,430,900,1500,2100,2700,3218],
    }
    ui.events=[{'type':'governor.mode_changed','severity':'warning'},{'type':'wifi.ap_discovered','severity':'info'}]
    if page in ui.pages.IDS: ui.page=ui.pages.IDS.index(page)
    if setup: setup(ui)
    ui.render()


def setopts(tid,opts):
    return lambda u:u.theme_options.__setitem__(tid,opts)


def gov(mode,budget,fps):
    def f(u):
        u.state.update({'governor.mode':mode,'governor.budget_pct':budget,'governor.ui.fps_cap':fps})
    return f


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='/opt/beast-ui');ap.add_argument('--state',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);state=json.loads(Path(a.state).read_text())
    state.update({
        'expedition.active':True,'expedition.id':'validation-expedition','expedition.duration_sec':3720,
        'expedition.distance_m':3218.688,'expedition.route_points':88,'expedition.ap_unique':42,
        'expedition.captures_delta':3,'expedition.xp_delta':120,'expedition.max_temp_c':77.2,
        'expedition.max_cpu_pct':89.0,'expedition.min_battery_pct':61.0,
    })

    # New theme default/extreme pairs.
    render(root,out/'synthwave-default.png','synthwave',state)
    render(root,out/'synthwave-extreme.png','synthwave',state,setup=setopts('synthwave',{'grid_density':'dense','sun':'full','horizon_glow':'hot','stars':'dense'}))
    render(root,out/'amber-tactical-default.png','amber_tactical',state)
    render(root,out/'amber-tactical-extreme.png','amber_tactical',state,setup=setopts('amber_tactical',{'grid_density':'dense','scope':'on','sweep':'fast','brackets':'on'}))
    render(root,out/'ghost-minimal-default.png','ghost_minimal',state)
    render(root,out/'ghost-minimal-active.png','ghost_minimal',state,setup=setopts('ghost_minimal',{'ambient':'soft','ghosts':'normal','edge_trace':'on'}))

    # New pages/integration.
    render(root,out/'expedition-synthwave.png','synthwave',state,page='expedition')
    render(root,out/'expedition-ghost.png','ghost_minimal',state,page='expedition')
    render(root,out/'map-expedition.png','amber_tactical',state,page='map')

    # Same System page at each budget for direct visual comparison.
    for mode,budget,fps in [('FULL',100,18),('GUARDED',75,10),('REDUCED',45,6),('SURVIVAL',20,3)]:
        render(root,out/f'governor-{mode.lower()}.png','synthwave',state,page='system',setup=gov(mode,budget,fps))

    # Keep representative v0.10 renderer regression in this gate.
    for mode in BeastUI.RENDERER_CHOICES['spectrum']:
        render(root,out/f'spectrum-{mode}.png','blackice',state,page='spectrum',setup=lambda u,m=mode:u.renderers.__setitem__('spectrum',m))

if __name__=='__main__':main()
