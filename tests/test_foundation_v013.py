from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from beastcore.channel_history import ChannelActivityEngine
from beastcore.db import Store
from beastcore.plugin_integration import PluginIntegrationEngine
from beastcore.state import StateRegistry
from beaststudio.server import StudioState
from beastui.apps import AppRegistry
from beastui.engine import BeastUI
from beastui.framebuffer import FrameBuffer
from beastui.pages import Pages

ROOT=Path(__file__).resolve().parents[1]
UIROOT=ROOT/'beastui'


def test_dirty_framebuffer_writes_only_changed_rows(tmp_path):
    fb_path=tmp_path/'fb.bin';fb_path.write_bytes(b'\0'*(480*320*2))
    fb=FrameBuffer(str(fb_path),480,320,full_write_threshold=.72)
    a=Image.new('RGB',(480,320),(0,0,0));fb.write(a)
    assert fb.last_full_write and fb.last_bytes_written==480*320*2
    b=a.copy()
    for x in range(30,90):b.putpixel((x,40),(255,255,255))
    fb.write(b)
    assert not fb.last_full_write
    assert fb.last_changed_rows==1
    assert fb.last_bytes_written<=480*2*3
    assert fb.telemetry()['saved_bytes']>300_000
    fb.write(b)
    assert fb.last_bytes_written==0 and fb.last_changed_rows==0
    fb.close()


def test_channel_history_is_real_per_channel_observation():
    state=StateRegistry();state.update_many('test',{'wifi.aps':[
        {'bssid':'a','channel':1,'rssi':-40,'hostname':'A','clients':[1,2]},
        {'bssid':'b','channel':6,'rssi':-65,'hostname':'B','encryption':'OPEN'},
    ]},priority=100)
    clock=[100.0];eng=ChannelActivityEngine(state,max_snapshots=8,clock=lambda:clock[0])
    p=eng.tick();rows=p['wifi.channel_activity']
    assert [r['channel'] for r in rows]==[1,6]
    assert rows[0]['client_count']==2 and rows[1]['open_count']==1
    clock[0]+=2;state.update_many('test',{'wifi.aps':[{'bssid':'c','channel':11,'rssi':-50,'hostname':'C'}]},priority=100);eng.tick()
    hist=eng.recent(8);channels,matrix=Pages._channel_history_matrix(hist)
    assert channels==[1,6,11]
    assert matrix[0]==[1.0,1.0,0.0] and matrix[1]==[0.0,0.0,1.0]


def test_app_registry_is_independent_from_home_deck_and_launcher_opens(tmp_path):
    reg=AppRegistry();assert len(reg.all())>len(Pages.IDS)
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.state={'health.core.state':'healthy'}
    ui.on_input('swipe',{'axis':'y','dy':-80,'delta':1})
    assert ui.app_launcher
    ui._open_app('telemetry');assert ui.telemetry_overlay and not ui.app_launcher
    ui.telemetry_overlay=False;ui._open_app('plugins');assert ui.plugins_overlay


