from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

from beastcore.db import Store
from beastcore.field_library import FieldLibraryEngine
from beastcore.operator_policy import OperatorPolicy
from beastcore.overview import OverviewEngine
from beastcore.search import UniversalSearch
from beastcore.state import StateRegistry
from beastcore.topology import ServiceTopologyEngine
from beastui.apps import AppRegistry
from beastui.engine import BeastUI

ROOT=Path(__file__).resolve().parents[1]
UIROOT=ROOT/'beastui'


def _state(**items):
    s=StateRegistry();s.update_many('test',items,priority=100);return s


def test_overview_is_derived_from_real_state_and_surfaces_attention():
    st=_state(**{
        'health.core.state':'healthy','pwnagotchi.service.state':'active','bettercap.state':'active',
        'pwnagotchi.bridge.state':'available','gps.state':'connected_no_fix','storage.root.readonly':False,
        'storage.root.used_pct':42.0,'system.temp.cpu_c':44.0,'system.cpu.total':12.0,'governor.mode':'FULL',
        'wifi.ap_count':18,'radio.primary.channel':6,'captures.indexed_files':3,'pwnagotchi.handshakes':1,
        'progression.level':8,'progression.stage':'Scout','expedition.id':'exp1',
    })
    out=OverviewEngine(st).tick()
    assert out['overview.state']=='healthy'
    assert out['overview.attention_count']==0
    assert {x['id'] for x in out['overview.cards']}=={'radio','beast','field','captures','system','storage'}
    st.update_many('test',{'pwnagotchi.service.state':'activating'},priority=100)
    out=OverviewEngine(st).tick()
    assert out['overview.state']=='critical'
    assert out['overview.attention'][0]['code']=='pwnagotchi'


def test_topology_describes_dependencies_not_fake_network_geometry():
    st=_state(**{'radio.primary.name':'wlan0mon','radio.primary.state':'up','bettercap.state':'active','pwnagotchi.service.state':'active','pwnagotchi.bridge.state':'available','health.core.state':'healthy','gps.state':'connected_no_fix','platform.services':[]})
    out=ServiceTopologyEngine(st).tick()
    ids={x['id'] for x in out['topology.nodes']}
    assert {'radio','bettercap','pwnagotchi','bridge','core','ui','studio','gps'} <= ids
    assert {'from':'pwnagotchi','to':'bridge','kind':'callbacks'} in out['topology.edges']


def test_field_library_indexes_text_and_catalogues_pdf(tmp_path):
    root=tmp_path/'library';root.mkdir()
    (root/'display_notes.md').write_text('ILI9486 field repair notes and Beast display recovery')
    (root/'manual.pdf').write_bytes(b'%PDF-1.4 placeholder')
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry()
    out=FieldLibraryEngine(st,store,roots=[str(root)],clock=lambda:1234.0).tick()
    assert out['library.document_count']==2
    assert out['library.text_indexed_count']==1
    rows=store.search_library('ILI9486',10,0)
    assert len(rows)==1 and rows[0]['filename']=='display_notes.md'
    jobs=store.recent_jobs(5);assert jobs and jobs[0]['status']=='complete'
    store.close()


def test_universal_search_crosses_library_network_capture_event_and_telemetry(tmp_path):
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry();st.update_many('test',{'system.temp.cpu_c':51.2},priority=100)
    store.upsert_library_document({'id':'d1','path':'/x/gps.txt','filename':'gps.txt','title':'GPS Manual','extension':'.txt','size_bytes':3,'mtime':1,'indexed_at':1,'text':'gps antenna'})
    class E:pass
    e=E();e.id='e1';e.ts=1;e.type='gps.fix';e.source='gps';e.severity='info';e.data={'message':'GPS lock'};store.add_event(e)
    out=UniversalSearch(st,store).search('gps',10)
    assert 'library' in out['groups'] and 'events' in out['groups']
    out2=UniversalSearch(st,store).search('temp',10)
    assert out2['groups']['telemetry'][0]['data']['key']=='system.temp.cpu_c'
    store.close()


