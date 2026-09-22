from __future__ import annotations

import fcntl
import os
from pathlib import Path
from typing import Any

from .base import Collector

I2C_SLAVE = 0x0703
REG_CONFIG=0x00; REG_SHUNT=0x01; REG_BUS=0x02; REG_POWER=0x03; REG_CURRENT=0x04; REG_CAL=0x05
# Waveshare UPS Module 3S vendor calibration for 0.01-ohm shunt.
CAL_VALUE=26868
CONFIG_VALUE=0x0EEF  # 16V, gain /2 (80mV), 12-bit x32, continuous shunt+bus
CURRENT_LSB_MA=0.1524
POWER_LSB_W=0.003048


def _signed16(v:int)->int:
    return v-65536 if v & 0x8000 else v


class _INA219:
    def __init__(self, bus=1, addr=0x41):
        self.path=f"/dev/i2c-{bus}"; self.addr=addr; self.fd=None
    def __enter__(self):
        self.fd=os.open(self.path, os.O_RDWR)
        fcntl.ioctl(self.fd, I2C_SLAVE, self.addr)
        return self
    def __exit__(self,*_):
        if self.fd is not None: os.close(self.fd); self.fd=None
    def write16(self,reg:int,val:int):
        os.write(self.fd, bytes((reg,(val>>8)&0xff,val&0xff)))
    def read16(self,reg:int)->int:
        os.write(self.fd, bytes((reg,)))
        data=os.read(self.fd,2)
        if len(data)!=2: raise OSError('short I2C read')
        return (data[0]<<8)|data[1]
    def sample(self)->dict[str,float]:
        # Reassert vendor calibration; INA219 current/power registers depend on it.
        self.write16(REG_CAL,CAL_VALUE); self.write16(REG_CONFIG,CONFIG_VALUE)
        bus=(self.read16(REG_BUS)>>3)*0.004
        shunt_mv=_signed16(self.read16(REG_SHUNT))*0.01
        current_ma=_signed16(self.read16(REG_CURRENT))*CURRENT_LSB_MA
        power_w=self.read16(REG_POWER)*POWER_LSB_W
        supply=bus+(shunt_mv/1000.0)
        return {"bus_v":bus,"shunt_mv":shunt_mv,"current_ma":current_ma,"power_w":power_w,"supply_v":supply}


class PowerCollector(Collector):
    """Waveshare UPS Module 3S telemetry.

    Activates only when /dev/i2c-1 exists and an INA219 responds at 0x41/0x40.
    A failed probe is represented as unavailable state, not a collector exception.
    """
    name="power"; interval=2.0; priority=75; stale_after=8.0
    def __init__(self): self.addr=None; self._last_ext=None

    def _probe(self):
        if not Path('/dev/i2c-1').exists(): return None
        for addr in (0x41,0x40,0x42):
            try:
                with _INA219(1,addr) as dev:
                    v=dev.sample()
                    if 5.0 <= v['supply_v'] <= 16.5: return addr,v
            except Exception:
                continue
        return None

    def collect(self)->dict[str,Any]:
        vals:dict[str,Any]={"power.source":"unknown","power.ups.model":"Waveshare UPS Module 3S","power.ups.i2c_bus_present":Path('/dev/i2c-1').exists(),"power.ups.probe_addresses":["0x41","0x40","0x42"]}
        try:
            if self.addr is None:
                got=self._probe()
                if not got:
                    vals.update({"power.ups.state":"not_detected","power.telemetry.available":False,"power.ups.hint":"INA219 did not respond on 0x41/0x40/0x42; verify SDA/SCL/GND telemetry wiring"})
                    return vals
                self.addr,sample=got
            else:
                with _INA219(1,self.addr) as dev: sample=dev.sample()
        except Exception as exc:
            self.addr=None
            vals.update({"power.ups.state":"read_error","power.telemetry.available":False,"power.ups.last_error":repr(exc)})
            return vals
        v=sample['supply_v']; cur=sample['current_ma']
        # Vendor percentage is a simple 3S 9.0V -> 12.6V interpolation.
        pct=max(0.0,min(100.0,(v-9.0)/3.6*100.0))
        charging=cur>50.0
        discharging=cur<-200.0
        external=not discharging
        vals.update({
            "power.ups.state":"available","power.telemetry.available":True,
            "power.ups.i2c_address":hex(self.addr),
            "power.battery.voltage_v":round(v,3),"power.battery.percent_estimate":round(pct,1),
            "power.current_ma":round(cur,1),"power.power_w":round(sample['power_w'],3),
            "power.shunt_mv":round(sample['shunt_mv'],3),
            "power.charging":charging,"power.discharging":discharging,
            "power.external_present":external,
            "power.external_confidence":"high" if discharging or charging else "medium",
            "power.source":"external" if external else "battery",
        })
        return vals
