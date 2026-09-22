import json
import time
from pathlib import Path

from beastcore.events import EventBus
from beastcore.semantic import SemanticEngine
from beastcore.state import StateRegistry
from beastui.engine import BeastUI


def test_event_bus_can_filter_transient():
    bus=EventBus()
    bus.publish("state.changed","system",{"keys":["x"]})
    bus.publish("gps.lock_acquired","gps",{})
    got=bus.recent(10,include_transient=False)
    assert [x["type"] for x in got]==["gps.lock_acquired"]


def test_semantic_transitions_and_ap_session_count():
    s=StateRegistry(); eng=SemanticEngine(s)
    s.update_many("x",{"context.mode.effective":"pwn","gps.fix":False,"health.core.state":"healthy","system.temp.cpu_c":60.0,"wifi.aps":[]},priority=50)
    eng.tick()
    s.update_many("x",{"context.mode.effective":"walk","gps.fix":True,"health.core.state":"healthy","system.temp.cpu_c":76.0,"wifi.aps":[{"mac":"aa:bb:cc:dd:ee:ff","hostname":"lab","channel":6,"rssi":-40}]},priority=50)
    types=[e[0] for e in eng.tick()]
    assert "context.mode_changed" in types
    # v0.5 deliberately debounces GPS lock events; raw fix should not fire immediately.
    assert "gps.lock_acquired" not in types
    eng._gps_candidate_since=time.monotonic()-4.0
    types += [e[0] for e in eng.tick()]
    assert "gps.lock_acquired" in types
    assert "system.thermal_band" in types
    assert "wifi.ap_discovered" in types
    assert s.get("wifi.encounters.session_unique")==1


def test_ui_renders_native_pages(tmp_path):
    root=Path(__file__).resolve().parents[1]/"beastui"
    ui=BeastUI(root=str(root), output=str(tmp_path/"frame.png"))
    ui.state={
        "health.core.state":"healthy","wifi.ap_count":2,"wifi.client_count":1,
        "wifi.aps":[{"hostname":"LAB","mac":"aa:bb:cc:dd:ee:ff","channel":6,"rssi":-42,"encryption":"WPA2","clients":[]}],
        "radio.primary.channel":6,"radio.primary.band":"2.4GHz","system.temp.cpu_c":55.0,
        "system.cpu.total":12.0,"system.memory.used_pct":7.0,"context.mode.effective":"pwn",
        "gps.fix":False,"gps.satellites_used":0,"gps.satellites_visible":0,
        "pwnagotchi.bridge.state":"available","pwnagotchi.mood":"awake","pwnagotchi.handshakes":0,
        "platform.services":[],
    }
    for i,_ in enumerate(ui.pages.IDS):
        ui.page=i; im=ui.render(); assert im.size==(480,320)
