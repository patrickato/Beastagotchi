from __future__ import annotations

import argparse
import logging

from .runtime import RuntimeBeastUI
from .experience_live_optimized import ExperienceBeastUI
from .experience_registry import experience_renderer_summary


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    p=argparse.ArgumentParser(prog="beast-ui")
    p.add_argument("--root",default="/opt/beast-ui")
    p.add_argument("--framebuffer",default="/dev/fb1")
    p.add_argument("--output",help="render to PNG instead of framebuffer")
    p.add_argument("--theme",default="classic")
    p.add_argument("--duration",type=float,default=0.0)
    p.add_argument("--physical-width",type=int,default=480,help="physical/output width; logical Beast canvas remains 480")
    p.add_argument("--physical-height",type=int,default=320,help="physical/output height; logical Beast canvas remains 320")
    p.add_argument("--display-mode",choices=("fit","stretch","native"),default="fit")
    p.add_argument("--display-resample",choices=("nearest","bilinear","bicubic","lanczos"),default="bilinear")
    p.add_argument(
        "--experience",
        choices=tuple(experience_renderer_summary()),
        help="explicit staging-only Experience renderer; does not change saved UI preferences",
    )
    p.add_argument(
        "--experience-page",
        default="home",
        help="initial page for --experience; invalid pages fall back to that Experience's authored first page",
    )
    a=p.parse_args()
    common=dict(
        physical_size=(a.physical_width,a.physical_height),
        display_mode=a.display_mode,
        display_resample=a.display_resample,
    )
    if a.experience:
        ui=ExperienceBeastUI(
            a.root,a.framebuffer,a.output,a.theme,
            experience_id=a.experience,
            experience_page=a.experience_page,
            **common,
        )
    else:
        # Default/production path uses the canonical preference-store adapter
        # (from the architecture-foundation tranche) so runtime UI preference
        # writes go through the canonical store.
        ui=RuntimeBeastUI(a.root,a.framebuffer,a.output,a.theme,**common)
    ui.run(a.duration)

if __name__=="__main__":main()