def test_map_uses_recorded_route_not_decorative_motion(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.state={'health.core.state':'healthy','gps.fix':True,'gps.satellites_used':5,'gps.satellites_visible':8,'expedition.distance_m':100,'expedition.ap_unique':2,'expedition.route_points':2}
    ui.page=ui.pages.IDS.index('map')
    ui.aux={'expedition':{'points':[{'latitude':42.0,'longitude':-84.0},{'latitude':42.001,'longitude':-84.002}]}}
    ui.phase=1.0;a=ui._compose(ui.page)
    ui.phase=9.0;b=ui._compose(ui.page)
    # Classic background can animate; route helper itself must consume exact points.
    assert Pages._route_points(ui.aux['expedition'])[1][:2]==(42.001,-84.002)
    assert a.size==b.size==(480,320)


def test_plugin_integration_distinguishes_enabled_from_integrated():
    state=StateRegistry();state.update_many('test',{'platform.plugins':[
        {'name':'gps','enabled':True,'configured':True},
        {'name':'mystery','enabled':True,'configured':True},
        {'name':'theme_manager','enabled':False,'configured':True},
    ]},priority=100)
    p=PluginIntegrationEngine(state).tick();rows={r['name']:r for r in p['plugins.catalog']}
    assert rows['gps']['integration']=='canonical'
    assert rows['mystery']['integration']=='config_only'
    assert rows['theme_manager']['display_policy']=='legacy_isolated'
    assert p['plugins.enabled_count']==2


def test_records_enrich_encounters_and_capture_vault(tmp_path):
    db=Store(str(tmp_path/'beast.db'))
    ap={'bssid':'aa:bb:cc:dd:ee:ff','ssid':'TestNet','vendor':'Vendor','channel':6,'rssi':-60,'encryption':'WPA2','clients':[1]}
    db.record_wifi_encounters([ap],100.0)
    ap2=dict(ap,channel=11,rssi=-42,clients=[1,2,3])
    assert db.update_wifi_observations([ap2],120.0,{'latitude':42.1,'longitude':-84.2,'accuracy_m':3.5})==1
    row=db.encounter_detail(ap['bssid']);assert row
    assert row['strongest_rssi']==-42 and row['channels']==[6,11] and row['max_clients']==3
    assert row['last_latitude']==42.1 and row['encryption']=='WPA2'
    capdir=tmp_path/'caps';capdir.mkdir();(capdir/'TestNet_001.pcapng').write_bytes(b'12345');(capdir/'note.txt').write_text('ignore')
    summary=db.index_capture_directory(capdir,130.0)
    assert summary['count']==1 and summary['bytes']==5 and summary['recent'][0]['extension']=='.pcapng'
    db.close()


def test_studio_uses_real_compositor_and_atomic_preferences(tmp_path):
    prefs=tmp_path/'preferences.json';token=tmp_path/'studio.token'
    st=StudioState(str(UIROOT),str(prefs),str(token))
    schema=st.schema();assert len(schema['themes'])>=9 and len(schema['pages'])==len(Pages.IDS)
    draft=st.preferences();draft['theme']='synthwave';draft['page']='system';draft['theme_options']={'synthwave':{'grid_density':'dense','sun':'full'}}
    png=st.preview(draft);assert png.startswith(b'\x89PNG') and len(png)>1000
    result=st.apply(draft);assert result['ok']
    saved=json.loads(prefs.read_text());assert saved['theme']=='synthwave'
    draft['theme']='ghost_minimal';st.apply(draft)
    assert list((prefs.parent/'backups').glob('preferences-*.json'))


def test_bridge_runtime_directory_is_preserved_in_release_unit():
    text=(ROOT/'systemd'/'beast-core.service').read_text()
    assert 'RuntimeDirectoryPreserve=yes' in text

from beastcore.collectors.performance import PerformanceCollector


def _write_fake_proc(root: Path, pid: int, cmd: str, ticks: int, rss_pages: int = 100):
    d=root/str(pid);d.mkdir(parents=True,exist_ok=True)
    (d/'cmdline').write_bytes(cmd.replace(' ', '\0').encode()+b'\0')
    # fields after comm: state(3), ppid...; utime is field14 => tail index11.
    tail=['S']+['0']*10+[str(ticks),'0']+['0']*8
    (d/'stat').write_text(f'{pid} (proc) '+' '.join(tail)+'\n')
    (d/'statm').write_text(f'1000 {rss_pages} 0 0 0 0 0\n')


def test_performance_collector_attributes_real_process_cost(tmp_path):
    proc=tmp_path/'proc';proc.mkdir();clock=[10.0]
    _write_fake_proc(proc,101,'/opt/.pwn/bin/python3 -m beastui',100)
    _write_fake_proc(proc,102,'/usr/bin/python3 -m beastcore',200)
    _write_fake_proc(proc,103,'/usr/bin/bettercap -caplet foo',300)
    runtime=tmp_path/'runtime.json';runtime.write_text(json.dumps({'avg_render_ms':9.5,'avg_compose_ms':6.2,'avg_fb_write_ms':1.2,'target_fps':12,'lifetime_fps':11.8,'theme':'classic','page':'system','framebuffer':{'changed_rows':10,'bytes_written':9600,'frame_bytes':307200,'full_write':False,'saved_bytes':297600,'totals':{'frames':9,'bytes_written':500000,'full_writes':1,'saved_bytes':2264800}}}))
    c=PerformanceCollector(str(proc),str(runtime),clock=lambda:clock[0]);first=c.collect();assert first['performance.process_count']==3
    clock[0]=12.0;_write_fake_proc(proc,101,'/opt/.pwn/bin/python3 -m beastui',120);_write_fake_proc(proc,102,'/usr/bin/python3 -m beastcore',240);_write_fake_proc(proc,103,'/usr/bin/bettercap -caplet foo',320)
    second=c.collect();rows={r['id']:r for r in second['performance.processes']}
    assert rows['beast_ui']['cpu_pct']>0 and rows['beast_core']['cpu_pct']>0 and rows['bettercap']['cpu_pct']>0
    assert second['performance.beast.cpu_pct']>second['performance.platform_services.cpu_pct']
    assert second['performance.fb.write_ratio_pct']==3.1
    assert second['performance.fb.total_frames']==9


def test_records_apps_and_performance_are_real_overlays(tmp_path):
    reg=AppRegistry();ids={a.id for a in reg.all()};assert {'beastdex','capture_vault','performance','beast_studio'}<=ids
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.state={'health.core.state':'healthy','records.encounters.total':1,'records.encounters.vendor_count':1,'records.encounters.recent':[{'bssid':'aa','ssid':'RealNet','vendor':'Vendor','channel':6,'strongest_rssi':-44,'last_seen':1,'observation_count':4,'channels':[6],'encryption':'WPA2'}],'captures.indexed_files':1,'captures.storage_bytes':5,'captures.recent':[{'filename':'RealNet.pcapng','extension':'.pcapng','size_bytes':5,'mtime':1,'network_hint':'RealNet','path':'/tmp/RealNet.pcapng'}],'performance.processes':[{'id':'beast_ui','label':'Beast UI','cpu_pct':12.0,'rss_mb':55.0}],'performance.beast.cpu_pct':12.0,'performance.platform_services.cpu_pct':8.0,'performance.ui.avg_render_ms':8.2,'performance.fb.write_ratio_pct':14.0,'system.hostname':'beast'}
    for app,flag in [('beastdex','beastdex_overlay'),('capture_vault','capture_vault_overlay'),('performance','performance_overlay'),('beast_studio','studio_overlay')]:
        ui._open_app(app);assert getattr(ui,flag);im=ui._compose(ui.page);assert im.size==(480,320);setattr(ui,flag,False)


def test_studio_live_apis_require_pairing_token():
    text=(ROOT/'beaststudio'/'server.py').read_text()
    assert "path.startswith('/api/') and not self._auth()" in text
    assert "'X-Beast-Studio-Token':TOKEN" in text
    assert "if path in {'/api/preview','/api/apply'} and not self._auth()" in text

from beastcore.actions import ActionBroker
from beastcore.events import EventBus
from beastcore.plugin_broker import CommandResult, PluginBroker, PluginBrokerError


def _write_plugin_config(path: Path, enabled: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('[main.plugins.demo]\nenabled = '+('true' if enabled else 'false')+'\n\n[main.plugins.beast_bridge]\nenabled = true\n')


def test_plugin_broker_is_transactional_and_uses_supported_cli(tmp_path):
    cfg=tmp_path/'config.toml';confd=tmp_path/'conf.d';custom=tmp_path/'plugins';snaps=tmp_path/'snapshots'
    confd.mkdir();custom.mkdir();(custom/'demo.py').write_text('# demo\n');(confd/'other.toml').write_text('[x]\ny=1\n');_write_plugin_config(cfg,False)
    commands=[];restarts=[]
    def runner(cmd):
        commands.append(cmd)
        _write_plugin_config(cfg,cmd[2]=='enable')
        return CommandResult(0,'ok','')
    def restart(unit):restarts.append(unit);return CommandResult(0)
    b=PluginBroker(config_path=str(cfg),conf_d=str(confd),custom_plugins=str(custom),snapshot_root=str(snaps),pwnagotchi_cli='/usr/bin/pwnagotchi',runner=runner,service_active=lambda u:False if u=='beast-ui.service' else True,service_restart=restart,sleep=lambda x:None,clock=lambda:100.0)
    plan=b.plan_toggle('demo',True);assert plan['allowed'] and plan['restart_required']
    result=b.toggle('demo',True);assert result['ok'] and b.current_enabled('demo') is True
    assert commands==[['/usr/bin/pwnagotchi','plugins','enable','demo']]
    assert restarts==['pwnagotchi.service'] and Path(result['snapshot'],'manifest.json').is_file()


def test_plugin_broker_rolls_back_failed_health_and_protects_bridge(tmp_path):
    cfg=tmp_path/'config.toml';confd=tmp_path/'conf.d';custom=tmp_path/'plugins';snaps=tmp_path/'snapshots'
    confd.mkdir();custom.mkdir();(custom/'demo.py').write_text('# demo\n');_write_plugin_config(cfg,False)
    active=[False,True]  # post-change health fails, rollback health succeeds
    def service_active(unit):
        if unit=='beast-ui.service':return False
        return active.pop(0) if active else True
    def runner(cmd):_write_plugin_config(cfg,True);return CommandResult(0)
    b=PluginBroker(config_path=str(cfg),conf_d=str(confd),custom_plugins=str(custom),snapshot_root=str(snaps),runner=runner,service_active=service_active,service_restart=lambda u:CommandResult(0),sleep=lambda x:None,clock=lambda:100.0)
    result=b.toggle('demo',True);assert not result['ok'] and result['rolled_back']
    assert b.current_enabled('demo') is False
    protected=b.plan_toggle('beast_bridge',False,beast_ui_active=False)
    assert not protected['allowed'] and protected['protected']


def test_plugin_broker_blocks_legacy_display_plugin_while_beast_owns_display(tmp_path):
    cfg=tmp_path/'config.toml';cfg.write_text('[main.plugins.theme_manager]\nenabled=false\n')
    b=PluginBroker(config_path=str(cfg),conf_d=str(tmp_path/'conf.d'),custom_plugins=str(tmp_path/'plugins'),snapshot_root=str(tmp_path/'s'),service_active=lambda u:True)
    plan=b.plan_toggle('theme_manager',True)
    assert plan['display_conflict'] and not plan['allowed']


def test_action_broker_audits_plugin_actions(tmp_path):
    db=Store(str(tmp_path/'beast.db'));state=StateRegistry();events=EventBus()
    class FakePlugins:
        def plan_toggle(self,name,enabled):return {'plugin':name,'requested_enabled':enabled,'allowed':True}
        def toggle(self,name,enabled,restart=True):return {'ok':True,'changed':True,'rolled_back':False,'final_enabled':enabled}
    a=ActionBroker(state,db,events,plugin_broker=FakePlugins())
    row=a.perform('plugin.toggle',{'name':'demo','enabled':True},actor='test')
    assert row['status']=='success' and state.get('actions.last.target')=='demo'
    hist=db.recent_actions(5);assert hist[0]['action']=='plugin.toggle' and hist[0]['request']['enabled'] is True
    assert any(x['type']=='action.completed' for x in events.recent(10))
    db.close()


def test_core_wires_privileged_action_broker_without_exposing_mutation_api():
    from beastcore.core import BeastCore
    core=BeastCore(db_path=':memory:',host='127.0.0.1',port=0)
    assert core.actions is not None
    core.store.close()
    api=(ROOT/'beastcore'/'api.py').read_text()
    assert 'parsed.path == "/actions"' in api
    assert 'method != "GET"' in api  # public Core API remains read-only


def test_plugin_catalog_marks_protected_and_legacy_display_owners():
    state=StateRegistry();state.update_many('test',{'platform.plugins':[{'name':'beast_bridge','enabled':True,'configured':True},{'name':'theme_manager','enabled':False,'configured':True}]},priority=100)
    rows={x['name']:x for x in PluginIntegrationEngine(state).tick()['plugins.catalog']}
    assert rows['beast_bridge']['protected'] and rows['beast_bridge']['toggle_capable']
    assert rows['theme_manager']['legacy_display_owner']


def test_custom_dashboard_binds_real_state_and_history(tmp_path):
    from beastui.customization import validate_dashboard_widgets
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'dash.png'),theme_id='classic')
    ui.state={'health.core.state':'healthy','system.cpu.total':42.0,'system.temp.cpu_c':63.2,'wifi.ap_count':17,'radio.primary.channel':149,'gps.satellites_used':8,'expedition.distance_m':1609.344}
    ui.histories={'wifi.ap_count':[2,4,8,17]}
    ui.dashboard_widgets=validate_dashboard_widgets([
        {'key':'system.cpu.total','label':'CPU','style':'radial','min':0,'max':100},
        {'key':'system.temp.cpu_c','label':'TEMP','style':'bar','min':25,'max':85},
        {'key':'wifi.ap_count','label':'APS','style':'microtrend'},
        {'key':'radio.primary.channel','label':'CHANNEL','style':'metric'},
        {'key':'gps.satellites_used','label':'GPS SAT','style':'bar','min':0,'max':16},
        {'key':'expedition.distance_m','label':'TRIP','style':'metric'},
    ])
    assert 'dashboard' in ui.pages.IDS
    ui.page=ui.pages.IDS.index('dashboard')
    im=ui._compose(ui.page);assert im.size==(480,320)
    # The dashboard must render from state/history, not mutate the source data.
    assert ui.state['wifi.ap_count']==17 and ui.histories['wifi.ap_count'][-1]==17


