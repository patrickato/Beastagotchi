#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image


def main():
    p=argparse.ArgumentParser(); p.add_argument("device"); p.add_argument("output"); p.add_argument("--width",type=int,default=480); p.add_argument("--height",type=int,default=320); a=p.parse_args()
    need=a.width*a.height*2
    with open(a.device,"rb",buffering=0) as f: raw=f.read(need)
    if len(raw)!=need: raise SystemExit(f"expected {need} bytes, got {len(raw)}")
    pix=[]
    for i in range(0,len(raw),2):
        v=raw[i] | (raw[i+1]<<8)
        r=((v>>11)&31)*255//31; g=((v>>5)&63)*255//63; b=(v&31)*255//31
        pix.append((r,g,b))
    im=Image.new("RGB",(a.width,a.height)); im.putdata(pix); Path(a.output).parent.mkdir(parents=True,exist_ok=True); im.save(a.output)
    print(a.output)
if __name__=="__main__": main()
