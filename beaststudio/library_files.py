from __future__ import annotations

import mimetypes
import os
import re
import time
from pathlib import Path
from typing import Any

_ALLOWED={'.txt','.md','.markdown','.rst','.log','.csv','.json','.toml','.yaml','.yml','.html','.htm','.pdf','.epub','.zim'}
_SAFE=re.compile(r'[^A-Za-z0-9._ -]+')


class LibraryFileError(ValueError):
    pass


class LibraryFileManager:
    """Safe Beast Studio import/read boundary for offline Field Library files."""

    def __init__(self, root: str='/var/lib/beastagotchi/library/imports', *, max_bytes: int=64*1024*1024,
                 readable_roots: tuple[str,...]=('/var/lib/beastagotchi/library','/home/pi/beast-library')) -> None:
        self.root=Path(root)
        self.max_bytes=max(1024,int(max_bytes))
        self.readable_roots=tuple(Path(x).resolve() for x in readable_roots)

    @staticmethod
    def _clean_name(name: str) -> str:
        base=Path(str(name or '')).name.strip()
        base=_SAFE.sub('_',base).strip(' .')
        if not base:raise LibraryFileError('filename required')
        if len(base)>180:
            stem=Path(base).stem[:140];ext=Path(base).suffix[:20];base=stem+ext
        ext=Path(base).suffix.lower()
        if ext not in _ALLOWED:raise LibraryFileError(f'unsupported Field Library file type: {ext or "none"}')
        return base

    def save(self,name: str,data: bytes) -> dict[str,Any]:
        if len(data)>self.max_bytes:raise LibraryFileError(f'file exceeds {self.max_bytes//(1024*1024)} MiB upload limit')
        clean=self._clean_name(name)
        self.root.mkdir(parents=True,exist_ok=True)
        try:os.chmod(self.root,0o750)
        except Exception:pass
        dest=self.root/clean
        if dest.exists():
            stamp=time.strftime('%Y%m%d-%H%M%S')
            dest=self.root/f'{dest.stem}-{stamp}{dest.suffix}'
            n=2
            while dest.exists():
                dest=self.root/f'{Path(clean).stem}-{stamp}-{n}{Path(clean).suffix}';n+=1
        tmp=dest.with_name('.'+dest.name+'.uploading')
        with open(tmp,'wb') as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        os.chmod(tmp,0o600);os.replace(tmp,dest)
        return {'ok':True,'name':dest.name,'path':str(dest),'size_bytes':len(data),'indexing':'automatic_within_60_seconds'}

    def _allowed_path(self,path: str) -> Path:
        p=Path(str(path or '')).resolve(strict=True)
        for root in self.readable_roots:
            try:p.relative_to(root);return p
            except ValueError:continue
        raise LibraryFileError('document path is outside Field Library roots')

    def read(self,path: str) -> tuple[bytes,str,str]:
        p=self._allowed_path(path)
        if not p.is_file():raise LibraryFileError('document file missing')
        size=p.stat().st_size
        if size>self.max_bytes:raise LibraryFileError('document too large for browser transfer')
        data=p.read_bytes()
        ctype=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
        return data,ctype,p.name
