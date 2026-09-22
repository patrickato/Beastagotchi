#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from beastui.engine import BeastUI


def render_ui(root:Path,out:Path,theme:str,state:dict,configure=None):
    ui=BeastUI(root=root,output=str(out),theme_id=theme)
    ui.state=dict(state)
    if configure: configure(ui)
    ui.render()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='/opt/beast-ui')
    p.add_argument('--state',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    root=Path(a.root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    state=json.loads(Path(a.state).read_text())

    render_ui(root,out/'matrix-sparse-drift.png','matrix',state,lambda ui: ui.theme_options.__setitem__('matrix',{
        'layer_mode':'background','density':'sparse','speed_mode':'drift','trail_mode':'short','glyph_set':'mixed',
        'palette_mode':'green','accent_mix':'off','foreground_fraction':'0.00'
    }))
    render_ui(root,out/'matrix-deluge-torrent.png','matrix',state,lambda ui: ui.theme_options.__setitem__('matrix',{
        'layer_mode':'mixed','density':'deluge','speed_mode':'torrent','trail_mode':'extreme','glyph_set':'hex',
        'palette_mode':'custom','primary_color':'green','secondary_color':'cyan','tertiary_color':'violet','quaternary_color':'amber',
        'accent_mix':'balanced','foreground_fraction':'0.30'
    }))

    def ach(ui):
        ui.achievements_overlay=True
    render_ui(root,out/'achievements.png','classic',state,ach)
    def near(ui):
        ui.achievements_overlay=True;ui.achievement_filter='near'
    render_ui(root,out/'achievements-near.png','classic',state,near)
    def detail(ui):
        ui.achievements_overlay=True
        rows=state.get('progression.achievements.catalog') or []
        candidate=next((r for r in rows if isinstance(r,dict) and not r.get('unlocked') and float(r.get('progress_pct') or 0)>=50),None)
        if candidate: ui.achievement_detail=str(candidate.get('id'))
    render_ui(root,out/'achievement-detail.png','classic',state,detail)

    # Native bridge renders use the exact live Pwnagotchi frame if available.
    for tid in ('pwn_native_raw','pwn_native_dark','pwn_native_light','pwn_native_chroma'):
        render_ui(root,out/f'{tid}.png',tid,state)

    def chroma_fx(ui):
        ui.theme_options['pwn_native_chroma']={'ink_mode':'fixed','palette_mode':'cyan','glow_level':'strong','effect':'halo'}
    render_ui(root,out/'pwn-native-chroma-halo.png','pwn_native_chroma',state,chroma_fx)

    def rare(ui):
        ui.state.update({'rare.omen.active':False,'rare.moment.active':True,'rare.preview.active':True,
                         'rare.moment.id':'validation','rare.moment.rarity':'mythic','rare.moment.sigil':'eye',
                         'rare.moment.presentation':'apparition','rare.moment.remaining_sec':15})
    render_ui(root,out/'rare-apparition.png','blackice',state,rare)

if __name__=='__main__': main()
