from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

from beastui.engine import BeastUI
from beastui.pwn_native import NativePwnFrameSource
from beastui.theme import load_theme

ROOT=Path(__file__).resolve().parents[1]/'beastui'


def _stock_like(path: Path):
    im=Image.new('1',(480,320),1)
    d=ImageDraw.Draw(im)
    d.rectangle((10,10,180,35),fill=0)
    d.rectangle((175,100,305,145),fill=0)
    d.rectangle((20,285,455,305),fill=0)
    im.save(path)
    return im


def test_native_themes_are_first_and_distinct():
    assert BeastUI.THEMES[:4]==['pwn_native_raw','pwn_native_dark','pwn_native_light','pwn_native_chroma']
    for tid in BeastUI.THEMES[:4]:
        th=load_theme(ROOT/f'themes/{tid}.json')
        assert th.face_style=='pwn_native'
    assert load_theme(ROOT/'themes/pwn_dark.json').label.startswith('Pwnagotchi Replica')


def test_native_bridge_preserves_mask_and_forces_requested_polarity(tmp_path):
    src_path=tmp_path/'pwnagotchi.png'
    original=_stock_like(src_path)
    src=NativePwnFrameSource(src_path)
    dark=src.render('dark',(480,320))
    light=src.render('light',(480,320))
    assert dark.size==original.size==light.size
    # background and foreground polarity are intentional and opposite
    assert dark.getpixel((470,250))==(0,0,0)
    assert dark.getpixel((20,20))==(255,255,255)
    assert light.getpixel((470,250))==(255,255,255)
    assert light.getpixel((20,20))==(0,0,0)


def test_native_raw_preserves_source_pixels(tmp_path):
    src_path=tmp_path/'pwnagotchi.png'; original=_stock_like(src_path).convert('RGB')
    cfg=tmp_path/'config.toml'; cfg.write_text('[ui.display]\nrotation = 0\n')
    src=NativePwnFrameSource(src_path,cfg)
    raw=src.render('raw',(480,320))
    assert raw.tobytes() == original.tobytes()


def test_native_chroma_uses_exact_native_mask(tmp_path):
    src_path=tmp_path/'pwnagotchi.png'; _stock_like(src_path)
    src=NativePwnFrameSource(src_path)
    chroma=src.render('chroma',(480,320),ink_color=(12,200,99),glow=False)
    assert chroma.getpixel((470,250))==(0,0,0)
    assert chroma.getpixel((20,20))==(12,200,99)


def test_native_theme_renders_source_frame_without_beast_chrome(tmp_path, monkeypatch):
    src_path=tmp_path/'pwnagotchi.png'; _stock_like(src_path)
    monkeypatch.setenv('BEAST_PWN_FRAME_PATH',str(src_path))
    out=tmp_path/'native.png'
    ui=BeastUI(root=ROOT,output=str(out),theme_id='pwn_native_dark')
    ui.state={'health.core.state':'healthy','pwnagotchi.mood':'awake'}
    im=ui.render()
    assert im.size==(480,320)
    # Stock source mark remains present in the same coordinate and Beast header
    # is not painted over it.
    assert im.getpixel((20,20))==(255,255,255)
    assert not ui.drawer


def test_native_mode_long_press_opens_beast_control_center(tmp_path, monkeypatch):
    src_path=tmp_path/'pwnagotchi.png'; _stock_like(src_path)
    monkeypatch.setenv('BEAST_PWN_FRAME_PATH',str(src_path))
    ui=BeastUI(root=ROOT,output=str(tmp_path/'native2.png'),theme_id='pwn_native_light')
    ui.on_input('long_press',{'x':240,'y':160,'duration':1.0})
    assert ui.drawer is True
