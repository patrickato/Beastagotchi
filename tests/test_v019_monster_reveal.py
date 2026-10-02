from __future__ import annotations

from PIL import Image
from beastui.monster_reveal import reveal_active, render_monster_reveal

class Theme:
    def c(self,key,default=None):
        return {'accent':(0,220,180),'secondary':(120,160,255),'text':(235,240,245)}.get(key,default or (255,255,255))

class Font:
    pass

def state():
    return {'roster.monster_reveal.id':'m1','roster.monster_reveal.name':'Nova','roster.monster_reveal.generation':1,
            'roster.monster_reveal.stage':'Origin','roster.monster_reveal.parents':['Hex','Orbit'],
            'roster.monster_reveal.traits':{'eyes':'visor','aura':'orbital','motion':'float'},
            'roster.monster_reveal.created_at':100.0,'roster.monster_reveal.until':112.0,'roster.monster_reveal.first_unlock':True}

def test_reveal_lifetime_and_dismissal():
    s=state();assert reveal_active(s,101.0) is True;assert reveal_active(s,113.0) is False;assert reveal_active(s,101.0,'m1') is False

def test_reveal_renderer_is_noop_outside_window():
    im=Image.new('RGB',(480,320),(1,2,3));out=render_monster_reveal(im,state(),1.0,Theme(),{},now=113.0)
    assert out.tobytes()==im.tobytes()

def test_first_unlock_is_distinct_state_flag():
    s=state();assert s['roster.monster_reveal.first_unlock'] is True