def test_studio_schema_and_apply_include_dashboard_bindings(tmp_path):
    prefs=tmp_path/'preferences.json';token=tmp_path/'studio.token'
    st=StudioState(str(UIROOT),str(prefs),str(token))
    schema=st.schema();assert schema['widget_styles']==['metric','bar','radial','microtrend']
    assert any(x['key']=='system.cpu.total' for x in schema['dashboard_keys'])
    draft=st.preferences();draft['page']='dashboard';draft['dashboard_widgets'][0]={'key':'system.temp.cpu_c','label':'HOT','style':'bar','min':20,'max':90}
    assert st.preview(draft).startswith(b'\x89PNG')
    assert st.apply(draft)['ok']
    saved=json.loads(prefs.read_text());assert saved['dashboard_widgets'][0]['key']=='system.temp.cpu_c'


def test_platform_apps_expand_beyond_main_deck_and_render(tmp_path):
    ids={a.id for a in AppRegistry().all()}
    assert {'timeline','notifications','diagnostics','services','hardware','storage'} <= ids
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'platform.png'),theme_id='classic')
    ui.state={
        'health.core.state':'healthy',
        'health.collector.system.state':'ok','health.collector.system.duration_ms':2.1,'health.collector.system.age_sec':.3,
        'platform.services':[{'unit':'pwnagotchi.service','active':'active','sub':'running','pid':123}],
        'platform.hardware':[{'raw':'Bus 001 Device 002: ID 1546:01a7 u-blox AG [u-blox 7]','id':'1546:01a7'}],
        'storage.root.used_pct':12.5,'storage.root.free_bytes':10_000_000,'storage.root.readonly':False,
        'storage.mounts':[{'source':'/dev/root','mount':'/','fstype':'ext4','options':['rw']}],
    }
    ui.events=[{'ts':1,'type':'gps.lock','source':'gps','severity':'info','data':{}},{'ts':2,'type':'collector.error','source':'radio','severity':'warning','data':{}}]
    for mode in ('timeline','notifications','diagnostics','services','hardware','storage'):
        ui.platform_overlay=mode;im=ui._compose(ui.page);assert im.size==(480,320);assert isinstance(ui._platform_rows(mode),list)


