from __future__ import annotations

import time
from pathlib import Path
from PIL import Image, ImageDraw

from beastui.engine import BeastUI

ROOT=Path(__file__).resolve().parents[1]/'beastui'


def _danger_pixels(ui,phase):
    ui.phase=phase
    ui.events=[{'type':'system.thermal_band','ts':time.time(),'data':{'from':'hot','to':'critical','temp_c':80.3}}]
    im=Image.new('RGB',(480,320),ui.theme.c('bg'))
    d=ImageDraw.Draw(im)
    ui._event_reaction(d)
    danger=ui.theme.c('danger')
    return {(x,y) for y in range(55,276) for x in range(480) if im.getpixel((x,y))==danger}


def test_matrix_danger_reaction_no_longer_translates_diagonally(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='matrix')
    a=_danger_pixels(ui,1.0); b=_danger_pixels(ui,2.0)
    # Dynamic pulse lengths may change, but reaction columns must stay on the
    # same fixed X coordinates instead of marching X+Y together.
    xa={x for x,y in a if 65 <= y <= 245}
    xb={x for x,y in b if 65 <= y <= 245}
    assert xa == xb
    allowed=set()
    for x in (28,86,151,219,288,354,417,462): allowed.update({x,x+1})
    assert xa.issubset(allowed)


def test_matrix_reactions_can_be_disabled(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='matrix')
    ui.theme_options['matrix']={'reactions_enabled':'off'}
    ui.phase=1.0
    ui.events=[{'type':'system.thermal_band','ts':time.time(),'data':{'to':'critical'}}]
    im=Image.new('RGB',(480,320),ui.theme.c('bg'))
    before=im.tobytes(); ui._event_reaction(ImageDraw.Draw(im))
    assert im.tobytes()==before


def test_matrix_theme_studio_exposes_reaction_toggle(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='matrix')
    rows=ui._matrix_option_rows()
    row=next(r for r in rows if r[0]=='reactions_enabled')
    assert row[2]==['on','off']


def test_achievement_touch_partitions_do_not_compete_at_boundaries(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.achievements_overlay=True
    ui.state={'progression.achievements.catalog':[
        {'id':'one','label':'One','unlocked':False,'progress_pct':10},
        {'id':'two','label':'Two','unlocked':False,'progress_pct':20},
    ],'progression.awards.catalog':[]}
    # Bottom of filter zone must still be filter, first pixel below it must be row 1.
    ui.achievement_filter='all'
    ui.on_input('tap',{'x':100,'y':121})
    assert ui.achievement_filter=='unlocked'
    ui.achievement_filter='all'
    ui.on_input('tap',{'x':100,'y':122})
    assert ui.achievement_detail in {'one','two'}
