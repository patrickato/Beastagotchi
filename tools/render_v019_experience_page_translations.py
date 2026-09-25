from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from beastui.experience_atlas import render_atlas_home, render_atlas_recon
from beastui.experience_observatory import render_observatory_home, render_observatory_spectrum
from beastui.experience_habitat import render_habitat_home, render_habitat_beast
from beastui.experience_forge import render_forge_home, render_forge_system
from beastui.experience_monolith import render_monolith_home, render_monolith_overview
from beastui.scene_runtime import SceneRuntime


def _card(label, im):
    out=Image.new("RGB",(480,350),(10,10,10))
    out.paste(im,(0,30))
    d=ImageDraw.Draw(out)
    try: font=ImageFont.truetype("DejaVuSans.ttf",15)
    except Exception: font=ImageFont.load_default()
    d.text((10,7),label,fill=(235,235,230),font=font)
    return out


def main()->int:
    state=json.loads(Path("tests/fixtures/v018_target_sanitized_state.json").read_text())
    root=Path("artifacts/v019-experience-page-translations")
    root.mkdir(parents=True,exist_ok=True)

    cases=[
        ("atlas_home",render_atlas_home),
        ("atlas_recon",render_atlas_recon),
        ("observatory_home",render_observatory_home),
        ("observatory_spectrum",render_observatory_spectrum),
        ("habitat_home",render_habitat_home),
        ("habitat_beast",render_habitat_beast),
        ("forge_home",render_forge_home),
        ("forge_system",render_forge_system),
        ("monolith_home",render_monolith_home),
        ("monolith_overview",render_monolith_overview),
    ]
    manifest={"purpose":"cross-page Experience-DNA translation proof","pages":{}}
    cards=[]
    for name,renderer in cases:
        rt=SceneRuntime()
        im=renderer(state,scene_runtime=rt)
        fp=root/f"{name}.png"
        im.save(fp)
        manifest["pages"][name]={"file":fp.name,"scene":rt.snapshot()}
        cards.append(_card(name.replace("_"," ").upper(),im))

    cols=3;rows=(len(cards)+cols-1)//cols
    sheet=Image.new("RGB",(cols*480,rows*350),(8,8,8))
    for idx,card in enumerate(cards):
        sheet.paste(card,((idx%cols)*480,(idx//cols)*350))
    sheet.save(root/"comparison.png")
    manifest["comparison"]="comparison.png"
    (root/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(root)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
