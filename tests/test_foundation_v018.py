import sqlite3
from pathlib import Path

from beastcore.backup import BackupManager
from beastcore.operator_sessions import OperatorSessionManager


def _db(p: Path):
    c=sqlite3.connect(p);c.execute('create table x(v text)');c.execute("insert into x values('beast')");c.commit();c.close()


def test_operator_session_expires_and_revokes(tmp_path):
    now=[1000.0]
    m=OperatorSessionManager(str(tmp_path/'session.json'),clock=lambda:now[0])
    assert m.current()['level']=='observer'
    row=m.authorize('operator',60,actor='owner')
    assert row['active'] is True and row['level']=='operator' and row['remaining_sec']==60
    now[0]=1061.0
    assert m.current()['active'] is False and m.current()['level']=='observer'
    m.authorize('maintainer',120)
    assert m.revoke()['level']=='observer'


def test_operator_admin_duration_is_bounded(tmp_path):
    m=OperatorSessionManager(str(tmp_path/'session.json'),clock=lambda:100.0)
    row=m.authorize('administrator',999999)
    assert row['remaining_sec']==3600


def test_backup_stage_isolated_and_no_live_restore(tmp_path):
    db=tmp_path/'beast.db';_db(db)
    mgr=BackupManager(str(db),root=str(tmp_path/'backups'),clock=lambda:1700000000.0);mgr.sources=[]
    made=mgr.create();out=mgr.stage(Path(made['path']).name,staging_root=str(tmp_path/'staging'))
    assert out['ok'] is True and out['staged'] is True and out['restore_applied'] is False
    assert Path(out['staging_path'],'beastagotchi-backup','manifest.json').is_file()
    assert any(x['path']=='beast.db' for x in out['inventory'])

from beastcore.personality import PersonalityEngine

class _S:
    def __init__(self,d):self.d=d
    def get(self,k,default=None):return self.d.get(k,default)


def test_personality_is_derived_from_real_state():
    now=[1000.0]
    s=_S({'wifi.ap_count':5,'health.core.state':'healthy','governor.mode':'FULL','system.temp.cpu_c':45,'gps.state':'locked','pwnagotchi.service.state':'active','bettercap.state':'active','expedition.active':True,'ambient.day_phase':'day','system.cpu.total':20,'progression.level':10})
    e=PersonalityEngine(s,clock=lambda:now[0]);first=e.tick();assert first['beast.mood'] in {'idle','hunting','curious'}
    s.d['wifi.ap_count']=7;now[0]+=2;row=e.tick();assert row['beast.mood']=='hunting' and row['beast.personality.source']=='derived_live'
    s.d['system.temp.cpu_c']=82;s.d['governor.mode']='SURVIVAL';assert e.tick()['beast.mood']=='overheated'
    s.d['health.core.state']='critical';assert e.tick()['beast.mood']=='fault'

from beastcore.missions import MissionPackEngine


def test_mission_packs_are_declarative_and_capability_aware(tmp_path):
    s=_S({'capabilities.present':['display','gps']})
    e=MissionPackEngine(s,str(tmp_path/'missions'))
    row=e.tick();assert row['missions.count']>=4
    trip=next(x for x in row['missions.items'] if x['id']=='road-trip')
    assert trip['requirements_met'] is True and 'apps' in trip and 'checklist' in trip
    assert all('shell' not in k for x in row['missions.items'] for k in x.keys())

from beastui.responsive import render_responsive_board
from beastui.theme import load_theme


def test_responsive_board_uses_native_800x480_canvas():
    theme=load_theme(Path('beastui/themes/classic.json'))
    widgets=[{'id':'cpu','key':'system.cpu.total','label':'CPU','style':'metric','x':0,'y':0,'w':6,'h':4,'z':0,'visible':True}]
    im=render_responsive_board((800,480),theme,{'system.cpu.total':42.0},widgets,'FIELD OPS')
    assert im.size==(800,480)
    # Right-side native canvas must contain composed pixels, proving this is not
    # a 720px compatibility viewport centered with 40px side bars.
    assert im.getbbox()==(0,0,800,480)

def test_operator_registry_uses_real_session_when_level_not_supplied(tmp_path):
    from beastcore.db import Store
    from beastcore.events import EventBus
    from beastcore.state import StateRegistry
    from beastcore.search import UniversalSearch
    from beastcore.actions import ActionBroker
    from beastcore.operator_tools import OperatorToolRegistry
    st=StateRegistry();store=Store(str(tmp_path/'b.db'));events=EventBus();broker=ActionBroker(st,store,events)
    broker.operator_sessions.path=tmp_path/'op.json'
    tools=OperatorToolRegistry(st,store,UniversalSearch(st,store),broker)
    assert tools.invoke('service.restart',{'unit':'gpsd.service'})['ok'] is False
    broker.operator_sessions.authorize('operator',120)
    # catalog now reflects persisted session without caller claiming a level
    assert tools.catalog()['active_level']=='operator'
    assert tools.invoke('operator.session')['data']['active'] is True
    store.close()

def test_restore_plan_is_dry_run_and_declares_rescue_requirements(tmp_path):
    db=tmp_path/'beast.db';_db(db)
    mgr=BackupManager(str(db),root=str(tmp_path/'backups'),clock=lambda:1700000000.0);mgr.sources=[]
    made=mgr.create();staged=mgr.stage(Path(made['path']).name,staging_root=str(tmp_path/'stage'))
    plan=mgr.restore_plan(staged['staging_path'])
    assert plan['ok'] is True and plan['dry_run'] is True and plan['restore_applied'] is False
    assert plan['requires_rescue_backup'] and plan['requires_service_quiesce'] and plan['rollback_required']
    assert any(x['kind']=='database' for x in plan['items'])

from beastui.face import FaceEngine


def test_face_engine_prefers_beast_personality_expression():
    f=FaceEngine()
    row=f.resolve({'beast.expression':'hunting','pwnagotchi.mood':'bored','health.core.state':'healthy'})
    assert row['mood']=='intense' and row['beast_expression']=='hunting'
    row=f.resolve({'beast.expression':'fault','health.core.state':'critical'})
    assert row['mood']=='broken'


def test_v018_packaged_installer_source_references_exist():
    from pathlib import Path
    import re

    root = Path(__file__).resolve().parents[1]
    for name in ("install.sh", "install_ui.sh", "install_bridge.sh", "validate_v018.sh"):
        script = root / name
        if not script.exists():
            continue
        text = script.read_text()
        refs = re.findall(r'\$SRC/([^"\s]+)', text)
        missing = [ref for ref in refs if not (root / ref).exists()]
        assert not missing, f"{name} has missing packaged source refs: {missing}"
