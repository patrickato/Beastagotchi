from __future__ import annotations
import colorsys
import math
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


def palette_color(name:str, phase:float, fallback=(0,255,140)):
    n=str(name or 'green').lower()
    fixed={
        'green':(0,255,92),'lime':(137,255,57),'cyan':(0,229,255),'blue':(65,125,255),
        'amber':(255,174,35),'yellow':(255,226,65),'orange':(255,126,34),
        'violet':(190,80,255),'magenta':(255,66,220),'red':(255,54,74),'white':(255,255,255),
    }
    if n=='rainbow':
        h=(phase*0.035)%1.0
        return tuple(int(v*255) for v in colorsys.hsv_to_rgb(h,0.9,1.0))
    return fixed.get(n,fallback)


def apply_native_effects(image:Image.Image, phase:float, options:dict|None=None, ink=(0,255,140))->Image.Image:
    """Post-process the exact native Pwnagotchi canvas without reconstructing it.

    These effects are intentionally independent from the Pwnagotchi face/state
    logic: the source pixels still come from Jayofelony's real View.  This is the
    Beast-native counterpart to the color/effect ideas explored by Korrie71's
    theme manager.
    """
    o=dict(options or {})
    effect=str(o.get('effect','clean')).lower()
    out=image.convert('RGB')

    if effect=='pulse':
        amount=0.92+0.16*(0.5+0.5*math.sin(phase*2.2))
        out=ImageEnhance.Brightness(out).enhance(amount)

    if effect=='vignette':
        ov=Image.new('RGBA',out.size,(0,0,0,0));d=ImageDraw.Draw(ov)
        w,h=out.size
        for i in range(18):
            a=int(7+i*3.2)
            d.rectangle((i,i,w-1-i,h-1-i),outline=(0,0,0,a),width=2)
        out=Image.alpha_composite(out.convert('RGBA'),ov).convert('RGB')

    elif effect=='scanlines':
        ov=Image.new('RGBA',out.size,(0,0,0,0));d=ImageDraw.Draw(ov)
        for y in range(0,out.height,4):d.line((0,y,out.width-1,y),fill=(0,0,0,42),width=1)
        out=Image.alpha_composite(out.convert('RGBA'),ov).convert('RGB')

    elif effect=='grain':
        # Sparse deterministic grain: cheap enough for the Pi and visually
        # obvious without touching every pixel in Python.
        ov=Image.new('RGBA',out.size,(0,0,0,0));d=ImageDraw.Draw(ov)
        seed=int(phase*8.0)
        for i in range(180):
            v=(i*1103515245 + seed*12345 + 0x9e3779b9) & 0xffffffff
            x=v%out.width; y=((v>>9)^(v*33))%out.height; a=18+((v>>19)&31)
            d.point((x,y),fill=(255,255,255,a) if v&1 else (0,0,0,a))
        out=Image.alpha_composite(out.convert('RGBA'),ov).convert('RGB')

    elif effect=='glitch':
        # A restrained, intermittent slice displacement. The original pixels
        # are moved, not replaced by a replica face.
        if int(phase*3.0)%11 in {0,1}:
            src=out.copy(); dseed=int(phase*37)
            for i in range(4):
                y=(dseed*17+i*61)%max(1,out.height-10); hh=3+((dseed+i*13)%8); shift=(-1 if i%2 else 1)*(3+((dseed+i)%9))
                strip=src.crop((0,y,out.width,min(out.height,y+hh)))
                out.paste(strip,(shift,y))

    elif effect=='halo':
        # Soft outline-like glow around all native ink, useful for dark themes.
        gray=out.convert('L'); mask=gray.point(lambda p:255 if p>40 else 0).filter(ImageFilter.GaussianBlur(2.2))
        layer=Image.new('RGB',out.size,tuple(int(c*0.28) for c in ink)); out.paste(layer,(0,0),mask)
        # Re-paste source to retain crisp exact glyph edges.
        out=Image.blend(out,image.convert('RGB'),0.72)

    return out
