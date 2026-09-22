from pathlib import Path
from beastui.engine import BeastUI
from beastui.face import PWN_CLASSIC_FACES
from beastui.theme import load_theme

ROOT=Path(__file__).resolve().parents[1]/'beastui'

def test_original_pwnagotchi_themes_are_first_class():
    assert all(t in BeastUI.THEMES for t in ['pwn_dark','pwn_light','pwn_chroma'])
    dark=load_theme(ROOT/'themes/pwn_dark.json')
    light=load_theme(ROOT/'themes/pwn_light.json')
    assert dark.face_style=='pwnclassic' and dark.c('bg')==(0,0,0) and dark.c('primary')==(255,255,255)
    assert light.face_style=='pwnclassic' and light.c('bg')==(255,255,255) and light.c('primary')==(0,0,0)

def test_pwnclassic_face_vocabulary_preserves_stock_identity():
    assert PWN_CLASSIC_FACES['awake']=='(◕‿‿◕)'
    assert PWN_CLASSIC_FACES['cool']=='(⌐■_■)'
    assert PWN_CLASSIC_FACES['sleep']=='(⇀‿‿↼)'
    assert PWN_CLASSIC_FACES['angry']=="(-_-')"

def test_chroma_uses_original_face_with_mood_colors(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'chroma.png'),theme_id='pwn_chroma')
    ui.state={'pwnagotchi.mood':'angry','health.core.state':'healthy'}
    im=ui.render()
    assert im.size==(480,320)
    assert ui.theme.face_style=='pwnclassic'
    assert ui.theme.mood_colors['angry']==(255,48,48)