def test_operator_policy_is_powerful_but_action_broker_mediated():
    p=OperatorPolicy().snapshot('administrator')
    assert 'shell.controlled' in p['operator.policy.capabilities']
    assert p['operator.policy.direct_root'] is False
    assert p['operator.policy.mutations_via_action_broker'] is True


def test_v016_apps_and_overview_render(tmp_path):
    ids={a.id for a in AppRegistry().all()}
    assert {'overview','operations','topology','tasks','field_library'} <= ids
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    assert 'overview' in ui.pages.IDS
    ui.page=ui.pages.IDS.index('overview')
    ui.state={
        'overview.state':'healthy','overview.attention_count':0,'overview.attention':[],
        'overview.cards':[{'id':'system','title':'SYSTEM','value':'42C','detail':'CPU 9% / FULL','status':'ok'}],
    }
    im=ui._compose(ui.page)
    assert im.size==(480,320)


def test_display_collector_discovers_framebuffer_and_drm(tmp_path):
    from beastcore.collectors.display import DisplayCollector
    g=tmp_path/'graphics';d=tmp_path/'drm';(g/'fb1').mkdir(parents=True);(d/'card0-HDMI-A-1').mkdir(parents=True)
    (g/'fb1'/'virtual_size').write_text('800,480\n');(g/'fb1'/'bits_per_pixel').write_text('32\n');(g/'fb1'/'name').write_text('vc4drmfb\n')
    (d/'card0-HDMI-A-1'/'status').write_text('connected\n');(d/'card0-HDMI-A-1'/'modes').write_text('1920x1080\n1280x720\n')
    out=DisplayCollector(str(g),str(d)).collect()
    assert out['display.framebuffers'][0]['width']==800
    assert out['display.framebuffers'][0]['bpp']==32
    assert out['display.connected_outputs']==1
    assert out['display.outputs'][0]['preferred_mode']=='1920x1080'


def test_service_broker_only_restarts_allowlisted_units():
    from beastcore.service_broker import ServiceBroker
    class R:
        returncode=0;stdout='ok';stderr=''
    calls=[]
    b=ServiceBroker(runner=lambda cmd:(calls.append(cmd) or R()))
    assert b.plan_restart('pwnagotchi.service')['allowed']
    assert not b.plan_restart('ssh.service')['allowed']
    out=b.restart('gpsd.service');assert out['ok'] and calls[-1]==['systemctl','restart','gpsd.service']


def test_plugin_integration_marks_enabled_display_conflicts():
    from beastcore.plugin_integration import PluginIntegrationEngine
    st=StateRegistry();st.update_many('test',{'platform.plugins':[{'name':'theme_manager','enabled':True,'configured':True}]},priority=100)
    out=PluginIntegrationEngine(st).tick()
    assert out['plugins.display_conflict_count']==1
    assert out['plugins.display_conflicts_enabled']==['theme_manager']
    assert out['plugins.catalog'][0]['legacy_display_owner'] is True


