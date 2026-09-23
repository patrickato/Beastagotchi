from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import Collector


class DisplayCollector(Collector):
    """Discover framebuffer/DRM display capabilities without taking ownership."""

    name='display'
    interval=15.0
    priority=55

    def __init__(self, graphics_root: str='/sys/class/graphics', drm_root: str='/sys/class/drm', handoff_root: str='/var/lib/beastagotchi/display-handoff', runtime_root: str='/run/beastagotchi') -> None:
        self.graphics_root=Path(graphics_root);self.drm_root=Path(drm_root);self.handoff_root=Path(handoff_root);self.runtime_root=Path(runtime_root)

    @staticmethod
    def _read(path: Path) -> str:
        try:return path.read_text(errors='replace').strip()
        except Exception:return ''

    def collect(self) -> dict[str,Any]:
        fbs=[]
        if self.graphics_root.is_dir():
            for fb in sorted(self.graphics_root.glob('fb*')):
                if not fb.name[2:].isdigit():continue
                virtual=self._read(fb/'virtual_size');bpp=self._read(fb/'bits_per_pixel');name=self._read(fb/'name')
                width=height=None
                try:width,height=(int(x) for x in virtual.split(',',1))
                except Exception:pass
                fbs.append({'id':fb.name,'device':'/dev/'+fb.name,'name':name or fb.name,'width':width,'height':height,'bpp':int(bpp) if bpp.isdigit() else None})
        outputs=[]
        if self.drm_root.is_dir():
            for conn in sorted(self.drm_root.glob('card*-*')):
                status=self._read(conn/'status')
                if not status:continue
                modes=[x.strip() for x in self._read(conn/'modes').splitlines() if x.strip()]
                outputs.append({'id':conn.name,'status':status,'modes':modes[:32],'preferred_mode':modes[0] if modes else None})
        connected=[x for x in outputs if x.get('status')=='connected']
        return {
            'display.framebuffers':fbs,
            'display.outputs':outputs,
            'display.connected_outputs':len(connected),
            'display.external_connected':bool(connected),
            'display.reference.logical_width':480,
            'display.reference.logical_height':320,
            'display.backend.current':'fbdev_rgb565',
            'display.backend.future':['fbdev','drm_kms','hdmi','dsi','window','web'],
            'display.handoff.backup_exists':(self.handoff_root/'config.toml.pre-beast').is_file(),
            'display.handoff.confirmed':(self.handoff_root/'confirmed').exists(),
            'display.handoff.test_mode':(self.runtime_root/'ui-test-mode').exists(),
        }
