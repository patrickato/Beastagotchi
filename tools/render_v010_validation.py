#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
from beastui.engine import BeastUI


def render(root,out,theme,state,page='home',setup=None):
    ui=BeastUI(root=root,output=str(out),theme_id=theme);ui.state=dict(state)
    ui.histories={'wifi.ap_count':[2,4,3,6,8,5,7,9],'system.cpu.total':[12,18,25,17,32,27,21], 'system.temp.cpu_c':[56,58,61,63,65,67,66]}
    ui.events=[{'type':'system.thermal_band','severity':'warning'},{'type':'wifi.ap_discovered','severity':'info'}]
    ui.page=ui.pages.IDS.index(page)
    if setup:setup(ui)
    ui.render()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='/opt/beast-ui');ap.add_argument('--state',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);state=json.loads(Path(a.state).read_text())
    # Non-Matrix theme personalities.
    render(root,out/'classic-dense.png','classic',state,setup=lambda u:u.theme_options.__setitem__('classic',{'grid_density':'dense','scanline':'on','pulse_level':'active'}))
    render(root,out/'starcore-nebula.png','starcore',state,setup=lambda u:u.theme_options.__setitem__('starcore',{'star_density':'nebula','twinkle':'high','orbit':'on'}))
    render(root,out/'blackice-whiteout.png','blackice',state,setup=lambda u:u.theme_options.__setitem__('blackice',{'frost_density':'whiteout','drift':'fast','crystal_overlay':'active'}))
    render(root,out/'hunter-heavy.png','hunter',state,setup=lambda u:u.theme_options.__setitem__('hunter',{'grid_density':'dense','reticle':'on','embers':'heavy'}))
    # Visualizer Studio.
    render(root,out/'visualizer-studio.png','classic',state,setup=lambda u:setattr(u,'visualizer_overlay',True))
    # Spectrum renderer gallery.
    for mode in BeastUI.RENDERER_CHOICES['spectrum']:
        render(root,out/f'spectrum-{mode}.png','blackice',state,page='spectrum',setup=lambda u,m=mode:u.renderers.__setitem__('spectrum',m))
    for mode in BeastUI.RENDERER_CHOICES['system']:
        render(root,out/f'system-{mode}.png','starcore',state,page='system',setup=lambda u,m=mode:u.renderers.__setitem__('system',m))

if __name__=='__main__':main()
