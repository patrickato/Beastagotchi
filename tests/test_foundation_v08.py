
import json
import tempfile
import time
from pathlib import Path

from beastcore.db import Store
from beastcore.events import Event
from beastcore.progression import ProgressionEngine, level_for_xp, xp_threshold, stage_for_level, aura_for_session_unique
from beastcore.state import StateRegistry
from beastui.engine import BeastUI
from beastui.reactions import ReactionGovernor


def test_progression_curve_is_finite_and_monotonic():
    assert xp_threshold(1) == 0
    assert xp_threshold(100) < 100000
    assert xp_threshold(99) < xp_threshold(100)
    assert level_for_xp(xp_threshold(100)) == 100
    assert stage_for_level(100) == 'Monstergotchi'
    assert aura_for_session_unique(50) == 'electric'


def test_progression_awards_lifetime_ap_and_achievement(tmp_path):
    state = StateRegistry()
    state.update_many('semantic', {'wifi.encounters.session_unique': 1}, priority=85)
    eng = ProgressionEngine(state, str(tmp_path/'profile.json'))
    ev = Event('1', time.time(), 'wifi.ap_discovered', 'bettercap', 'info', {
        'lifetime_new_count': 1,
        'aps': [{'bssid':'aa:bb:cc:dd:ee:ff','vendor':'Acme'}],
    })
    rows = eng.on_event(ev)
    types = [r[0] for r in rows]
    assert 'progression.xp_awarded' in types
    assert 'progression.vendor_discovered' in types
    assert 'progression.achievement_unlocked' in types
    assert state.get('progression.level') >= 1
    assert state.get('progression.achievements.count') >= 1
    # Replaying without lifetime-new AP and same vendor must not refarm those awards.
    xp = state.get('progression.xp')
    ev2 = Event('2', time.time(), 'wifi.ap_discovered', 'bettercap', 'info', {
        'lifetime_new_count': 0,
        'aps': [{'bssid':'aa:bb:cc:dd:ee:ff','vendor':'Acme'}],
    })
    eng.on_event(ev2)
    assert state.get('progression.xp') == xp


def test_wifi_encounter_catalog_tracks_lifetime_uniques(tmp_path):
    store = Store(str(tmp_path/'beast.db'))
    first = store.record_wifi_encounters([
        {'bssid':'aa:bb:cc:dd:ee:01','ssid':'A','vendor':'Vendor1','channel':1,'rssi':-60},
        {'bssid':'aa:bb:cc:dd:ee:02','ssid':'B','vendor':'Vendor2','channel':6,'rssi':-70},
    ], 1.0)
    assert first['new_count'] == 2
    second = store.record_wifi_encounters([
        {'bssid':'aa:bb:cc:dd:ee:01','ssid':'A','vendor':'Vendor1','channel':11,'rssi':-40},
    ], 2.0)
    assert second['new_count'] == 0
    summary = store.encounter_summary(10)
    assert summary['total'] == 2
    assert summary['vendor_count'] == 2
    a = next(x for x in summary['recent'] if x['bssid']=='aa:bb:cc:dd:ee:01')
    assert a['strongest_rssi'] == -40.0
    store.close()


def test_reaction_governor_prioritizes_thermal_over_level():
    now=time.time()
    gov=ReactionGovernor()
    picked=gov.select([
        {'id':'a','ts':now,'type':'progression.level_up','data':{'to':5}},
        {'id':'b','ts':now,'type':'system.thermal_band','data':{'to':'hot'}},
    ], now)
    assert picked['event']['type']=='system.thermal_band'


def test_spectrum_renderer_cycle_and_beast_page_render(tmp_path):
    root=Path(__file__).resolve().parents[1]/'beastui'
    # isolate static output preferences
    pref=Path('/tmp/beast-ui-test-prefs.json')
    try: pref.unlink()
    except FileNotFoundError: pass
    ui=BeastUI(root=str(root), output=str(tmp_path/'frame.png'), theme_id='classic')
    ui.state={
        'health.core.state':'healthy','radio.primary.channel':6,'radio.primary.band':'2.4GHz',
        'wifi.ap_count':4,'wifi.client_count':1,
        'wifi.aps':[{'hostname':'A','channel':1,'rssi':-45,'encryption':'WPA2'},
                    {'hostname':'B','channel':6,'rssi':-50,'encryption':'WPA2'},
                    {'hostname':'C','channel':11,'rssi':-55,'encryption':'WPA2'}],
        'system.temp.cpu_c':59.0,'system.cpu.total':12.0,'system.memory.used_pct':8.0,
        'context.mode.effective':'pwn','pwnagotchi.mood':'awake','pwnagotchi.handshakes':1,
        'progression.level':8,'progression.max_level':100,'progression.stage':'Cub',
        'progression.xp':500,'progression.xp_next_level':100,'progression.level_progress_pct':75.0,
        'progression.aura':'spark','progression.vendors.count':3,'progression.achievements.count':2,
        'progression.achievement.last':'First Signal','wifi.encounters.lifetime_unique':22,
        'wifi.encounters.lifetime_vendors':3,
    }
    ui.page=3
    seen=[]
    for _ in range(4):
        seen.append(ui.renderer_for('spectrum'))
        ui.render()
        ui.cycle_renderer('spectrum')
    assert seen == ['bars','line','heatmap','radar']
    ui.page=6
    assert ui.render().size == (480,320)
