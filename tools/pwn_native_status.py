#!/opt/.pwn/bin/python3
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, '/opt/beast-ui')
from beastui.pwn_native import NativePwnFrameSource

src = NativePwnFrameSource()
info = src.info()
obj = {
    'path': info.path,
    'available': info.available,
    'width': info.width,
    'height': info.height,
    'age_sec': None if info.age_sec is None else round(info.age_sec, 3),
    'error': info.error,
    'rotation': info.rotation,
    'exact_480x320': bool(info.available and (info.width, info.height) == (480, 320)),
}
print(json.dumps(obj, indent=2))
