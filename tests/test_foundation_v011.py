from pathlib import Path

from beastcore.db import Store
from beastcore.expeditions import ExpeditionEngine
from beastcore.governor import ResourceGovernor
from beastcore.state import StateRegistry
from beastui.engine import BeastUI
from beastui.rare_overlay import render_rare_overlay
from beastui.theme import load_theme
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / 'beastui'


class Clock:
    def __init__(self, value=1_800_000_000.0):
        self.value = float(value)
    def __call__(self):
        return self.value
    def advance(self, sec):
        self.value += float(sec)


def _ui_state():
    return {
        'health.core.state':'healthy','radio.primary.channel':6,'radio.primary.band':'2.4GHz',
        'wifi.ap_count':4,'wifi.client_count':1,'wifi.handshake_ap_count':2,
        'wifi.aps':[{'bssid':f'00:11:22:33:44:{i:02x}','hostname':f'AP{i}','channel':ch,'rssi':-40-i*4,'encryption':'WPA2'} for i,ch in enumerate([1,6,11,44])],
        'system.temp.cpu_c':65.0,'system.cpu.total':25.0,'system.memory.used_pct':12.0,
        'context.mode.effective':'pwn','pwnagotchi.mood':'awake','pwnagotchi.handshakes':1,
        'progression.level':9,'progression.max_level':100,'progression.xp':900,
        'progression.xp_next_level':300,'progression.level_progress_pct':40.0,'progression.stage':'Cub','progression.aura':'spark',
        'wifi.encounters.lifetime_unique':30,'captures.total':3,'capabilities.count':7,
        'expedition.active':True,'expedition.id':'exp-test','expedition.duration_sec':3720,
        'expedition.distance_m':3218.688,'expedition.route_points':88,'expedition.ap_unique':42,
        'expedition.captures_delta':3,'expedition.xp_delta':120,'expedition.max_temp_c':73.2,
        'expedition.max_cpu_pct':82.0,'expedition.min_battery_pct':61.0,
        'governor.mode':'FULL','governor.budget_pct':100,'governor.ui.fps_cap':18.0,
    }


def test_resource_governor_escalates_immediately_and_recovers_with_hysteresis():
    state=StateRegistry();mono=Clock(100.0);g=ResourceGovernor(state,recovery_hold_sec=10,mono=mono)
    state.update_many('test',{'system.temp.cpu_c':65,'system.cpu.total':20,'system.memory.used_pct':10},priority=100)
    assert g.tick()['governor.mode']=='FULL'
    state.update_many('test',{'system.temp.cpu_c':79},priority=100)
    assert g.tick()['governor.mode']=='REDUCED'
    state.update_many('test',{'system.temp.cpu_c':64},priority=100)
    assert g.tick()['governor.mode']=='REDUCED'
    mono.advance(11)
    assert g.tick()['governor.mode']=='FULL'


def test_resource_governor_distinguishes_current_and_historical_throttle():
    state=StateRegistry();g=ResourceGovernor(state,recovery_hold_sec=0)
    # 0x50000 means historical conditions only; do not pin the live UI in survival.
    state.update_many('test',{'system.temp.cpu_c':65,'system.cpu.total':30,'system.memory.used_pct':20,'system.throttle.flags':'0x50000'},priority=100)
    p=g.tick();assert p['governor.mode']=='FULL';assert not p['governor.throttle_current'];assert p['governor.throttle_history_seen']
    # Low bits indicate a condition that is happening now.
    state.update_many('test',{'system.throttle.flags':'0x1'},priority=100)
    p=g.tick();assert p['governor.mode']=='SURVIVAL';assert p['governor.ui.fps_cap']<=3;assert not p['governor.ui.foreground_allowed']


def test_resource_governor_thermal_bands_shed_before_pi_throttle():
    state=StateRegistry();g=ResourceGovernor(state,recovery_hold_sec=0)
    state.update_many('test',{'system.cpu.total':20,'system.memory.used_pct':10,'system.throttle.flags':'0x0'},priority=100)
    for temp, expected in [(69.9,'FULL'),(70.0,'GUARDED'),(76.0,'REDUCED'),(80.0,'SURVIVAL')]:
        state.update_many('test',{'system.temp.cpu_c':temp},priority=100)
        assert g.tick()['governor.mode']==expected


def test_ui_honors_governor_fps_cap_and_transient_load_shedding(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'x.png'),theme_id='synthwave');ui.state=_ui_state()
    ui.state['governor.ui.fps_cap']=3;ui.state['governor.mode']='SURVIVAL'
    assert ui.adaptive_fps()<=3
    opts=ui.render_options_for_theme('synthwave')
    assert opts['grid_density']=='off' and opts['stars']=='off'
    # Saved theme preference is untouched by the runtime governor.
    assert ui.options_for_theme('synthwave')['grid_density']=='normal'


