import io
import json
import sqlite3
import tarfile
import zipfile
from pathlib import Path

from PIL import Image

from beastcore.backup import BackupManager
from beastcore.db import Store
from beastcore.document_extractors import extract_epub
from beastcore.events import EventBus
from beastcore.operator_tools import OperatorToolRegistry
from beastcore.search import UniversalSearch
from beastcore.state import StateRegistry
from beastcore.actions import ActionBroker
from beastui.display import DisplayTransform


def test_display_transform_800x480_letterboxes_and_reverse_maps():
    t=DisplayTransform((480,320),(800,480),mode='fit',resample='nearest')
    assert (t.viewport.x,t.viewport.y,t.viewport.width,t.viewport.height)==(40,0,720,480)
    im=Image.new('RGB',(480,320),'white')
    out=t.to_physical(im)
    assert out.size==(800,480)
    assert t.to_logical_point(40,0)==(0,0)
    assert t.to_logical_point(400,240)==(240,160)
    assert t.to_logical_point(10,240) is None
    meta=t.metadata()
    assert meta['compatibility_scaling'] is True
    assert meta['responsive_layout'] is False


def test_epub_extractor_indexes_searchable_text_without_dependency(tmp_path):
    p=tmp_path/'manual.epub'
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('OEBPS/ch1.xhtml','<html><body><h1>GPS Recovery</h1><p>Restart gpsd after checking USB power.</p></body></html>')
    text,kind=extract_epub(p,10000)
    assert kind=='epub_zip'
    assert 'GPS Recovery' in text and 'gpsd' in text


def test_field_library_fts5_search_when_supported(tmp_path):
    store=Store(str(tmp_path/'beast.db'))
    store.upsert_library_document({'id':'1','path':'/tmp/gps.md','filename':'gps.md','title':'GPS Recovery','extension':'.md','size_bytes':10,'mtime':1,'indexed_at':1,'text':'reset gpsd serial receiver troubleshooting','status':'present'})
    store.upsert_library_document({'id':'2','path':'/tmp/fan.md','filename':'fan.md','title':'Cooling','extension':'.md','size_bytes':10,'mtime':2,'indexed_at':2,'text':'PWM fan thermals temperature cooling','status':'present'})
    rows=store.search_library('gpsd troubleshooting',10,0)
    assert rows and rows[0]['id']=='1'
    if store.library_fts:
        assert '[' in rows[0]['snippet'] or 'gpsd' in rows[0]['snippet'].lower()
    store.close()


def _tiny_db(path: Path):
    con=sqlite3.connect(path);con.execute('create table hello(x text)');con.execute("insert into hello values('beast')");con.commit();con.close()


def test_backup_inspect_verifies_manifest_hash_and_sqlite(tmp_path):
    db=tmp_path/'beast.db';_tiny_db(db)
    mgr=BackupManager(str(db),root=str(tmp_path/'backups'),clock=lambda:1700000000.0)
    mgr.sources=[]
    created=mgr.create()
    out=mgr.inspect(Path(created['path']).name)
    assert out['ok'] is True and out['ready_to_stage'] is True
    assert out['db_valid'] is True
    assert out['sha256']==created['sha256']
    assert out['restore_applied'] is False


def test_backup_inspect_rejects_links_or_escape_members(tmp_path):
    db=tmp_path/'beast.db';_tiny_db(db)
    root=tmp_path/'backups';root.mkdir()
    p=root/'beastagotchi-backup-evil.tar.gz'
    with tarfile.open(p,'w:gz') as tf:
        data=json.dumps({'format':1,'db_snapshot':False}).encode()
        info=tarfile.TarInfo('beastagotchi-backup/manifest.json');info.size=len(data);tf.addfile(info,io.BytesIO(data))
        bad=tarfile.TarInfo('../escape');bad.size=1;tf.addfile(bad,io.BytesIO(b'x'))
    mgr=BackupManager(str(db),root=str(root))
    out=mgr.inspect(p.name)
    assert out['ok'] is False and out['ready_to_stage'] is False
    assert any('outside' in x or 'unsafe' in x for x in out['blockers'])


def test_operator_registry_has_powerful_structured_tools_but_no_generic_shell(tmp_path):
    store=Store(str(tmp_path/'beast.db'));st=StateRegistry();events=EventBus();search=UniversalSearch(st,store);broker=ActionBroker(st,store,events)
    tools=OperatorToolRegistry(st,store,search,broker)
    observer=tools.catalog('observer');operator=tools.catalog('operator')
    names={x['name'] for x in operator['items']}
    assert {'service.restart','plugin.toggle','backup.create','support.bundle','container.control'} <= names
    assert operator['generic_shell'] is False
    assert next(x for x in observer['items'] if x['name']=='service.restart')['available_at_level'] is False
    assert next(x for x in operator['items'] if x['name']=='service.restart')['available_at_level'] is True
    store.close()