def test_local_action_server_is_unix_only_and_allowlisted(tmp_path):
    import asyncio
    from beastcore.action_server import LocalActionServer
    from beaststudio.action_client import BeastActionClient
    class Fake:
        def plan(self,action,payload):
            assert action=='plugin.toggle';return {'allowed':True,'plugin':payload['name'],'requested_enabled':payload['enabled']}
        def perform(self,action,payload,actor='local'):
            assert actor.startswith('local:');return {'status':'success','action':action,'target':payload['name']}
    sock=tmp_path/'action.sock';srv=LocalActionServer(Fake(),str(sock),group='group-that-does-not-exist')
    async def scenario():
        await srv.start()
        try:
            # Sync client calls run in worker threads so the asyncio server can serve them.
            c=BeastActionClient(str(sock),timeout=2)
            plan=await asyncio.to_thread(c.plan,'plugin.toggle',{'name':'demo','enabled':True})
            done=await asyncio.to_thread(c.perform,'plugin.toggle',{'name':'demo','enabled':True})
            assert plan['ok'] and plan['plan']['allowed'] and done['ok']
        finally:await srv.stop()
    asyncio.run(scenario())
    assert not sock.exists()


def test_studio_and_ui_join_privileged_action_group():
    studio=(ROOT/'ui_systemd'/'beast-studio.service').read_text()
    ui=(ROOT/'ui_systemd'/'beast-ui.service').read_text()
    installer=(ROOT/'install.sh').read_text()
    assert 'beastagotchi' in studio and 'beastagotchi' in ui
    assert 'groupadd --system beastagotchi' in installer


def test_static_ui_does_not_request_continuous_redraw(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'static.png'),theme_id='minimal')
    ui.state={'health.core.state':'healthy'}
    ui._compose(ui.page)  # builds the static background cache
    ui.transition=None;ui.button_flash=None
    assert ui._background_cadence(ui.render_options_for_theme(ui.theme.id))==0.0
    assert ui._dynamic_frame_due(ui._bg_cache_at+0.5) is False


def test_app_launcher_can_filter_categories_without_limiting_registry(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'apps.png'),theme_id='classic')
    cats=ui._app_categories();assert 'System' in cats and 'Studio' in cats and cats[0]=='ALL'
    ui.app_category_idx=cats.index('System');rows=ui._apps_current()
    assert rows and all(a.category=='System' for a in rows)
    assert len(ui.apps.all())>len(ui.pages.IDS)
