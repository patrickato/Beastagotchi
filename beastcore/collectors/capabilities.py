from __future__ import annotations

import re
from typing import Any

from .base import Collector
from ..util import run

KNOWN = {
    "0e8d:7612": {
        "name":"ALFA AWUS036ACM", "class":"wifi", "chipset":"MediaTek MT7612U",
        "bands":["2.4GHz","5GHz"], "candidate_roles":["scout","management","monitor","kismet"],
        "verification":"runtime_required",
    },
    "7392:7811": {
        "name":"Edimax EW-7811Un", "class":"wifi", "chipset":"Realtek RTL8188CUS",
        "bands":["2.4GHz"], "candidate_roles":["management","scout"], "verification":"runtime_required",
    },
    "1546:01a7": {
        "name":"u-blox GPS", "class":"gps", "candidate_roles":["navigation"], "verification":"known_present",
    },
}


class CapabilityCollector(Collector):
    """Turns attached hardware into stable capability records.

    Unknown hardware is never rejected; it is surfaced as an unclassified USB device
    so a future adapter can claim it without changing the core collector.
    """
    name = "capabilities"
    interval = 5.0
    priority = 60

    def collect(self) -> dict[str, Any]:
        rc, out, _ = run(["lsusb"], timeout=3)
        devices=[]; caps=set()
        if rc == 0:
            for line in out.splitlines():
                m=re.search(r"ID\s+([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\s*(.*)$", line)
                if not m: continue
                usb_id=m.group(1).lower(); desc=m.group(2).strip()
                rec={"usb_id":usb_id,"description":desc,"raw":line}
                profile=KNOWN.get(usb_id)
                if profile:
                    rec.update(profile)
                    caps.add(profile["class"])
                    for role in profile.get("candidate_roles",[]): caps.add(f"role:{role}")
                else:
                    d=desc.lower()
                    if any(x in d for x in ("bluetooth","bt radio")): rec["class"]="bluetooth"; caps.add("bluetooth")
                    elif any(x in d for x in ("rtl2838","rtl-sdr","realtek semiconductor corp. rtl2838")): rec["class"]="sdr"; caps.add("sdr")
                    elif "keyboard" in d: rec["class"]="keyboard"; caps.add("keyboard")
                    elif "mouse" in d: rec["class"]="mouse"; caps.add("mouse")
                    elif "ethernet" in d: rec["class"]="ethernet"; caps.add("ethernet")
                    else: rec["class"]="usb"
                devices.append(rec)
        # A few capability facts exist without USB discovery.
        if __import__('pathlib').Path('/dev/fb1').exists(): caps.add('display')
        if __import__('pathlib').Path('/dev/i2c-1').exists(): caps.add('i2c')
        return {
            "capabilities.usb_devices": devices,
            "capabilities.present": sorted(caps),
            "capabilities.count": len(caps),
            "capabilities.awus036acm.present": any(d.get('name')=='ALFA AWUS036ACM' for d in devices),
            "capabilities.rtlsdr.present": any(d.get('class')=='sdr' for d in devices),
        }
