from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any


class BackupError(RuntimeError):pass


class BackupManager:
    """Create bounded Beast recovery archives without arbitrary path access."""

    def __init__(self,db_path: str,root: str='/var/lib/beastagotchi/backups',keep: int=5,clock=time.time) -> None:
        self.db_path=Path(db_path);self.root=Path(root);self.keep=max(1,min(int(keep),20));self.clock=clock
        self.sources=[Path('/etc/beastagotchi'),Path('/var/lib/beastagotchi/ui'),Path('/etc/pwnagotchi/config.toml'),Path('/etc/pwnagotchi/conf.d')]

    def plan(self)->dict[str,Any]:
        return {'allowed':True,'operation':'backup.create','destination':str(self.root),'retention':self.keep,'includes':['Beast database snapshot','Beast config/UI preferences','Pwnagotchi config/drop-ins'],'warnings':['Backup may contain private configuration; store it securely.']}

    @staticmethod
    def _sha256(path: Path)->str:
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        return h.hexdigest()

    def _sqlite_snapshot(self,dest: Path)->None:
        src=sqlite3.connect(self.db_path,timeout=10.0);dst=sqlite3.connect(dest)
        try:src.backup(dst)
        finally:dst.close();src.close()


    def _resolve_backup(self, name: str) -> Path:
        raw=Path(str(name or '').strip()).name
        if not raw or not raw.startswith('beastagotchi-backup-') or not raw.endswith('.tar.gz'):
            raise BackupError('invalid backup name')
        root=self.root.resolve()
        p=(root/raw).resolve()
        if p.parent!=root or not p.is_file():
            raise BackupError('backup not found')
        return p

    def inspect(self, name: str) -> dict[str,Any]:
        """Verify archive structure and SQLite snapshot without restoring it.

        This is deliberately read-only. Restore/apply remains a separate future
        transaction so a corrupt or hostile archive can never be unpacked over
        the live Beast merely because a user clicked Restore.
        """
        p=self._resolve_backup(name)
        blockers=[];warnings=[];manifest={};db_valid=None;member_count=0
        try:
            with tarfile.open(p,'r:gz') as tf:
                members=tf.getmembers();member_count=len(members)
                for m in members:
                    n=str(m.name or '')
                    parts=Path(n).parts
                    if not (n=='beastagotchi-backup' or n.startswith('beastagotchi-backup/')):
                        blockers.append(f'archive member outside Beast backup root: {n[:120]}');continue
                    if n.startswith('/') or '..' in parts:
                        blockers.append(f'unsafe archive path: {n[:120]}')
                    if m.issym() or m.islnk():
                        blockers.append(f'links are not allowed in recovery archives: {n[:120]}')
                try:
                    mf=tf.extractfile('beastagotchi-backup/manifest.json')
                    manifest=json.load(mf) if mf else {}
                except Exception as exc:
                    blockers.append(f'manifest unreadable: {type(exc).__name__}')
                    manifest={}
                if int(manifest.get('format') or 0)!=1:
                    blockers.append('unsupported or missing backup manifest format')
                db_member=None
                try:db_member=tf.getmember('beastagotchi-backup/beast.db')
                except KeyError:db_member=None
                if manifest.get('db_snapshot') and db_member is None:
                    blockers.append('manifest expects database snapshot but beast.db is missing')
                if db_member is not None:
                    try:
                        fh=tf.extractfile(db_member)
                        data=fh.read() if fh else b''
                        with tempfile.NamedTemporaryFile(prefix='beast-verify-',suffix='.db',delete=True) as tmp:
                            tmp.write(data);tmp.flush()
                            con=sqlite3.connect(tmp.name)
                            try:
                                row=con.execute('PRAGMA quick_check').fetchone()
                                db_valid=bool(row and str(row[0]).lower()=='ok')
                            finally:con.close()
                        if not db_valid:blockers.append('SQLite quick_check failed')
                    except Exception as exc:
                        db_valid=False;blockers.append(f'database verification failed: {type(exc).__name__}')
                elif manifest.get('db_snapshot') is False:
                    warnings.append('backup contains no Beast database snapshot')
        except (tarfile.TarError,OSError) as exc:
            blockers.append(f'archive unreadable: {type(exc).__name__}')
        st=p.stat()
        return {
            'ok':not blockers,'ready_to_stage':not blockers,'name':p.name,'path':str(p),
            'size_bytes':int(st.st_size),'mtime':float(st.st_mtime),'sha256':self._sha256(p),
            'member_count':member_count,'manifest':manifest,'db_valid':db_valid,
            'blockers':blockers,'warnings':warnings,'restore_applied':False,
        }

    def stage(self, name: str, staging_root: str='/var/lib/beastagotchi/restore-staging') -> dict[str,Any]:
        """Safely extract a verified recovery archive into an isolated staging area.

        Staging never mutates live configuration.  The returned inventory is the
        input to a later explicit restore transaction.
        """
        check=self.inspect(name)
        if not check.get('ok'):
            raise BackupError('backup is not safe to stage: '+ '; '.join(check.get('blockers') or []))
        p=self._resolve_backup(name);root=Path(staging_root)
        token=str(check['sha256'])[:16];dest=root/token
        root.mkdir(parents=True,exist_ok=True)
        if dest.exists():shutil.rmtree(dest)
        dest.mkdir(mode=0o700)
        with tarfile.open(p,'r:gz') as tf:
            for m in tf.getmembers():
                # inspect() already rejected links/escapes; enforce again here.
                n=str(m.name or '');parts=Path(n).parts
                if not (n=='beastagotchi-backup' or n.startswith('beastagotchi-backup/')) or n.startswith('/') or '..' in parts or m.issym() or m.islnk():
                    raise BackupError('unsafe member during staging')
            tf.extractall(dest,filter='data')
        base=dest/'beastagotchi-backup';manifest=json.loads((base/'manifest.json').read_text())
        inventory=[]
        for fp in sorted(base.rglob('*')):
            if fp.is_file():inventory.append({'path':str(fp.relative_to(base)),'size_bytes':fp.stat().st_size})
        return {'ok':True,'staged':True,'restore_applied':False,'name':p.name,'sha256':check['sha256'],'staging_path':str(dest),'manifest':manifest,'inventory':inventory}

    def restore_plan(self, staging_path: str) -> dict[str,Any]:
        """Build a dry-run restore diff from an isolated staging directory."""
        dest=Path(staging_path).resolve();base=dest/'beastagotchi-backup'
        if not base.is_dir() or not (base/'manifest.json').is_file():raise BackupError('invalid restore staging directory')
        manifest=json.loads((base/'manifest.json').read_text())
        items=[]
        db=base/'beast.db'
        if db.is_file():
            items.append({'kind':'database','source':'beast.db','target':str(self.db_path),'action':'replace' if self.db_path.exists() else 'create','size_bytes':db.stat().st_size})
        files=base/'files'
        if files.is_dir():
            for fp in sorted(files.rglob('*')):
                if not fp.is_file():continue
                rel=fp.relative_to(files);target=Path('/')/rel
                action='replace' if target.exists() else 'create'
                same=False
                if target.is_file():
                    try:same=target.stat().st_size==fp.stat().st_size and self._sha256(target)==self._sha256(fp)
                    except OSError:same=False
                items.append({'kind':'file','source':str(Path('files')/rel),'target':str(target),'action':'unchanged' if same else action,'size_bytes':fp.stat().st_size})
        changes=sum(1 for x in items if x['action']!='unchanged')
        return {'ok':True,'dry_run':True,'restore_applied':False,'manifest':manifest,'items':items,'change_count':changes,'unchanged_count':len(items)-changes,'requires_rescue_backup':True,'requires_service_quiesce':True,'rollback_required':True}

    def create(self)->dict[str,Any]:
        self.root.mkdir(parents=True,exist_ok=True)
        ts=float(self.clock());stamp=time.strftime('%Y%m%d-%H%M%S',time.localtime(ts));final=self.root/f'beastagotchi-backup-{stamp}.tar.gz'
        with tempfile.TemporaryDirectory(prefix='beast-backup-') as td:
            stage=Path(td)/'beastagotchi-backup';stage.mkdir()
            dbdest=stage/'beast.db'
            if self.db_path.exists():self._sqlite_snapshot(dbdest)
            copied=[]
            for src in self.sources:
                if not src.exists():continue
                if src.is_dir():
                    dest=stage/'files'/src.as_posix().lstrip('/')
                    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(src,dest,dirs_exist_ok=True);copied.append(str(src))
                else:
                    dest=stage/'files'/src.as_posix().lstrip('/')
                    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);copied.append(str(src))
            manifest={'created_at':ts,'format':1,'db_snapshot':dbdest.exists(),'sources':copied,'sensitive':True}
            (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
            with tarfile.open(final,'w:gz') as tf:tf.add(stage,arcname='beastagotchi-backup')
        os.chmod(final,0o600)
        rows=sorted(self.root.glob('beastagotchi-backup-*.tar.gz'),key=lambda p:p.stat().st_mtime,reverse=True)
        for old in rows[self.keep:]:
            try:old.unlink()
            except OSError:pass
        return {'ok':True,'path':str(final),'size_bytes':final.stat().st_size,'sha256':self._sha256(final),'created_at':ts,'retention':self.keep}