def test_operations_and_topology_special_views_render(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.state={'overview.state':'healthy','overview.attention_count':0,'health.core.state':'healthy','health.core.collector_count':12,'platform.services':[], 'library.document_count':2,'library.text_indexed_count':1,
              'topology.nodes':[{'id':'core','label':'Beast Core','kind':'service','state':'healthy'}], 'topology.edges':[], 'topology.failure_count':0}
    ui.aux={'jobs':{'items':[]}}
    ui.platform_overlay='operations';assert ui._compose(ui.page).size==(480,320)
    ui.platform_overlay='topology';assert ui._compose(ui.page).size==(480,320)


def test_studio_exposes_universal_search_surface():
    from beaststudio.server import HTML
    assert 'UNIVERSAL BEAST SEARCH' in HTML
    assert 'SEARCH BEAST' in HTML


def test_incident_engine_opens_and_resolves_durable_black_box(tmp_path):
    from beastcore.events import EventBus
    from beastcore.incidents import IncidentEngine
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry();ev=EventBus()
    st.update_many('test',{'health.core.uptime_sec':30,'pwnagotchi.service.state':'failed','bettercap.state':'active','storage.root.readonly':False},priority=100)
    eng=IncidentEngine(st,store,ev,clock=lambda:100.0)
    patch,rows=eng.tick();assert patch['incidents.open_count']==1 and rows[0][0]=='incident.opened'
    first=store.recent_incidents(5)[0];assert first['kind']=='service.pwnagotchi' and first['status']=='open'
    assert first['snapshot']['state']['pwnagotchi.service.state']=='failed'
    st.update_many('test',{'pwnagotchi.service.state':'active'},priority=100)
    eng.clock=lambda:120.0
    patch,rows=eng.tick();assert patch['incidents.open_count']==0 and rows[0][0]=='incident.resolved'
    assert store.recent_incidents(5)[0]['status']=='resolved'
    store.close()


def test_black_box_app_is_present():
    assert AppRegistry().get('incidents') is not None

def test_backup_manager_creates_bounded_verified_archive(tmp_path):
    from beastcore.backup import BackupManager
    db=tmp_path/'beast.db';store=Store(str(db));store.close()
    root=tmp_path/'backups'
    mgr=BackupManager(str(db),root=str(root),keep=2,clock=lambda:1700000000.0)
    mgr.sources=[]
    out=mgr.create()
    assert out['ok'] and Path(out['path']).is_file()
    assert len(out['sha256'])==64
    import tarfile,json
    with tarfile.open(out['path'],'r:gz') as tf:
        manifest=json.load(tf.extractfile('beastagotchi-backup/manifest.json'))
    assert manifest['format']==1 and manifest['db_snapshot'] is True


def test_backup_collector_validates_archive_manifest(tmp_path):
    from beastcore.backup import BackupManager
    from beastcore.collectors.backups import BackupCollector
    db=tmp_path/'beast.db';store=Store(str(db));store.close()
    mgr=BackupManager(str(db),root=str(tmp_path/'backups'),clock=lambda:1700000000.0);mgr.sources=[];mgr.create()
    out=BackupCollector(str(tmp_path/'backups')).collect()
    assert out['backups.count']==1
    assert out['backups.items'][0]['valid'] is True


def test_ai_collector_is_capability_driven(tmp_path,monkeypatch):
    from beastcore.collectors.ai import AICapabilityCollector
    import beastcore.collectors.ai as mod
    root=tmp_path/'models';root.mkdir();(root/'tiny.gguf').write_bytes(b'x'*10)
    monkeypatch.setattr(mod.shutil,'which',lambda name:'/usr/bin/llama-cli' if name=='llama-cli' else None)
    c=AICapabilityCollector();c.MODEL_ROOTS=(root,)
    out=c.collect()
    assert out['ai.local.available'] is True
    assert out['ai.llama.available'] is True
    assert out['ai.models.count']==1


def test_optional_apps_do_not_clutter_without_capability(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.state={};ui.apps=ui._build_app_registry();ids={a.id for a in ui.apps.all()}
    assert 'containers' not in ids and 'ai_operator' not in ids
    ui.state={'containers.runtime.available':True,'ai.local.available':True};ui.apps=ui._build_app_registry();ids={a.id for a in ui.apps.all()}
    assert {'containers','ai_operator'} <= ids


def test_backup_center_and_studio_backup_controls_present():
    from beaststudio.server import HTML
    assert AppRegistry().get('backups') is not None
    assert 'CREATE RECOVERY BACKUP' in HTML
    assert '/api/backup-create' in HTML

def test_desktop_capability_collector_never_starts_desktop(monkeypatch):
    from beastcore.collectors.desktop import DesktopCapabilityCollector
    import beastcore.collectors.desktop as mod
    seen=[]
    def which(name):
        seen.append(name)
        return '/usr/bin/startx' if name=='startx' else None
    monkeypatch.setattr(mod.shutil,'which',which)
    out=DesktopCapabilityCollector().collect()
    assert out['desktop.runtime.available'] is True
    assert out['desktop.session.state']=='not_started_by_beast'
    assert 'startx' in seen


def test_command_center_appears_only_with_external_display(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic')
    ui.state={'display.external_connected':False};ui.apps=ui._build_app_registry();assert ui.apps.get('command_center') is None
    ui.state={'display.external_connected':True};ui.apps=ui._build_app_registry();assert ui.apps.get('command_center') is not None


def test_default_decks_include_platform_operations():
    from beastui.customization import DEFAULT_CONTEXT_DECKS
    system=next(x for x in DEFAULT_CONTEXT_DECKS if x['id']=='system')
    assert {'overview','operations','topology','incidents','backups'} <= set(system['apps'])

def test_incident_snapshot_links_relevant_field_library_runbook(tmp_path):
    from beastcore.events import EventBus
    from beastcore.incidents import IncidentEngine
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry();ev=EventBus()
    store.upsert_library_document({'id':'gpsdoc','path':'/library/gps.md','filename':'gps.md','title':'GPS Repair Runbook','extension':'.md','size_bytes':10,'mtime':1,'indexed_at':1,'text':'gps service troubleshooting and recovery'})
    st.update_many('test',{'health.core.uptime_sec':30,'pwnagotchi.service.state':'active','bettercap.state':'active','storage.root.readonly':False,'system.temp.cpu_c':83.0},priority=100)
    eng=IncidentEngine(st,store,ev,clock=lambda:10.0);eng.tick()
    # Thermal has no matching doc, then create a GPS-ish incident by direct snapshot helper
    snap=eng._snapshot('service.gps','GPS service troubleshooting')
    assert any(x['id']=='gpsdoc' for x in snap['related_documents'])
    store.close()


def test_core_health_reports_starting_not_degraded_during_normal_boot(tmp_path):
    from beastcore.core import BeastCore
    core=BeastCore(db_path=str(tmp_path/'beast.db'),port=0)
    try:
        out=core._health_summary(now=100.0,uptime=1.0)
        assert out['health.core.state']=='starting'
        assert out['health.core.ready'] is False
        assert out['health.core.degraded_collectors']==[]
        assert set(out['health.core.starting_collectors'])=={c.name for c in core.collectors}
    finally:
        core.store.close()


def test_core_health_becomes_degraded_if_collectors_never_start_after_grace(tmp_path):
    from beastcore.core import BeastCore
    core=BeastCore(db_path=str(tmp_path/'beast.db'),port=0)
    try:
        core.state.update_many('test',{'pwnagotchi.service.state':'active','bettercap.state':'active'},priority=100)
        out=core._health_summary(now=100.0,uptime=25.0)
        assert out['health.core.state']=='degraded'
        assert out['health.core.ready'] is True
        assert len(out['health.core.degraded_collectors'])==len(core.collectors)
        assert out['health.core.critical_failures']==[]
    finally:
        core.store.close()


def test_pwnagotchi_inventory_can_refresh_plugin_catalog_immediately():
    from beastcore.plugin_integration import PluginIntegrationEngine
    st=StateRegistry()
    st.update_many('pwnagotchi',{'platform.plugins':[{'name':'beast_bridge','enabled':True,'configured':True},{'name':'theme_manager','enabled':False,'configured':True}]},priority=30)
    out=PluginIntegrationEngine(st).tick()
    assert out['plugins.catalog_count']==2
    assert out['plugins.enabled_count']==1
    rows={r['name']:r for r in out['plugins.catalog']}
    assert rows['beast_bridge']['protected'] is True
    assert rows['theme_manager']['legacy_display_owner'] is True


def test_display_transform_fits_480x320_into_800x480_without_distortion():
    from beastui.display import DisplayTransform
    from PIL import Image
    t=DisplayTransform((480,320),(800,480),mode='fit')
    assert t.viewport.x==40 and t.viewport.y==0
    assert t.viewport.width==720 and t.viewport.height==480
    im=Image.new('RGB',(480,320),'white')
    out=t.to_physical(im)
    assert out.size==(800,480)
    assert out.getpixel((0,0))==(0,0,0)
    assert out.getpixel((400,240))==(255,255,255)
    assert t.to_logical_point(20,240) is None
    cx=t.to_logical_point(400,240)
    assert cx is not None and abs(cx[0]-240)<=1 and abs(cx[1]-160)<=1


def test_display_transform_reverse_touch_mapping_and_identity():
    from beastui.display import DisplayTransform
    t=DisplayTransform((480,320),(640,480),mode='fit')
    p=t.to_physical_point(240,160)
    q=t.to_logical_point(*p)
    assert q is not None and abs(q[0]-240)<=1 and abs(q[1]-160)<=1
    native=DisplayTransform((480,320),(480,320))
    assert native.identity is True
    assert native.metadata()['compatibility_scaling'] is False


def test_ui_can_emit_800x480_compatibility_frame(tmp_path):
    ui=BeastUI(root=UIROOT,output=str(tmp_path/'x.png'),theme_id='classic',physical_size=(800,480))
    ui.state={'system.temp.cpu_c':42.0,'system.cpu.total':5.0,'governor.mode':'FULL'}
    out=ui.render()
    assert out.size==(800,480)
    assert (tmp_path/'x.png').is_file()


def test_field_library_extracts_epub_without_extra_dependency(tmp_path):
    import zipfile
    root=tmp_path/'library';root.mkdir();epub=root/'guide.epub'
    with zipfile.ZipFile(epub,'w') as z:
        z.writestr('OEBPS/ch1.xhtml','<html><body><h1>Field Guide</h1><p>GPS antenna recovery steps</p></body></html>')
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry()
    out=FieldLibraryEngine(st,store,roots=[str(root)],clock=lambda:1234.0).tick()
    rows=store.search_library('antenna recovery',10,0)
    assert len(rows)==1 and rows[0]['filename']=='guide.epub'
    assert out['library.extractor_counts']['epub_zip']==1
    assert out['library.extractors']['epub'] is True
    store.close()


def test_field_library_pdf_extractor_is_capability_driven(tmp_path):
    from beastcore.document_extractors import capabilities
    caps=capabilities()
    assert caps['text'] is True and caps['epub'] is True
    assert isinstance(caps['pdf_pymupdf'],bool) and isinstance(caps['pdf_pypdf'],bool)
    assert caps['zim'] is False


def test_operator_tool_registry_exposes_structured_power_without_generic_shell(tmp_path):
    from beastcore.actions import ActionBroker
    from beastcore.events import EventBus
    from beastcore.operator_tools import OperatorToolRegistry
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry();events=EventBus();search=UniversalSearch(st,store);broker=ActionBroker(st,store,events)
    tools=OperatorToolRegistry(st,store,search,broker)
    cat=tools.catalog('operator')
    assert cat['generic_shell'] is False
    names={x['name'] for x in cat['items']}
    assert {'state.get','search.query','service.restart','backup.create','plugin.toggle'} <= names
    assert all(x['name']!='shell.exec' for x in cat['items'])
    store.close()


def test_operator_tools_enforce_privilege_levels_and_delegate_plans(tmp_path):
    from beastcore.actions import ActionBroker
    from beastcore.events import EventBus
    from beastcore.operator_tools import OperatorToolRegistry
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry();events=EventBus();search=UniversalSearch(st,store);broker=ActionBroker(st,store,events)
    tools=OperatorToolRegistry(st,store,search,broker)
    denied=tools.invoke('service.restart',{'unit':'gpsd.service'},level='observer')
    assert denied['ok'] is False and 'operator' in denied['error']
    plan=tools.invoke('action.plan',{'action':'service.restart','payload':{'unit':'gpsd.service'}},level='observer')
    assert plan['ok'] is True and plan['data']['allowed'] is True
    bad=tools.invoke('action.plan',{'action':'service.restart','payload':{'unit':'ssh.service'}},level='observer')
    assert bad['ok'] is True and bad['data']['allowed'] is False
    store.close()


def test_container_broker_refuses_unenrolled_container_and_allows_managed():
    from beastcore.container_broker import ContainerBroker
    import json
    class R:
        def __init__(self,rc=0,out='',err=''):self.returncode=rc;self.stdout=out;self.stderr=err
    calls=[]
    managed=[{'Config':{'Labels':{'io.beastagotchi.managed':'true'}}}]
    un=[{'Config':{'Labels':{}}}]
    current={'obj':managed}
    def run(cmd,**kw):
        calls.append(cmd)
        if cmd[1]=='inspect':return R(out=json.dumps(current['obj']))
        return R(out='ok')
    b=ContainerBroker(runner=run,which=lambda n:'/usr/bin/docker' if n=='docker' else None)
    assert b.plan('demo','restart')['allowed'] is True
    assert b.perform('demo','restart')['ok'] is True
    current['obj']=un
    plan=b.plan('other','stop')
    assert plan['allowed'] is False and 'not enrolled' in plan['blockers'][0]


def test_container_collector_marks_beast_managed_labels():
    from beastcore.collectors.containers import ContainerCollector
    assert ContainerCollector._is_beast_managed({'io.beastagotchi.managed':'true'}) is True
    assert ContainerCollector._is_beast_managed({'random':'true'}) is False


def test_library_file_manager_safely_imports_supported_docs(tmp_path):
    from beaststudio.library_files import LibraryFileManager,LibraryFileError
    m=LibraryFileManager(str(tmp_path/'imports'),max_bytes=1000,readable_roots=(str(tmp_path),))
    out=m.save('../../GPS Manual.md',b'GPS recovery notes')
    assert out['ok'] and Path(out['path']).parent==tmp_path/'imports'
    assert '..' not in Path(out['path']).name
    data,ctype,name=m.read(out['path'])
    assert data==b'GPS recovery notes' and name.endswith('.md')
    import pytest
    with pytest.raises(LibraryFileError):m.save('script.py',b'print(1)')
    with pytest.raises(LibraryFileError):m.save('huge.txt',b'x'*1025)


def test_studio_includes_field_library_import_and_open_ui():
    from beaststudio.server import HTML
    assert 'FIELD LIBRARY IMPORT' in HTML
    assert '/api/library-upload' in HTML
    assert '/api/library-file' in HTML
    assert 'OPEN LOCAL DOCUMENT' in HTML


def test_bluetooth_collector_parses_adapter_without_starting_discovery(monkeypatch):
    from beastcore.collectors.bluetooth import BluetoothCollector
    import beastcore.collectors.bluetooth as mod
    monkeypatch.setattr(mod.shutil,'which',lambda n:'/usr/bin/bluetoothctl')
    monkeypatch.setattr(mod,'run',lambda *a,**k:(0,'Controller AA:BB:CC:DD:EE:FF beast [default]\n\tName: beast\n\tPowered: yes\n\tDiscoverable: no\n\tPairable: yes\n\tDiscovering: no\n',''))
    out=BluetoothCollector().collect()
    assert out['bluetooth.adapter.present'] is True
    assert out['bluetooth.adapter.powered'] is True
    assert out['bluetooth.adapter.discovering'] is False


def test_system_pi_clock_parsers():
    from beastcore.collectors.system import SystemCollector
    assert SystemCollector._parse_clock_hz('frequency(48)=1500000000')==1500.0
    assert SystemCollector._parse_mem_mb('gpu=76M')==76


def test_support_bundle_omits_network_and_gps_identifiers(tmp_path):
    from beastcore.support_bundle import SupportBundleManager
    import tarfile,json
    st=StateRegistry();st.update_many('test',{
        'system.beast_version':'0.test','system.temp.cpu_c':42.0,'health.core.state':'healthy',
        'wifi.aps':[{'ssid':'SECRET','bssid':'aa:bb:cc:dd:ee:ff'}],
        'gps.latitude':12.34,'gps.longitude':56.78,'network.default.gateway':'192.168.1.1',
        'network.route.available':True,'network.internet.state':'unknown',
    },priority=100)
    store=Store(str(tmp_path/'beast.db'))
    mgr=SupportBundleManager(st,store,root=str(tmp_path/'support'),clock=lambda:1700000000.0)
    out=mgr.create();assert out['ok']
    with tarfile.open(out['path'],'r:gz') as tf:
        state=json.load(tf.extractfile('beast-support/state.json'))
        manifest=json.load(tf.extractfile('beast-support/manifest.json'))
    assert state['system.temp.cpu_c']==42.0
    assert state['network.route.available'] is True
    assert 'wifi.aps' not in state and 'gps.latitude' not in state and 'network.default.gateway' not in state
    assert manifest['privacy']=='sanitized' and manifest['raw_logs_included'] is False
    store.close()


def test_support_bundle_is_an_operator_tool(tmp_path):
    from beastcore.actions import ActionBroker
    from beastcore.events import EventBus
    from beastcore.operator_tools import OperatorToolRegistry
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry();events=EventBus();search=UniversalSearch(st,store);broker=ActionBroker(st,store,events)
    tools=OperatorToolRegistry(st,store,search,broker)
    names={x['name'] for x in tools.catalog('operator')['items']}
    assert 'support.bundle' in names
    store.close()


def test_studio_schema_declares_reference_and_compatibility_outputs(tmp_path):
    from beaststudio.server import StudioState
    root=Path(__file__).resolve().parents[1]/'beastui'
    st=StudioState(str(root),str(tmp_path/'prefs.json'),str(tmp_path/'token'))
    st.api.telemetry=lambda: []
    schema=st.schema()
    outputs={x['id']:x for x in schema['preview_outputs']}
    assert schema['version']=='0.18.0'
    assert outputs['480x320']['reference'] is True
    assert outputs['640x480']['reference'] is False
    assert outputs['800x480']['reference'] is False
    assert (outputs['800x480']['width'],outputs['800x480']['height'])==(800,480)


def test_studio_html_labels_nonreference_output_as_compatibility_only():
    from beaststudio.server import HTML
    assert 'COMPATIBILITY · 800 × 480' not in HTML  # populated from schema, not hard-coded as a supported layout
    assert 'Compatibility scaling only — this is not yet a responsive larger-screen layout.' in HTML
    assert 'layout editing uses' not in HTML.lower() or 'reference' in HTML.lower()


def test_studio_ops_exposes_sanitized_support_bundle_control():
    from beaststudio.server import HTML
    assert 'CREATE SANITIZED SUPPORT BUNDLE' in HTML
    assert '/api/support-plan' in HTML
    assert '/api/support-create' in HTML
    assert 'raw config and raw logs are excluded' in HTML


def test_studio_800x480_preview_uses_display_transform_not_responsive_claim(tmp_path):
    from beaststudio.server import StudioState
    from PIL import Image
    import io
    class FakeAPI:
        def telemetry(self): return []
        def live(self,*_a,**_k): return {'state':{},'events':[]}
        def history_batch(self,*_a,**_k): return {'histories':{},'channel_history':[],'telemetry':[],'expedition':None}
    root=Path(__file__).resolve().parents[1]/'beastui'
    st=StudioState(str(root),str(tmp_path/'prefs.json'),str(tmp_path/'token'))
    st.api=FakeAPI()
    draft=st.preferences();draft['preview_output']='800x480'
    im=Image.open(io.BytesIO(st.preview(draft)))
    assert im.size==(800,480)
