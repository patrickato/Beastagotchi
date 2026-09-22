from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


def run(cmd: list[str], timeout: float = 3.0) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr
    except Exception as exc:
        return 255, "", repr(exc)


def read_text(path: str, default: str = "") -> str:
    try:
        return Path(path).read_text(errors="replace")
    except Exception:
        return default


def read_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(errors="replace"))
    except Exception:
        return None


def atomic_json_write(path: str, obj: Any, mode: int = 0o640) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, default=str))
    os.chmod(tmp, mode)
    os.replace(tmp, p)


def parse_iw_dev(text: str) -> list[dict[str, Any]]:
    interfaces: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("Interface "):
            if current:
                interfaces.append(current)
            current = {"name": line.split(None, 1)[1]}
        elif current is not None:
            if line.startswith("addr "):
                current["mac"] = line.split(None, 1)[1]
            elif line.startswith("type "):
                current["mode"] = line.split(None, 1)[1]
            elif line.startswith("channel "):
                m = re.match(r"channel\s+(\d+)\s+\((\d+)\s+MHz\)", line)
                if m:
                    current["channel"] = int(m.group(1)); current["frequency_mhz"] = int(m.group(2))
    if current:
        interfaces.append(current)
    return interfaces


def channel_to_band(channel: int | None, freq: int | None) -> str | None:
    if freq:
        if 2400 <= freq < 2500: return "2.4GHz"
        if 4900 <= freq < 5925: return "5GHz"
        if 5925 <= freq < 7125: return "6GHz"
    if channel:
        if 1 <= channel <= 14: return "2.4GHz"
        if channel >= 30: return "5GHz"
    return None
