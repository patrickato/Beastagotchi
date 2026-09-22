from pathlib import Path

from beastcore.dock import DockEngine
from beastcore.state import StateRegistry
from beastcore.collectors.capabilities import CapabilityCollector
from beastcore.collectors.power import PowerCollector
from beastui.engine import BeastUI


def test_dock_requires_power_ethernet_and_enrolled_home(tmp_path):
    s=StateRegistry(); profile=tmp_path/'home.json'; profile.write_text('{"gateway":"192.168.1.1","gateway_mac":"aa:bb:cc:dd:ee:ff"}')
    eng=DockEngine(s,str(profile))
    s.update_many('x',{'power.external_present':True,'network.ethernet.carrier':True,'network.default.gateway':'192.168.1.1','network.default.gateway_mac':'aa:bb:cc:dd:ee:ff'},priority=80)
    out=eng.tick(); assert out['dock.docked'] is True and out['dock.state']=='docked'
    s.update_many('x',{'power.external_present':False},priority=80); assert eng.tick()['dock.docked'] is False


def test_awus_profile(monkeypatch):
    import beastcore.collectors.capabilities as mod
    monkeypatch.setattr(mod,'run',lambda cmd,timeout=3:(0,'Bus 001 Device 004: ID 0e8d:7612 MediaTek Inc. Wireless Adapter\n',''))
    out=CapabilityCollector().collect();dev=out['capabilities.usb_devices'][0]
    assert dev['name']=='ALFA AWUS036ACM'; assert dev['chipset']=='MediaTek MT7612U'; assert out['capabilities.awus036acm.present'] is True


def test_power_absent_is_not_error(monkeypatch):
    import beastcore.collectors.power as mod
    monkeypatch.setattr(mod.Path,'exists',lambda self:False)
    out=PowerCollector().collect(); assert out['power.ups.state']=='not_detected'; assert out['power.telemetry.available'] is False


def test_all_visual_alpha_themes_render(tmp_path):
    root=Path(__file__).resolve().parents[1]/'beastui'
    state={'health.core.state':'healthy','wifi.ap_count':9,'wifi.client_count':5,'wifi.aps':[{'hostname':'LAB','channel':6,'rssi':-42,'encryption':'WPA2'}], 'radio.primary.channel':6,'radio.primary.band':'2.4GHz','system.temp.cpu_c':56.0,'system.cpu.total':18.0,'system.memory.used_pct':7.0,'context.mode.effective':'wardrive','context.visual.tags':['wardrive','wind','goggles'],'gps.fix':True,'gps.satellites_used':8,'gps.satellites_visible':13,'context.motion.speed_mph':22.0,'pwnagotchi.bridge.state':'available','pwnagotchi.mood':'excited','pwnagotchi.handshakes':2,'platform.services':[],'dock.state':'field','dock.docked':False,'capabilities.count':4}
    for tid in BeastUI.THEMES:
        ui=BeastUI(root=str(root),output=str(tmp_path/f'{tid}.png'),theme_id=tid);ui.state=state;im=ui.render();assert im.size==(480,320);assert ui.theme.id==tid

def test_help_registry_and_touch_zone_overlay_render(tmp_path):
    root=Path(__file__).resolve().parents[1]/'beastui'
    ui=BeastUI(root=str(root),output=str(tmp_path/'help.png'),theme_id='classic')
    ui.state={'health.core.state':'healthy','radio.primary.channel':6,'system.cpu.total':10.0}
    ui.help_overlay=True
    assert ui.render().size==(480,320)
    ui.help_overlay=False; ui.touch_zones_overlay=True
    assert ui.render().size==(480,320)
