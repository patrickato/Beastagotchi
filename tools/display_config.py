#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

SECTION_RE = re.compile(r"(?ms)^\[ui\.display\]\s*$.*?(?=^\[|\Z)")
ENABLED_RE = re.compile(r"(?m)^(\s*enabled\s*=\s*)(true|false)(\s*(?:#.*)?)$")


def load(path: Path) -> str:
    return path.read_text()


def find_section(text: str):
    return SECTION_RE.search(text)


def get_enabled(text: str):
    m = find_section(text)
    if not m:
        return None
    e = ENABLED_RE.search(m.group(0))
    if not e:
        return None
    return e.group(2).lower() == "true"


def set_enabled_text(text: str, value: bool) -> str:
    m = find_section(text)
    if not m:
        raise RuntimeError("[ui.display] section not found")
    sec = m.group(0)
    rep = "true" if value else "false"
    if ENABLED_RE.search(sec):
        new_sec = ENABLED_RE.sub(lambda x: f"{x.group(1)}{rep}{x.group(3)}", sec, count=1)
    else:
        lines = sec.splitlines(True)
        if not lines:
            raise RuntimeError("empty [ui.display] section")
        nl = "\n" if lines[0].endswith("\n") else os.linesep
        lines.insert(1, f"enabled = {rep}{nl}")
        new_sec = "".join(lines)
    return text[:m.start()] + new_sec + text[m.end():]


def atomic_write(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".beast-tmp")
    st = path.stat()
    tmp.write_text(content)
    os.chmod(tmp, st.st_mode)
    try:
        os.chown(tmp, st.st_uid, st.st_gid)
    except PermissionError:
        pass
    os.replace(tmp, path)


def cmd_status(args) -> int:
    p = Path(args.config)
    text = load(p)
    out = {
        "config": str(p),
        "exists": p.exists(),
        "ui_display_section": find_section(text) is not None,
        "enabled": get_enabled(text),
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_disable(args) -> int:
    p = Path(args.config); b = Path(args.backup)
    text = load(p)
    if find_section(text) is None:
        raise RuntimeError("[ui.display] section not found; refusing to edit")
    b.parent.mkdir(parents=True, exist_ok=True)
    if b.exists() and not args.reuse_backup:
        raise RuntimeError(f"backup already exists: {b}")
    if not b.exists():
        shutil.copy2(p, b)
    atomic_write(p, set_enabled_text(text, False))
    print(json.dumps({"ok": True, "enabled": get_enabled(load(p)), "backup": str(b)}, indent=2))
    return 0


def cmd_restore(args) -> int:
    p = Path(args.config); b = Path(args.backup)
    if not b.exists():
        raise RuntimeError(f"backup missing: {b}")
    shutil.copy2(b, p)
    print(json.dumps({"ok": True, "enabled": get_enabled(load(p)), "restored_from": str(b)}, indent=2))
    return 0


def cmd_require_disabled(args) -> int:
    p = Path(args.config)
    enabled = get_enabled(load(p))
    if enabled is False:
        print("display-disabled-safe")
        return 0
    print(f"unsafe: ui.display.enabled={enabled}", file=sys.stderr)
    return 4


def cmd_require_enabled(args) -> int:
    p = Path(args.config)
    enabled = get_enabled(load(p))
    if enabled is True:
        print("display-enabled")
        return 0
    print(f"unexpected: ui.display.enabled={enabled}", file=sys.stderr)
    return 4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="/etc/pwnagotchi/config.toml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    d = sub.add_parser("disable"); d.add_argument("--backup", required=True); d.add_argument("--reuse-backup", action="store_true")
    r = sub.add_parser("restore"); r.add_argument("--backup", required=True)
    sub.add_parser("require-disabled")
    sub.add_parser("require-enabled")
    a = ap.parse_args()
    try:
        return {"status":cmd_status,"disable":cmd_disable,"restore":cmd_restore,"require-disabled":cmd_require_disabled,"require-enabled":cmd_require_enabled}[a.cmd](a)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
