from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  ts REAL NOT NULL,
  type TEXT NOT NULL,
  source TEXT NOT NULL,
  severity TEXT NOT NULL,
  data_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(type, ts);
CREATE TABLE IF NOT EXISTS samples (
  ts REAL NOT NULL,
  key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  source TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_samples_key_ts ON samples(key, ts);
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS wifi_encounters (
  bssid TEXT PRIMARY KEY,
  first_seen REAL NOT NULL,
  last_seen REAL NOT NULL,
  seen_sessions INTEGER NOT NULL DEFAULT 1,
  ssid TEXT,
  vendor TEXT,
  channel INTEGER,
  strongest_rssi REAL
);
CREATE INDEX IF NOT EXISTS idx_wifi_encounters_last_seen ON wifi_encounters(last_seen);
CREATE INDEX IF NOT EXISTS idx_wifi_encounters_vendor ON wifi_encounters(vendor);
CREATE TABLE IF NOT EXISTS expeditions (
  id TEXT PRIMARY KEY,
  started_at REAL NOT NULL,
  last_update REAL NOT NULL,
  ended_at REAL,
  status TEXT NOT NULL DEFAULT 'active',
  end_reason TEXT,
  recovered INTEGER NOT NULL DEFAULT 0,
  distance_m REAL NOT NULL DEFAULT 0,
  route_points INTEGER NOT NULL DEFAULT 0,
  ap_unique INTEGER NOT NULL DEFAULT 0,
  captures_delta INTEGER NOT NULL DEFAULT 0,
  xp_delta INTEGER NOT NULL DEFAULT 0,
  gps_fix_samples INTEGER NOT NULL DEFAULT 0,
  max_temp_c REAL,
  max_cpu_pct REAL,
  min_battery_pct REAL,
  start_captures INTEGER NOT NULL DEFAULT 0,
  start_xp INTEGER NOT NULL DEFAULT 0,
  summary_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_expeditions_started ON expeditions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_expeditions_status ON expeditions(status,last_update DESC);
CREATE TABLE IF NOT EXISTS expedition_points (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  expedition_id TEXT NOT NULL,
  ts REAL NOT NULL,
  latitude REAL NOT NULL,
  longitude REAL NOT NULL,
  altitude_m REAL,
  accuracy_m REAL,
  speed_mps REAL,
  heading_deg REAL,
  temp_c REAL,
  cpu_pct REAL,
  governor TEXT
);
CREATE INDEX IF NOT EXISTS idx_expedition_points_exp_ts ON expedition_points(expedition_id,ts);
CREATE TABLE IF NOT EXISTS expedition_aps (
  expedition_id TEXT NOT NULL,
  bssid TEXT NOT NULL,
  first_seen REAL NOT NULL,
  ssid TEXT,
  vendor TEXT,
  channel INTEGER,
  strongest_rssi REAL,
  PRIMARY KEY(expedition_id,bssid)
);
CREATE INDEX IF NOT EXISTS idx_expedition_aps_exp ON expedition_aps(expedition_id);
CREATE TABLE IF NOT EXISTS captures (
  path TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  extension TEXT,
  size_bytes INTEGER NOT NULL DEFAULT 0,
  mtime REAL NOT NULL DEFAULT 0,
  indexed_at REAL NOT NULL,
  network_hint TEXT,
  status TEXT NOT NULL DEFAULT 'present'
);
CREATE INDEX IF NOT EXISTS idx_captures_mtime ON captures(mtime DESC);
CREATE TABLE IF NOT EXISTS actions (
  id TEXT PRIMARY KEY,
  ts REAL NOT NULL,
  finished_at REAL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT,
  status TEXT NOT NULL,
  request_json TEXT NOT NULL,
  plan_json TEXT NOT NULL,
  result_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_actions_ts ON actions(ts DESC);
CREATE INDEX IF NOT EXISTS idx_actions_target_ts ON actions(target,ts DESC);
CREATE TABLE IF NOT EXISTS library_documents (
  id TEXT PRIMARY KEY,
  path TEXT UNIQUE NOT NULL,
  filename TEXT NOT NULL,
  title TEXT NOT NULL,
  extension TEXT,
  size_bytes INTEGER NOT NULL DEFAULT 0,
  mtime REAL NOT NULL DEFAULT 0,
  indexed_at REAL NOT NULL,
  text_content TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'present'
);
CREATE INDEX IF NOT EXISTS idx_library_documents_mtime ON library_documents(mtime DESC);
CREATE INDEX IF NOT EXISTS idx_library_documents_title ON library_documents(title);
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  label TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at REAL NOT NULL,
  started_at REAL,
  finished_at REAL,
  progress REAL,
  detail TEXT,
  result_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);
CREATE TABLE IF NOT EXISTS incidents (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  opened_at REAL NOT NULL,
  last_seen REAL NOT NULL,
  resolved_at REAL,
  summary TEXT NOT NULL,
  detail TEXT,
  snapshot_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_incidents_status_seen ON incidents(status,last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_kind_seen ON incidents(kind,last_seen DESC);
"""

class Store:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)
        self.library_fts = False
        self._migrate()
        self.conn.commit()

    def _migrate(self) -> None:
        """Forward-only additive migrations for pre-v0.13 databases."""
        cols={r[1] for r in self.conn.execute("PRAGMA table_info(wifi_encounters)").fetchall()}
        additions={
            "encryption":"TEXT", "channels_json":"TEXT", "observation_count":"INTEGER NOT NULL DEFAULT 1",
            "max_clients":"INTEGER NOT NULL DEFAULT 0", "last_latitude":"REAL", "last_longitude":"REAL",
            "last_accuracy_m":"REAL",
        }
        for name,decl in additions.items():
            if name not in cols:self.conn.execute(f"ALTER TABLE wifi_encounters ADD COLUMN {name} {decl}")
        # FTS5 is available in normal Raspberry Pi / Python SQLite builds, but
        # Field Library must remain usable if a custom build omits it.
        try:
            self.conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS library_fts USING fts5(
                id UNINDEXED, title, filename, path UNINDEXED, text_content,
                tokenize='unicode61 remove_diacritics 2'
            )""")
            self.library_fts = True
            count=int(self.conn.execute("SELECT COUNT(*) FROM library_fts").fetchone()[0])
            if count==0:
                self.conn.execute("""INSERT INTO library_fts(id,title,filename,path,text_content)
                    SELECT id,title,filename,path,text_content FROM library_documents WHERE status='present'""")
        except sqlite3.OperationalError:
            self.library_fts = False

    def add_event(self, ev: Any) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO events(id,ts,type,source,severity,data_json) VALUES(?,?,?,?,?,?)",
            (ev.id, ev.ts, ev.type, ev.source, ev.severity, json.dumps(ev.data, separators=(",", ":"), default=str)),
        )
        self.conn.commit()

    def add_sample(self, ts: float, key: str, value: Any, source: str) -> None:
        self.add_samples([(ts, key, value, source)])

    def add_samples(self, rows: list[tuple[float, str, Any, str]]) -> None:
        if not rows: return
        vals = [(ts, key, json.dumps(value, separators=(",", ":"), default=str), source) for ts,key,value,source in rows]
        with self.conn:
            self.conn.executemany("INSERT INTO samples(ts,key,value_json,source) VALUES(?,?,?,?)", vals)

    def prune_samples(self, before_ts: float) -> int:
        with self.conn:
            cur = self.conn.execute("DELETE FROM samples WHERE ts < ?", (before_ts,))
        return int(cur.rowcount or 0)

    def query_samples(self, key: str, since: float = 0.0, limit: int = 1000) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 5000))
        rows = self.conn.execute(
            "SELECT ts,value_json,source FROM samples WHERE key=? AND ts>=? ORDER BY ts DESC LIMIT ?",
            (key, float(since), limit),
        ).fetchall()
        out = []
        for ts, value_json, source in reversed(rows):
            try: value = json.loads(value_json)
            except Exception: value = value_json
            out.append({"ts": ts, "value": value, "source": source})
        return out


    def record_wifi_encounters(self, aps: list[dict[str, Any]], ts: float | None = None) -> dict[str, Any]:
        """Record session-first AP observations and return lifetime-new counts.

        This is called only for BSSIDs first observed in the current Beast Core session,
        so it does not hammer the SD card every scan cycle.
        """
        if not aps:
            return {"new_count": 0, "total": self.count_wifi_encounters(), "new_bssids": []}
        ts = float(ts or __import__('time').time())
        new_bssids: list[str] = []
        with self.conn:
            for ap in aps:
                if not isinstance(ap, dict):
                    continue
                bssid = str(ap.get("bssid") or ap.get("mac") or "").lower().strip()
                if not bssid:
                    continue
                row = self.conn.execute("SELECT strongest_rssi,channels_json FROM wifi_encounters WHERE bssid=?", (bssid,)).fetchone()
                ssid = str(ap.get("ssid") or ap.get("hostname") or "<hidden>")
                vendor = str(ap.get("vendor") or "")
                ch = ap.get("channel")
                try: ch = int(ch) if ch is not None else None
                except Exception: ch = None
                rssi = ap.get("rssi")
                try: rssi = float(rssi) if rssi is not None else None
                except Exception: rssi = None
                encryption=str(ap.get("encryption") or ap.get("security") or "")
                clients=ap.get("clients") or [];client_count=len(clients) if isinstance(clients,list) else 0
                if row is None:
                    self.conn.execute(
                        "INSERT INTO wifi_encounters(bssid,first_seen,last_seen,seen_sessions,ssid,vendor,channel,strongest_rssi,encryption,channels_json,observation_count,max_clients) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                        (bssid, ts, ts, 1, ssid, vendor, ch, rssi, encryption, json.dumps([ch] if ch is not None else []), 1, client_count),
                    )
                    new_bssids.append(bssid)
                else:
                    old_rssi,old_channels = row
                    strongest = rssi if old_rssi is None else old_rssi if rssi is None else max(float(old_rssi), rssi)
                    try:channels=set(json.loads(old_channels or "[]"))
                    except Exception:channels=set()
                    if ch is not None:channels.add(ch)
                    self.conn.execute(
                        "UPDATE wifi_encounters SET last_seen=?,seen_sessions=seen_sessions+1,ssid=?,vendor=?,channel=?,strongest_rssi=?,encryption=?,channels_json=?,observation_count=COALESCE(observation_count,0)+1,max_clients=MAX(COALESCE(max_clients,0),?) WHERE bssid=?",
                        (ts, ssid, vendor, ch, strongest, encryption, json.dumps(sorted(channels)), client_count, bssid),
                    )
        return {"new_count": len(new_bssids), "total": self.count_wifi_encounters(), "new_bssids": new_bssids}

    def count_wifi_encounters(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) FROM wifi_encounters").fetchone()
        return int(row[0] if row else 0)

    def encounter_summary(self, limit: int = 8) -> dict[str, Any]:
        total = self.count_wifi_encounters()
        vendors = self.conn.execute("SELECT COUNT(DISTINCT vendor) FROM wifi_encounters WHERE vendor IS NOT NULL AND vendor<>''").fetchone()[0]
        recent = self.conn.execute(
            "SELECT bssid,ssid,vendor,channel,strongest_rssi,last_seen,seen_sessions FROM wifi_encounters ORDER BY last_seen DESC LIMIT ?",
            (max(1, min(int(limit), 100)),),
        ).fetchall()
        return {
            "total": int(total),
            "vendor_count": int(vendors or 0),
            "recent": [
                {"bssid":r[0],"ssid":r[1],"vendor":r[2],"channel":r[3],"strongest_rssi":r[4],"last_seen":r[5],"seen_sessions":r[6]}
                for r in recent
            ],
        }


    def update_wifi_observations(self, aps: list[dict[str, Any]], ts: float, gps: dict[str, Any] | None = None) -> int:
        """Enrich already-known encounters without creating session-new rows."""
        if not isinstance(aps,list):return 0
        updated=0
        with self.conn:
            for ap in aps:
                if not isinstance(ap,dict):continue
                bssid=str(ap.get('bssid') or ap.get('mac') or '').strip().lower()
                if not bssid:continue
                row=self.conn.execute('SELECT strongest_rssi,channels_json FROM wifi_encounters WHERE bssid=?',(bssid,)).fetchone()
                if row is None:continue
                old_rssi,channels_json=row
                try:rssi=float(ap.get('rssi')) if ap.get('rssi') is not None else None
                except Exception:rssi=None
                strongest=rssi if old_rssi is None else old_rssi if rssi is None else max(float(old_rssi),rssi)
                try:ch=int(ap.get('channel')) if ap.get('channel') is not None else None
                except Exception:ch=None
                try:channels=set(json.loads(channels_json or '[]'))
                except Exception:channels=set()
                if ch is not None:channels.add(ch)
                clients=ap.get('clients') or [];client_count=len(clients) if isinstance(clients,list) else 0
                lat=lon=acc=None
                if isinstance(gps,dict):lat=gps.get('latitude');lon=gps.get('longitude');acc=gps.get('accuracy_m')
                sql=("UPDATE wifi_encounters SET last_seen=?,ssid=?,vendor=?,channel=?,strongest_rssi=?,encryption=?,channels_json=?, "
                     "observation_count=COALESCE(observation_count,0)+1,max_clients=MAX(COALESCE(max_clients,0),?), "
                     "last_latitude=COALESCE(?,last_latitude),last_longitude=COALESCE(?,last_longitude),last_accuracy_m=COALESCE(?,last_accuracy_m) WHERE bssid=?")
                self.conn.execute(sql,(float(ts),str(ap.get('ssid') or ap.get('hostname') or '<hidden>'),str(ap.get('vendor') or ''),ch,strongest,
                    str(ap.get('encryption') or ap.get('security') or ''),json.dumps(sorted(channels)),client_count,lat,lon,acc,bssid))
                updated+=1
        return updated

    def search_encounters(self, query: str = '', limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        limit=max(1,min(int(limit),200));offset=max(0,int(offset));q=str(query or '').strip()
        fields='bssid,ssid,vendor,channel,strongest_rssi,last_seen,seen_sessions,encryption,channels_json,observation_count,max_clients,last_latitude,last_longitude,last_accuracy_m'
        if q:
            like=f'%{q}%';rows=self.conn.execute(f'SELECT {fields} FROM wifi_encounters WHERE ssid LIKE ? OR vendor LIKE ? OR bssid LIKE ? ORDER BY last_seen DESC LIMIT ? OFFSET ?',(like,like,like,limit,offset)).fetchall()
        else:
            rows=self.conn.execute(f'SELECT {fields} FROM wifi_encounters ORDER BY last_seen DESC LIMIT ? OFFSET ?',(limit,offset)).fetchall()
        keys=['bssid','ssid','vendor','channel','strongest_rssi','last_seen','seen_sessions','encryption','channels_json','observation_count','max_clients','last_latitude','last_longitude','last_accuracy_m']
        out=[]
        for r in rows:
            d=dict(zip(keys,r))
            try:d['channels']=json.loads(d.pop('channels_json') or '[]')
            except Exception:d['channels']=[];d.pop('channels_json',None)
            out.append(d)
        return out

    def encounter_detail(self,bssid: str) -> dict[str,Any] | None:
        rows=self.search_encounters(str(bssid),20,0);target=str(bssid).strip().lower()
        return next((r for r in rows if str(r.get('bssid','')).lower()==target),None)

    @staticmethod
    def _capture_hint(filename: str) -> str:
        return Path(filename).stem[:80]

    def index_capture_directory(self, root: Path, ts: float | None = None) -> dict[str,Any]:
        from collections import Counter
        root=Path(root);ts=float(ts or __import__('time').time());seen=set();formats=Counter();total_bytes=0
        if root.exists():
            with self.conn:
                for fp in root.rglob('*'):
                    try:
                        if not fp.is_file() or fp.suffix.lower() not in {'.pcap','.pcapng','.22000','.16800','.hccapx','.cap'}:continue
                        st=fp.stat();path=str(fp);seen.add(path);ext=fp.suffix.lower();formats[ext or '<none>']+=1;total_bytes+=int(st.st_size)
                        sql=("INSERT INTO captures(path,filename,extension,size_bytes,mtime,indexed_at,network_hint,status) VALUES(?,?,?,?,?,?,?,'present') "
                             "ON CONFLICT(path) DO UPDATE SET filename=excluded.filename,extension=excluded.extension,size_bytes=excluded.size_bytes,mtime=excluded.mtime,indexed_at=excluded.indexed_at,network_hint=excluded.network_hint,status='present'")
                        self.conn.execute(sql,(path,fp.name,ext,int(st.st_size),float(st.st_mtime),ts,self._capture_hint(fp.name)))
                    except OSError:continue
                self.conn.execute("UPDATE captures SET status='missing',indexed_at=? WHERE status='present'",(ts,))
                if seen:self.conn.executemany("UPDATE captures SET status='present' WHERE path=?",[(x,) for x in seen])
        rows=self.conn.execute("SELECT path,filename,extension,size_bytes,mtime,network_hint,status FROM captures WHERE status='present' ORDER BY mtime DESC LIMIT 12").fetchall()
        count=self.conn.execute("SELECT COUNT(*) FROM captures WHERE status='present'").fetchone()[0]
        bytes_db=self.conn.execute("SELECT COALESCE(SUM(size_bytes),0) FROM captures WHERE status='present'").fetchone()[0]
        return {'count':int(count or 0),'bytes':int(bytes_db or total_bytes),'formats':dict(formats),'recent':[{'path':r[0],'filename':r[1],'extension':r[2],'size_bytes':r[3],'mtime':r[4],'network_hint':r[5],'status':r[6]} for r in rows]}

    def capture_summary(self,limit: int=20) -> dict[str,Any]:
        limit=max(1,min(int(limit),200));rows=self.conn.execute("SELECT path,filename,extension,size_bytes,mtime,network_hint,status FROM captures WHERE status='present' ORDER BY mtime DESC LIMIT ?",(limit,)).fetchall();count=self.conn.execute("SELECT COUNT(*) FROM captures WHERE status='present'").fetchone()[0];size=self.conn.execute("SELECT COALESCE(SUM(size_bytes),0) FROM captures WHERE status='present'").fetchone()[0]
        return {'count':int(count or 0),'bytes':int(size or 0),'recent':[{'path':r[0],'filename':r[1],'extension':r[2],'size_bytes':r[3],'mtime':r[4],'network_hint':r[5],'status':r[6]} for r in rows]}

    _EXP_FIELDS = {
        "last_update", "ended_at", "status", "end_reason", "recovered",
        "distance_m", "route_points", "ap_unique", "captures_delta", "xp_delta",
        "gps_fix_samples", "max_temp_c", "max_cpu_pct", "min_battery_pct",
        "start_captures", "start_xp", "summary_json",
    }

    @staticmethod
    def _expedition_row(row) -> dict[str, Any] | None:
        if row is None:
            return None
        keys = ["id","started_at","last_update","ended_at","status","end_reason","recovered",
                "distance_m","route_points","ap_unique","captures_delta","xp_delta","gps_fix_samples",
                "max_temp_c","max_cpu_pct","min_battery_pct","start_captures","start_xp","summary_json"]
        out = dict(zip(keys,row))
        if out.get("summary_json"):
            try: out["summary"] = json.loads(out["summary_json"])
            except Exception: out["summary"] = {}
        out["recovered"] = int(out.get("recovered") or 0)
        return out

    def begin_expedition(self, expedition_id: str, started_at: float, start_captures: int = 0, start_xp: int = 0) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO expeditions(id,started_at,last_update,status,start_captures,start_xp) VALUES(?,?,?,?,?,?)",
                (str(expedition_id), float(started_at), float(started_at), "active", int(start_captures), int(start_xp)),
            )

    def update_expedition(self, expedition_id: str, **fields: Any) -> None:
        clean = {k:v for k,v in fields.items() if k in self._EXP_FIELDS}
        if not clean:
            return
        if "summary_json" in clean and not isinstance(clean["summary_json"], str):
            clean["summary_json"] = json.dumps(clean["summary_json"], separators=(",",":"), default=str)
        cols = ",".join(f"{k}=?" for k in clean)
        vals = list(clean.values()) + [str(expedition_id)]
        with self.conn:
            self.conn.execute(f"UPDATE expeditions SET {cols} WHERE id=?", vals)

    def end_expedition(self, expedition_id: str, ended_at: float, reason: str, status: str = "complete", **fields: Any) -> None:
        payload = dict(fields)
        payload.update({"last_update":float(ended_at), "ended_at":float(ended_at), "end_reason":str(reason), "status":str(status)})
        self.update_expedition(expedition_id, **payload)

    def get_expedition(self, expedition_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT id,started_at,last_update,ended_at,status,end_reason,recovered,distance_m,route_points,ap_unique,captures_delta,xp_delta,gps_fix_samples,max_temp_c,max_cpu_pct,min_battery_pct,start_captures,start_xp,summary_json FROM expeditions WHERE id=?",
            (str(expedition_id),),
        ).fetchone()
        return self._expedition_row(row)

    def active_expedition(self) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT id,started_at,last_update,ended_at,status,end_reason,recovered,distance_m,route_points,ap_unique,captures_delta,xp_delta,gps_fix_samples,max_temp_c,max_cpu_pct,min_battery_pct,start_captures,start_xp,summary_json FROM expeditions WHERE status='active' ORDER BY last_update DESC LIMIT 1"
        ).fetchone()
        return self._expedition_row(row)

    def recent_expeditions(self, limit: int = 20) -> list[dict[str, Any]]:
        limit=max(1,min(int(limit),200))
        rows=self.conn.execute(
            "SELECT id,started_at,last_update,ended_at,status,end_reason,recovered,distance_m,route_points,ap_unique,captures_delta,xp_delta,gps_fix_samples,max_temp_c,max_cpu_pct,min_battery_pct,start_captures,start_xp,summary_json FROM expeditions ORDER BY started_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._expedition_row(r) for r in rows]

    def add_expedition_point(self, expedition_id: str, ts: float, latitude: float, longitude: float, **fields: Any) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO expedition_points(expedition_id,ts,latitude,longitude,altitude_m,accuracy_m,speed_mps,heading_deg,temp_c,cpu_pct,governor) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (str(expedition_id),float(ts),float(latitude),float(longitude),fields.get("altitude_m"),fields.get("accuracy_m"),fields.get("speed_mps"),fields.get("heading_deg"),fields.get("temp_c"),fields.get("cpu_pct"),fields.get("governor")),
            )

    def last_expedition_point(self, expedition_id: str) -> dict[str, Any] | None:
        row=self.conn.execute(
            "SELECT ts,latitude,longitude,altitude_m,accuracy_m,speed_mps,heading_deg,temp_c,cpu_pct,governor FROM expedition_points WHERE expedition_id=? ORDER BY ts DESC LIMIT 1",
            (str(expedition_id),),
        ).fetchone()
        if not row:return None
        keys=["ts","latitude","longitude","altitude_m","accuracy_m","speed_mps","heading_deg","temp_c","cpu_pct","governor"]
        return dict(zip(keys,row))

    def expedition_points(self, expedition_id: str, limit: int = 2000) -> list[dict[str, Any]]:
        limit=max(1,min(int(limit),10000))
        rows=self.conn.execute(
            "SELECT ts,latitude,longitude,altitude_m,accuracy_m,speed_mps,heading_deg,temp_c,cpu_pct,governor FROM expedition_points WHERE expedition_id=? ORDER BY ts ASC LIMIT ?",
            (str(expedition_id),limit),
        ).fetchall()
        keys=["ts","latitude","longitude","altitude_m","accuracy_m","speed_mps","heading_deg","temp_c","cpu_pct","governor"]
        return [dict(zip(keys,r)) for r in rows]

    def record_expedition_aps(self, expedition_id: str, aps: list[dict[str, Any]]) -> None:
        if not aps:return
        with self.conn:
            for ap in aps:
                bssid=str(ap.get("bssid") or "").strip().lower()
                if not bssid:continue
                ch=ap.get("channel")
                try:ch=int(ch) if ch is not None else None
                except Exception:ch=None
                rssi=ap.get("rssi")
                try:rssi=float(rssi) if rssi is not None else None
                except Exception:rssi=None
                self.conn.execute(
                    "INSERT OR IGNORE INTO expedition_aps(expedition_id,bssid,first_seen,ssid,vendor,channel,strongest_rssi) VALUES(?,?,?,?,?,?,?)",
                    (str(expedition_id),bssid,float(ap.get("ts") or 0),str(ap.get("ssid") or "<hidden>"),str(ap.get("vendor") or ""),ch,rssi),
                )

    def expedition_ap_bssids(self, expedition_id: str) -> list[str]:
        return [r[0] for r in self.conn.execute("SELECT bssid FROM expedition_aps WHERE expedition_id=?",(str(expedition_id),)).fetchall()]

    def expedition_detail(self, expedition_id: str, point_limit: int = 2000) -> dict[str, Any] | None:
        exp=self.get_expedition(expedition_id)
        if not exp:return None
        exp["points"]=self.expedition_points(expedition_id,point_limit)
        exp["aps"]=int(self.conn.execute("SELECT COUNT(*) FROM expedition_aps WHERE expedition_id=?",(str(expedition_id),)).fetchone()[0])
        return exp

    def add_action(self, row: dict[str, Any]) -> None:
        # Privileged actions are executed by ActionServer in a worker thread.
        # Use a short-lived SQLite connection here instead of sharing the Core's
        # event-loop-owned connection across threads. WAL keeps this cheap.
        conn=sqlite3.connect(self.path,timeout=5.0)
        try:
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO actions(id,ts,finished_at,actor,action,target,status,request_json,plan_json,result_json) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (str(row.get("id")), float(row.get("ts") or 0), row.get("finished_at"), str(row.get("actor") or "local"), str(row.get("action") or ""), str(row.get("target") or ""), str(row.get("status") or "unknown"), json.dumps(row.get("request") or {}, separators=(",",":"), default=str), json.dumps(row.get("plan") or {}, separators=(",",":"), default=str), json.dumps(row.get("result") or {}, separators=(",",":"), default=str)),
                )
        finally:
            conn.close()

    def recent_actions(self, limit: int = 50) -> list[dict[str, Any]]:
        limit=max(1,min(int(limit),500))
        rows=self.conn.execute("SELECT id,ts,finished_at,actor,action,target,status,request_json,plan_json,result_json FROM actions ORDER BY ts DESC LIMIT ?",(limit,)).fetchall()
        out=[]
        for row in rows:
            item=dict(zip(["id","ts","finished_at","actor","action","target","status","request_json","plan_json","result_json"],row))
            for src,dst in (("request_json","request"),("plan_json","plan"),("result_json","result")):
                try:item[dst]=json.loads(item.pop(src) or "{}")
                except Exception:item[dst]={};item.pop(src,None)
            out.append(item)
        return out

    def upsert_library_document(self, row: dict[str, Any]) -> None:
        with self.conn:
            self.conn.execute(
                """INSERT INTO library_documents(id,path,filename,title,extension,size_bytes,mtime,indexed_at,text_content,status)
                   VALUES(?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(path) DO UPDATE SET id=excluded.id,filename=excluded.filename,title=excluded.title,
                   extension=excluded.extension,size_bytes=excluded.size_bytes,mtime=excluded.mtime,indexed_at=excluded.indexed_at,
                   text_content=excluded.text_content,status='present'""",
                (str(row.get('id') or ''),str(row.get('path') or ''),str(row.get('filename') or ''),str(row.get('title') or ''),
                 str(row.get('extension') or ''),int(row.get('size_bytes') or 0),float(row.get('mtime') or 0),
                 float(row.get('indexed_at') or 0),str(row.get('text') or ''),str(row.get('status') or 'present'))
            )
            if self.library_fts:
                path=str(row.get('path') or '')
                self.conn.execute("DELETE FROM library_fts WHERE path=?",(path,))
                self.conn.execute("INSERT INTO library_fts(id,title,filename,path,text_content) VALUES(?,?,?,?,?)",
                    (str(row.get('id') or ''),str(row.get('title') or ''),str(row.get('filename') or ''),path,str(row.get('text') or '')))

    def mark_missing_library_documents(self, present_paths: set[str], ts: float) -> int:
        rows=self.conn.execute("SELECT path FROM library_documents WHERE status='present'").fetchall()
        missing=[str(r[0]) for r in rows if str(r[0]) not in present_paths]
        if not missing:return 0
        with self.conn:
            self.conn.executemany("UPDATE library_documents SET status='missing',indexed_at=? WHERE path=?",[(float(ts),x) for x in missing])
            if self.library_fts:
                self.conn.executemany("DELETE FROM library_fts WHERE path=?",[(x,) for x in missing])
        return len(missing)

    def search_captures(self, query: str='', limit: int=50) -> list[dict[str,Any]]:
        limit=max(1,min(int(limit),200));q=str(query or '').strip();like=f"%{q}%"
        if q:
            rows=self.conn.execute("SELECT path,filename,extension,size_bytes,mtime,indexed_at,network_hint,status FROM captures WHERE filename LIKE ? OR network_hint LIKE ? OR path LIKE ? ORDER BY mtime DESC LIMIT ?",(like,like,like,limit)).fetchall()
        else:
            rows=self.conn.execute("SELECT path,filename,extension,size_bytes,mtime,indexed_at,network_hint,status FROM captures ORDER BY mtime DESC LIMIT ?",(limit,)).fetchall()
        keys=['path','filename','extension','size_bytes','mtime','indexed_at','network_hint','status']
        return [dict(zip(keys,r)) for r in rows]

    def library_summary(self, limit: int=20) -> dict[str,Any]:
        limit=max(1,min(int(limit),200))
        total=int(self.conn.execute("SELECT COUNT(*) FROM library_documents WHERE status='present'").fetchone()[0])
        text_indexed=int(self.conn.execute("SELECT COUNT(*) FROM library_documents WHERE status='present' AND length(text_content)>0").fetchone()[0])
        bytes_total=int(self.conn.execute("SELECT COALESCE(SUM(size_bytes),0) FROM library_documents WHERE status='present'").fetchone()[0])
        rows=self.conn.execute("SELECT id,path,filename,title,extension,size_bytes,mtime,indexed_at,status,length(text_content) FROM library_documents WHERE status='present' ORDER BY mtime DESC LIMIT ?",(limit,)).fetchall()
        keys=['id','path','filename','title','extension','size_bytes','mtime','indexed_at','status','text_chars']
        return {'total':total,'text_indexed':text_indexed,'bytes':bytes_total,'recent':[dict(zip(keys,r)) for r in rows]}

    def get_library_document(self, doc_id: str) -> dict[str,Any] | None:
        row=self.conn.execute("SELECT id,path,filename,title,extension,size_bytes,mtime,indexed_at,status,text_content FROM library_documents WHERE id=? LIMIT 1",(str(doc_id),)).fetchone()
        if not row:return None
        keys=['id','path','filename','title','extension','size_bytes','mtime','indexed_at','status','text']
        return dict(zip(keys,row))

    @staticmethod
    def _fts_query(query: str) -> str:
        terms=re.findall(r"[\w-]+",str(query or ''),flags=re.UNICODE)[:12]
        return " AND ".join(f'"{t.replace(chr(34), chr(34)*2)}"*' for t in terms if t)

    def search_library(self, query: str='', limit: int=50, offset: int=0) -> list[dict[str,Any]]:
        limit=max(1,min(int(limit),200));offset=max(0,int(offset));q=str(query or '').strip()
        keys=['id','path','filename','title','extension','size_bytes','mtime','indexed_at','status','snippet']
        if q and self.library_fts:
            try:
                match=self._fts_query(q)
                if match:
                    rows=self.conn.execute("""
                        SELECT d.id,d.path,d.filename,d.title,d.extension,d.size_bytes,d.mtime,d.indexed_at,d.status,
                               snippet(library_fts,4,'[',']',' … ',24)
                        FROM library_fts JOIN library_documents d ON d.path=library_fts.path
                        WHERE library_fts MATCH ? AND d.status='present'
                        ORDER BY bm25(library_fts), d.mtime DESC LIMIT ? OFFSET ?
                    """,(match,limit,offset)).fetchall()
                    return [dict(zip(keys,r)) for r in rows]
            except sqlite3.OperationalError:
                pass
        if q:
            like=f"%{q}%"
            rows=self.conn.execute("SELECT id,path,filename,title,extension,size_bytes,mtime,indexed_at,status,substr(text_content,1,240) FROM library_documents WHERE status='present' AND (title LIKE ? OR filename LIKE ? OR path LIKE ? OR text_content LIKE ?) ORDER BY mtime DESC LIMIT ? OFFSET ?",(like,like,like,like,limit,offset)).fetchall()
        else:
            rows=self.conn.execute("SELECT id,path,filename,title,extension,size_bytes,mtime,indexed_at,status,substr(text_content,1,240) FROM library_documents WHERE status='present' ORDER BY mtime DESC LIMIT ? OFFSET ?",(limit,offset)).fetchall()
        return [dict(zip(keys,r)) for r in rows]

    def search_events(self, query: str='', limit: int=50) -> list[dict[str,Any]]:
        limit=max(1,min(int(limit),200));q=str(query or '').strip()
        if q:
            like=f"%{q}%"
            rows=self.conn.execute("SELECT id,ts,type,source,severity,data_json FROM events WHERE type LIKE ? OR source LIKE ? OR data_json LIKE ? ORDER BY ts DESC LIMIT ?",(like,like,like,limit)).fetchall()
        else:
            rows=self.conn.execute("SELECT id,ts,type,source,severity,data_json FROM events ORDER BY ts DESC LIMIT ?",(limit,)).fetchall()
        out=[]
        for row in rows:
            item={'id':row[0],'ts':row[1],'type':row[2],'source':row[3],'severity':row[4]}
            try:item['data']=json.loads(row[5] or '{}')
            except Exception:item['data']={}
            out.append(item)
        return out

    def open_incident(self, row: dict[str,Any]) -> dict[str,Any]:
        kind=str(row.get('kind') or '')
        existing=self.conn.execute("SELECT id,opened_at FROM incidents WHERE kind=? AND status='open' ORDER BY opened_at DESC LIMIT 1",(kind,)).fetchone()
        iid=str(existing[0]) if existing else str(row.get('id') or '')
        opened=float(existing[1]) if existing else float(row.get('opened_at') or 0)
        with self.conn:
            self.conn.execute("""INSERT INTO incidents(id,kind,severity,status,opened_at,last_seen,resolved_at,summary,detail,snapshot_json) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET severity=excluded.severity,status='open',last_seen=excluded.last_seen,resolved_at=NULL,summary=excluded.summary,detail=excluded.detail,snapshot_json=CASE WHEN incidents.snapshot_json='{}' THEN excluded.snapshot_json ELSE incidents.snapshot_json END""",
            (iid,kind,str(row.get('severity') or 'warning'),'open',opened,float(row.get('last_seen') or opened),None,str(row.get('summary') or kind),str(row.get('detail') or ''),json.dumps(row.get('snapshot') or {},separators=(',',':'),default=str)))
        return {'id':iid,'kind':kind,'opened_at':opened}

    def resolve_incident(self, kind: str, ts: float) -> int:
        with self.conn:
            cur=self.conn.execute("UPDATE incidents SET status='resolved',resolved_at=?,last_seen=? WHERE kind=? AND status='open'",(float(ts),float(ts),str(kind)))
        return int(cur.rowcount or 0)

    def recent_incidents(self, limit: int=50, status: str|None=None) -> list[dict[str,Any]]:
        limit=max(1,min(int(limit),200))
        if status:rows=self.conn.execute("SELECT id,kind,severity,status,opened_at,last_seen,resolved_at,summary,detail,snapshot_json FROM incidents WHERE status=? ORDER BY last_seen DESC LIMIT ?",(str(status),limit)).fetchall()
        else:rows=self.conn.execute("SELECT id,kind,severity,status,opened_at,last_seen,resolved_at,summary,detail,snapshot_json FROM incidents ORDER BY last_seen DESC LIMIT ?",(limit,)).fetchall()
        keys=['id','kind','severity','status','opened_at','last_seen','resolved_at','summary','detail','snapshot_json'];out=[]
        for row in rows:
            item=dict(zip(keys,row))
            try:item['snapshot']=json.loads(item.pop('snapshot_json') or '{}')
            except Exception:item['snapshot']={};item.pop('snapshot_json',None)
            out.append(item)
        return out

    def upsert_job(self, row: dict[str,Any]) -> None:
        values=(str(row.get('id') or ''),str(row.get('kind') or ''),str(row.get('label') or ''),str(row.get('status') or 'queued'),float(row.get('created_at') or 0),row.get('started_at'),row.get('finished_at'),row.get('progress'),str(row.get('detail') or ''),json.dumps(row.get('result') or {},separators=(',',':'),default=str))
        # Jobs can be updated by ActionBroker worker threads as well as Core's
        # event loop. Use a short-lived connection so sqlite thread affinity
        # never turns a successful maintenance action into an incident.
        con=sqlite3.connect(self.path,timeout=5.0)
        try:
            with con:
                con.execute("""INSERT OR REPLACE INTO jobs(id,kind,label,status,created_at,started_at,finished_at,progress,detail,result_json) VALUES(?,?,?,?,?,?,?,?,?,?)""",values)
        finally:
            con.close()

    def recent_jobs(self, limit: int=50) -> list[dict[str,Any]]:
        limit=max(1,min(int(limit),200))
        rows=self.conn.execute("SELECT id,kind,label,status,created_at,started_at,finished_at,progress,detail,result_json FROM jobs ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
        keys=['id','kind','label','status','created_at','started_at','finished_at','progress','detail','result_json'];out=[]
        for row in rows:
            item=dict(zip(keys,row))
            try:item['result']=json.loads(item.pop('result_json') or '{}')
            except Exception:item['result']={};item.pop('result_json',None)
            out.append(item)
        return out

    def close(self) -> None:
        self.conn.close()