def test_expedition_records_route_aps_stats_and_recovers(tmp_path):
    db=Store(str(tmp_path/'beast.db'));state=StateRegistry();clock=Clock();mono=Clock(100.0)
    state.update_many('test',{
        'captures.total':2,'progression.xp':1000,'gps.fix':True,'gps.latitude':42.1,'gps.longitude':-84.1,
        'gps.accuracy_m':4.0,'gps.speed_mps':5.0,'system.temp.cpu_c':68.0,'system.cpu.total':20.0,
        'governor.mode':'FULL','wifi.aps':[{'bssid':'aa:bb:cc:dd:ee:01','ssid':'one','channel':6,'rssi':-45}],
    },priority=100)
    e=ExpeditionEngine(state,db,clock=clock,mono=mono);patch,events=e.tick();eid=patch['expedition.id']
    assert patch['expedition.route_points']==1 and patch['expedition.ap_unique']==1
    assert any(x[0]=='expedition.started' for x in events)
    clock.advance(5);mono.advance(5)
    state.update_many('test',{
        'gps.latitude':42.1002,'gps.longitude':-84.1002,'captures.total':4,'progression.xp':1125,
        'system.temp.cpu_c':74.0,'system.cpu.total':81.0,
        'wifi.aps':[{'bssid':'aa:bb:cc:dd:ee:02','ssid':'two','channel':11,'rssi':-52}],
    },priority=100)
    patch,_=e.tick()
    assert patch['expedition.distance_m']>0
    assert patch['expedition.route_points']==2 and patch['expedition.ap_unique']==2
    assert patch['expedition.captures_delta']==2 and patch['expedition.xp_delta']==125
    # Simulate Beast Core process restart without a clean finish.
    clock.advance(10);mono.advance(10)
    e2=ExpeditionEngine(state,db,clock=clock,mono=mono);p2,ev2=e2.tick()
    assert p2['expedition.id']==eid and p2['expedition.recovered'] is True
    assert any(x[0]=='expedition.recovered' for x in ev2)
    detail=db.expedition_detail(eid);assert detail and len(detail['points'])>=2 and detail['aps']==2
    finished=e2.finish();assert finished and db.get_expedition(eid)['status']=='complete'
    db.close()


def test_expedition_clean_checkpoint_is_recovered_not_ended(tmp_path):
    db=Store(str(tmp_path/'beast.db'));state=StateRegistry();clock=Clock();mono=Clock(100.0)
    state.update_many('test',{'captures.total':1,'progression.xp':50,'gps.fix':False},priority=100)
    e=ExpeditionEngine(state,db,clock=clock,mono=mono);p,_=e.tick();eid=p['expedition.id']
    saved=e.checkpoint();assert saved and saved[0]==eid
    assert db.get_expedition(eid)['status']=='active'
    clock.advance(5);mono.advance(5)
    e2=ExpeditionEngine(state,db,clock=clock,mono=mono);p2,events=e2.tick()
    assert p2['expedition.id']==eid and p2['expedition.recovered'] is True
    assert any(x[0]=='expedition.recovered' for x in events)
    e2.finish('test_end');assert db.get_expedition(eid)['status']=='complete'
    db.close()


def test_new_structural_themes_render_and_have_runtime_options(tmp_path):
    state=_ui_state()
    variants={
        'synthwave':({'grid_density':'off','sun':'off','horizon_glow':'off','stars':'off'},{'grid_density':'dense','sun':'full','horizon_glow':'hot','stars':'dense'}),
        'amber_tactical':({'grid_density':'off','scope':'off','sweep':'off','brackets':'off'},{'grid_density':'dense','scope':'on','sweep':'fast','brackets':'on'}),
        'ghost_minimal':({'ambient':'off','ghosts':'off','edge_trace':'off'},{'ambient':'soft','ghosts':'normal','edge_trace':'on'}),
    }
    for tid,(aopt,bopt) in variants.items():
        ui=BeastUI(root=ROOT,output=str(tmp_path/f'{tid}.png'),theme_id=tid);ui.state=dict(state);ui.phase=2.0
        assert ui._theme_option_rows(tid)
        ui.theme_options[tid]=aopt;a=ui._compose(0)
        ui.theme_options[tid]=bopt;b=ui._compose(0)
        assert a.size==(480,320) and a.tobytes()!=b.tobytes()


def test_expedition_page_renders(tmp_path):
    ui=BeastUI(root=ROOT,output=str(tmp_path/'exp.png'),theme_id='ghost_minimal');ui.state=_ui_state()
    ui.page=ui.pages.IDS.index('expedition')
    im=ui.render();assert im.size==(480,320)


def test_rare_cinematic_yields_to_governor_render_budget(tmp_path):
    theme=load_theme(ROOT/'themes'/'synthwave.json');fonts=BeastUI(root=ROOT,output=str(tmp_path/'font-probe.png'),theme_id='synthwave').fonts
    base=Image.new('RGB',(480,320),(0,0,0))
    state={'rare.moment.active':True,'rare.moment.id':'r1','rare.moment.sigil':'gate',
           'rare.moment.rarity':'mythic','rare.moment.presentation':'cinematic',
           'governor.rare.cinematic_allowed':False}
    reduced=render_rare_overlay(base,state,2.0,theme,fonts)
    state['rare.moment.presentation']='fade'
    explicit=render_rare_overlay(base,state,2.0,theme,fonts)
    assert reduced.tobytes()==explicit.tobytes()


def test_all_structural_themes_render_every_main_page(tmp_path):
    themes=['classic','matrix','starcore','blackice','hunter','minimal','synthwave','amber_tactical','ghost_minimal']
    state=_ui_state()
    for tid in themes:
        ui=BeastUI(root=ROOT,output=str(tmp_path/f'{tid}-smoke.png'),theme_id=tid);ui.state=dict(state)
        for page_id in ui.pages.IDS:
            ui.page=ui.pages.IDS.index(page_id)
            frame=ui._compose(0)
            assert frame.size==(480,320), (tid,page_id)
