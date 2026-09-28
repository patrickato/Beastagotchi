from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from beastui.experience_registry import render_experience_page
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
        ("atlas","home"),
        ("atlas","recon"),
        ("observatory","home"),
        ("observatory","spectrum"),
        ("habitat","home"),
        ("habitat","beast"),
        ("forge","home"),
        ("forge","system"),
        ("monolith","home"),
        ("monolith","overview"),
    ]
    manifest={"purpose":"active-registry cross-page Experience-DNA translation proof","pages":{}}
    cards=[]
    for experience_id,page_id in cases:
        name=f"{experience_id}_{page_id}"
        rt=SceneRuntime()
        im=render_experience_page(experience_id,page_id,state,scene_runtime=rt)
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
