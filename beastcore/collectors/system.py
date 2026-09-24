from __future__ import annotations

import os
import platform
import socket
import time
from pathlib import Path
from typing import Any

from .base import Collector
from ..util import read_text, run

class SystemCollector(Collector):
    name = "system"
    interval = 1.0
    priority = 70

    def __init__(self) -> None:
        self._last_cpu: dict[str, tuple[int, int]] = {}
        self._static: dict[str, Any] | None = None
        self._throttle_value: str | None = None
        self._throttle_at = 0.0
        self._clock_synced: bool | None = None
        self._clock_at = 0.0
        self._pi_clock_values: dict[str, Any] = {}
        self._pi_clock_at = 0.0

    @staticmethod
    def _cpu_rows() -> dict[str, tuple[int, int]]:
        out: dict[str, tuple[int, int]] = {}
        for line in read_text("/proc/stat").splitlines():
            if not line.startswith("cpu"): continue
            parts = line.split()
            if not parts[0].startswith("cpu"): continue
            vals = [int(x) for x in parts[1:11]]
            idle = vals[3] + vals[4]
            total = sum(vals)
            out[parts[0]] = (total, idle)
        return out

    def _cpu_pct(self) -> dict[str, float | None]:
        cur = self._cpu_rows(); result: dict[str, float | None] = {}
        for name, (total, idle) in cur.items():
            prev = self._last_cpu.get(name)
            if not prev:
                result[name] = None
            else:
                dt = total - prev[0]; di = idle - prev[1]
                result[name] = round((1.0 - (di / dt)) * 100.0, 2) if dt > 0 else None
        self._last_cpu = cur
        return result

    @staticmethod
    def _mem() -> dict[str, int]:
        m: dict[str, int] = {}
        for line in read_text("/proc/meminfo").splitlines():
            if ":" not in line: continue
            k, v = line.split(":", 1)
            try: m[k] = int(v.strip().split()[0]) * 1024
            except Exception: pass
        return m

    @staticmethod
    def _parse_clock_hz(text: str) -> float | None:
        try:
            raw=str(text or '').strip().split('=',1)[-1]
            return round(int(raw)/1_000_000.0,2)
        except Exception:return None

    @staticmethod
    def _parse_mem_mb(text: str) -> int | None:
        try:
            raw=str(text or '').strip().split('=',1)[-1].strip().lower().removesuffix('m')
            return int(raw)
        except Exception:return None

    def collect(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        cpu = self._cpu_pct()
        if cpu.get("cpu") is not None: values["system.cpu.total"] = cpu["cpu"]
        for idx in range(4):
            key = f"cpu{idx}"
            if cpu.get(key) is not None: values[f"system.cpu.core{idx}"] = cpu[key]
        try:
            l1, l5, l15 = os.getloadavg()
            values.update({"system.load.1m": l1, "system.load.5m": l5, "system.load.15m": l15})
        except Exception: pass
        mem = self._mem(); total = mem.get("MemTotal", 0); avail = mem.get("MemAvailable", mem.get("MemFree", 0))
        if total:
            used = max(total - avail, 0)
            values["system.memory.used_pct"] = round(used / total * 100, 2)
            values["system.memory.used_mb"] = round(used / 1048576, 1)
            values["system.memory.free_mb"] = round(avail / 1048576, 1)
            values["system.ram_mb"] = round(total / 1048576)
        st = mem.get("SwapTotal", 0); sf = mem.get("SwapFree", 0)
        values["system.swap.used_pct"] = round((st - sf) / st * 100, 2) if st else 0.0
        temp = read_text("/sys/class/thermal/thermal_zone0/temp").strip()
        if temp.isdigit(): values["system.temp.cpu_c"] = round(int(temp) / 1000.0, 2)
        up = read_text("/proc/uptime").split()
        if up:
            try:
                uptime = float(up[0]); values["system.uptime_sec"] = uptime; values["system.boot_time"] = time.time() - uptime
            except Exception: pass
        if self._static is None:
            static = {"system.hostname": socket.gethostname(), "system.kernel": platform.release(), "system.architecture": platform.machine(), "system.os": platform.system()}
            model = read_text("/proc/device-tree/model").replace("\x00", "").strip()
            if model: static["system.model"] = model
            self._static = static
        values.update(self._static)

        # These shell-outs are useful, but they do not need to run every second.
        # Keep fast telemetry fast while moving slow facts to appropriate cadences.
        mono = time.monotonic()
        if mono - self._throttle_at >= 5.0 or self._throttle_value is None:
            rc, out, _ = run(["vcgencmd", "get_throttled"], timeout=1.5)
            if rc == 0 and "=" in out:
                self._throttle_value = out.strip().split("=", 1)[1]
            self._throttle_at = mono
        if self._throttle_value is not None:
            values["system.throttle.flags"] = self._throttle_value

        # Pi clock/GPU allocation telemetry is useful in Performance/Hardware
        # Studio, but vcgencmd shell-outs are cached so instrumentation itself
        # does not become a thermal load.
        if mono - self._pi_clock_at >= 10.0 or not self._pi_clock_values:
            slow: dict[str, Any] = {}
            rc,out,_=run(["vcgencmd","measure_clock","arm"],timeout=1.5)
            if rc==0:
                v=self._parse_clock_hz(out)
                if v is not None:slow["system.clock.arm_mhz"]=v
            rc,out,_=run(["vcgencmd","measure_clock","core"],timeout=1.5)
            if rc==0:
                v=self._parse_clock_hz(out)
                if v is not None:slow["system.clock.core_mhz"]=v
            rc,out,_=run(["vcgencmd","get_mem","gpu"],timeout=1.5)
            if rc==0:
                v=self._parse_mem_mb(out)
                if v is not None:slow["system.gpu.mem_mb"]=v
            self._pi_clock_values=slow
            self._pi_clock_at=mono
        values.update(self._pi_clock_values)

        if mono - self._clock_at >= 60.0 or self._clock_synced is None:
            rc, out, _ = run(["timedatectl", "show", "-p", "NTPSynchronized", "--value"], timeout=1.5)
            if rc == 0:
                self._clock_synced = out.strip().lower() == "yes"
            self._clock_at = mono
        if self._clock_synced is not None:
            values["system.clock.synced"] = self._clock_synced
        return values
