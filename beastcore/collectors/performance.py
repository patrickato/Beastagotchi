from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from .base import Collector


class PerformanceCollector(Collector):
    """Attribute CPU/RAM/UI rendering cost to the services Beast actually uses.

    This is intentionally lightweight and dependency-free.  PID discovery scans
    /proc only occasionally; per-process CPU/RSS samples are then read from the
    remembered PIDs.  Values are descriptive telemetry, not a control loop.
    """

    name = "performance"
    interval = 2.0
    priority = 55

    TARGETS = {
        "beast_ui": ("Beast UI", ("-m beastui", "/beastui/", " beastui")),
        "beast_core": ("Beast Core", ("-m beastcore", "/beastcore/", " beastcore")),
        "beast_studio": ("Beast Studio", ("-m beaststudio", "/beaststudio/", " beaststudio")),
        "pwnagotchi": ("Pwnagotchi", ("pwnagotchi",)),
        "bettercap": ("Bettercap", ("bettercap",)),
        "gpsd": ("gpsd", ("gpsd",)),
    }

    def __init__(self, proc_root: str = "/proc", runtime_path: str = "/var/lib/beastagotchi/ui/runtime.json",
                 *, clock=time.monotonic) -> None:
        self.proc_root = Path(proc_root)
        self.runtime_path = Path(runtime_path)
        self.clock = clock
        self._pids: dict[str, list[int]] = {}
        self._pid_scan_at = 0.0
        self._previous: dict[int, tuple[float, float]] = {}
        try:
            self._hz = float(os.sysconf("SC_CLK_TCK"))
        except Exception:
            self._hz = 100.0
        try:
            self._page_size = float(os.sysconf("SC_PAGE_SIZE"))
        except Exception:
            self._page_size = 4096.0

    def _cmdline(self, pid: int) -> str:
        try:
            raw = (self.proc_root / str(pid) / "cmdline").read_bytes().replace(b"\0", b" ")
            return " " + raw.decode(errors="replace").strip().lower()
        except Exception:
            return ""

    def _discover(self) -> None:
        found = {k: [] for k in self.TARGETS}
        try:
            dirs = list(self.proc_root.iterdir())
        except Exception:
            dirs = []
        for entry in dirs:
            if not entry.name.isdigit():
                continue
            pid = int(entry.name)
            cmd = self._cmdline(pid)
            if not cmd:
                continue
            for key, (_label, needles) in self.TARGETS.items():
                # Beast-specific entries are checked before generic Pwnagotchi so
                # a path containing the word pwnagotchi does not steal Beast PIDs.
                if any(n in cmd for n in needles):
                    found[key].append(pid)
                    break
        self._pids = found
        self._pid_scan_at = float(self.clock())

    def _stat(self, pid: int) -> tuple[float, float] | None:
        """Return process CPU ticks and RSS MiB."""
        try:
            text = (self.proc_root / str(pid) / "stat").read_text(errors="replace")
            # comm may contain spaces inside parentheses. Everything after the
            # final ')' resumes the ordinary /proc/<pid>/stat fields at #3.
            tail = text[text.rfind(")") + 2:].split()
            # tail[11] = field 14 utime, tail[12] = field 15 stime.
            ticks = float(tail[11]) + float(tail[12])
            statm = (self.proc_root / str(pid) / "statm").read_text().split()
            rss_pages = float(statm[1]) if len(statm) > 1 else 0.0
            rss_mb = rss_pages * self._page_size / 1048576.0
            return ticks, rss_mb
        except Exception:
            return None

    def _runtime(self) -> dict[str, Any]:
        try:
            obj = json.loads(self.runtime_path.read_text(errors="replace"))
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def collect(self) -> dict[str, Any]:
        now = float(self.clock())
        if not self._pids or now - self._pid_scan_at >= 10.0:
            self._discover()

        rows: list[dict[str, Any]] = []
        beast_cpu = platform_cpu = total_rss = 0.0
        live_pids: set[int] = set()
        for key, (label, _needles) in self.TARGETS.items():
            cpu = rss = 0.0
            pids = []
            for pid in list(self._pids.get(key) or []):
                sample = self._stat(pid)
                if sample is None:
                    continue
                pids.append(pid); live_pids.add(pid)
                ticks, rss_mb = sample; rss += rss_mb
                prev = self._previous.get(pid)
                if prev is not None:
                    prev_ticks, prev_at = prev
                    dt = max(0.001, now - prev_at)
                    cpu += max(0.0, (ticks - prev_ticks) / self._hz / dt * 100.0)
                self._previous[pid] = (ticks, now)
            if pids:
                row = {"id": key, "label": label, "pids": pids,
                       "cpu_pct": round(cpu, 2), "rss_mb": round(rss, 1)}
                rows.append(row); total_rss += rss
                if key.startswith("beast_"): beast_cpu += cpu
                else: platform_cpu += cpu
        self._previous = {pid:v for pid,v in self._previous.items() if pid in live_pids}

        runtime = self._runtime()
        fb = runtime.get("framebuffer") if isinstance(runtime.get("framebuffer"), dict) else {}
        frame_bytes = int(fb.get("frame_bytes") or 0); written = int(fb.get("bytes_written") or 0)
        values: dict[str, Any] = {
            "performance.processes": rows,
            "performance.beast.cpu_pct": round(beast_cpu, 2),
            "performance.platform_services.cpu_pct": round(platform_cpu, 2),
            "performance.tracked.rss_mb": round(total_rss, 1),
            "performance.process_count": len(rows),
        }
        if runtime:
            values.update({
                "performance.ui.avg_render_ms": runtime.get("avg_render_ms"),
                "performance.ui.avg_compose_ms": runtime.get("avg_compose_ms"),
                "performance.ui.avg_fb_write_ms": runtime.get("avg_fb_write_ms"),
                "performance.ui.target_fps": runtime.get("target_fps"),
                "performance.ui.lifetime_fps": runtime.get("lifetime_fps"),
                "performance.ui.theme": runtime.get("theme"),
                "performance.ui.page": runtime.get("page"),
                "performance.fb.changed_rows": fb.get("changed_rows"),
                "performance.fb.bytes_written": written,
                "performance.fb.frame_bytes": frame_bytes,
                "performance.fb.full_write": fb.get("full_write"),
                "performance.fb.write_ratio_pct": round((written / frame_bytes * 100.0), 1) if frame_bytes else None,
                "performance.fb.saved_bytes": fb.get("saved_bytes"),
            })
            totals = fb.get("totals") if isinstance(fb.get("totals"), dict) else {}
            if totals:
                values.update({
                    "performance.fb.total_frames": totals.get("frames"),
                    "performance.fb.total_bytes_written": totals.get("bytes_written"),
                    "performance.fb.total_full_writes": totals.get("full_writes"),
                    "performance.fb.total_saved_bytes": totals.get("saved_bytes"),
                })
        return values
