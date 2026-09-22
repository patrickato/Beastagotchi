from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Any

from .document_extractors import extract as extract_document, capabilities as extractor_capabilities

_TEXT_EXTS={'.txt','.md','.markdown','.rst','.log','.csv','.json','.toml','.yaml','.yml','.html','.htm'}
_DOC_EXTS=_TEXT_EXTS|{'.pdf','.epub','.zim'}


class FieldLibraryEngine:
    """Low-frequency local document index for offline field reference.

    Text-like files are indexed directly. PDF/EPUB/ZIM files are catalogued by
    metadata now and can gain richer extractors later without changing the API.
    """

    def __init__(self,state,store,roots=None,clock=time.time,max_text_bytes: int=1_000_000) -> None:
        self.state=state;self.store=store;self.clock=clock;self.max_text_bytes=max(16_384,int(max_text_bytes))
        self.roots=[Path(x) for x in (roots or ['/var/lib/beastagotchi/library','/home/pi/beast-library'])]

    @staticmethod
    def _title(path: Path) -> str:
        return path.stem.replace('_',' ').replace('-',' ').strip() or path.name

    def _text(self,path: Path) -> tuple[str,str]:
        return extract_document(path,self.max_text_bytes,_TEXT_EXTS)

    def tick(self) -> dict[str,Any]:
        now=float(self.clock());seen=set();indexed=0;bytes_total=0;roots_present=[];extractor_counts={};extract_failures=0
        try:self.store.upsert_job({'id':'field-library-index','kind':'index','label':'Field Library Index','status':'running','created_at':now,'started_at':now,'progress':0.0,'detail':'Scanning offline knowledge roots'})
        except Exception:pass
        for root in self.roots:
            if not root.is_dir():continue
            roots_present.append(str(root))
            try:paths=list(root.rglob('*'))
            except Exception:paths=[]
            for p in paths:
                try:
                    if not p.is_file() or p.suffix.lower() not in _DOC_EXTS:continue
                    st=p.stat();key=str(p.resolve());seen.add(key);bytes_total+=int(st.st_size)
                    sig=f"{st.st_mtime_ns}:{st.st_size}:{key}".encode();doc_id=hashlib.sha1(sig).hexdigest()
                    text,extractor=self._text(p)
                    extractor_counts[extractor]=extractor_counts.get(extractor,0)+1
                    if p.suffix.lower() in {'.pdf','.epub'} and not text:extract_failures+=1
                    self.store.upsert_library_document({
                        'id':doc_id,'path':key,'filename':p.name,'title':self._title(p),'extension':p.suffix.lower(),
                        'size_bytes':int(st.st_size),'mtime':float(st.st_mtime),'indexed_at':now,'text':text,
                    });indexed+=1
                except Exception:continue
        try:self.store.mark_missing_library_documents(seen,now)
        except Exception:pass
        summary=self.store.library_summary(6)
        try:self.store.upsert_job({'id':'field-library-index','kind':'index','label':'Field Library Index','status':'complete','created_at':now,'started_at':now,'finished_at':float(self.clock()),'progress':1.0,'detail':f"Indexed {indexed} files",'result':{'files':indexed,'documents':summary.get('total',0)}})
        except Exception:pass
        return {
            'library.state':'ready',
            'library.roots':roots_present,
            'library.document_count':int(summary.get('total') or 0),
            'library.text_indexed_count':int(summary.get('text_indexed') or 0),
            'library.storage_bytes':int(summary.get('bytes') or bytes_total),
            'library.recent':summary.get('recent') or [],
            'library.last_indexed_at':now,
            'library.last_scan_files':indexed,
            'library.extractors':extractor_capabilities(),
            'library.extractor_counts':extractor_counts,
            'library.extract_failures':extract_failures,
            'library.search_engine':'fts5' if bool(getattr(self.store,'library_fts',False)) else 'like_fallback',
        }
