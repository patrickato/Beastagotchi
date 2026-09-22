from __future__ import annotations

import argparse
import logging
from .engine import BeastUI


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
    a=p.parse_args()
    BeastUI(a.root,a.framebuffer,a.output,a.theme,physical_size=(a.physical_width,a.physical_height),display_mode=a.display_mode,display_resample=a.display_resample).run(a.duration)

if __name__=="__main__":main()
