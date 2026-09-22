from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import time
import urllib.parse
from typing import Any

class LocalAPI:
    """Dependency-free read-only HTTP/WebSocket API for Beast Core."""
    def __init__(self, state, events, store, host: str = "127.0.0.1", port: int = 8090,
                 *, channel_history=None, telemetry=None) -> None:
        self.state = state; self.events = events; self.store = store
        self.channel_history = channel_history; self.telemetry = telemetry
        self.host = host; self.port = port; self.server = None
        self.search_engine = None
        self.operator_policy = None
        self.operator_tools = None
        self.backup_manager = None

    async def start(self) -> None:
        self.server = await asyncio.start_server(self._handle, self.host, self.port)

    async def stop(self) -> None:
        if self.server:
            self.server.close(); await self.server.wait_closed()

    @staticmethod
    def _headers(raw: bytes) -> tuple[str, str, dict[str,str]]:
        lines = raw.decode(errors="replace").split("\r\n")
        method, target, _ = lines[0].split(" ", 2)
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                k,v = line.split(":",1); headers[k.strip().lower()] = v.strip()
        return method, target, headers

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            raw = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=2)
            method, target, headers = self._headers(raw)
            if method != "GET": return await self._reply(writer, 405, {"error":"read-only API"})
            parsed = urllib.parse.urlsplit(target)
            if parsed.path == "/ws" and headers.get("upgrade", "").lower() == "websocket":
                return await self._websocket(writer, headers)
            if parsed.path == "/health":
                state_name = self.state.get("health.core.state", "starting")
                body = {"ok": state_name == "healthy", "state":state_name, **self.state.stats()}
            elif parsed.path == "/state":
                q = urllib.parse.parse_qs(parsed.query); meta = q.get("meta", ["1"])[0] != "0"
                body = self.state.snapshot(meta)
            elif parsed.path == "/events":
                q = urllib.parse.parse_qs(parsed.query)
                try: limit = int(q.get("limit", ["100"])[0])
                except Exception: limit = 100
                include_transient = q.get("transient", ["1"])[0] != "0"
                body = self.events.recent(limit, include_transient=include_transient)
            elif parsed.path == "/live":
                q = urllib.parse.parse_qs(parsed.query)
                try: limit = int(q.get("events", ["24"])[0])
                except Exception: limit = 24
                body = {
                    "state": self.state.snapshot(False),
                    "events": self.events.recent(limit, include_transient=False),
                    "state_stats": self.state.stats(),
                }
            elif parsed.path == "/history-batch":
                q = urllib.parse.parse_qs(parsed.query)
                raw_keys = q.get("keys", [""])[0]
                keys = [x for x in raw_keys.split(",") if x][:64]
                try: limit = int(q.get("limit", ["64"])[0])
                except Exception: limit = 64
                histories = {key:self.store.query_samples(key, 0.0, limit) for key in keys}
                body = {"histories": histories}
                if self.telemetry is not None:
                    body["telemetry"] = self.telemetry.snapshot(keys)
                try: channel_limit = int(q.get("channel", ["0"])[0])
                except Exception: channel_limit = 0
                if channel_limit and self.channel_history is not None:
                    body["channel_history"] = self.channel_history.recent(channel_limit)
                try: point_limit = int(q.get("expedition_points", ["0"])[0])
                except Exception: point_limit = 0
                if point_limit:
                    eid = str(self.state.get("expedition.id") or "")
                    body["expedition"] = self.store.expedition_detail(eid, point_limit) if eid else None
            elif parsed.path == "/telemetry":
                if self.telemetry is None:
                    body = []
                else:
                    q = urllib.parse.parse_qs(parsed.query)
                    raw = q.get("keys", [""])[0]
                    keys = [x for x in raw.split(",") if x] or None
                    body = self.telemetry.snapshot(keys)
            elif parsed.path == "/actions":
                q = urllib.parse.parse_qs(parsed.query)
                try: limit = int(q.get("limit", ["50"])[0])
                except Exception: limit = 50
                items = self.store.recent_actions(limit)
                body = {"count": len(items), "items": items}
            elif parsed.path == "/platform-bundle":
                body = {
                    "library": self.store.library_summary(12),
                    "jobs": {"items": self.store.recent_jobs(20)},
                    "incidents": {"items": self.store.recent_incidents(20), "open_count": int(self.state.get("incidents.open_count",0) or 0)},
                    "overview": {
                        "state": self.state.get("overview.state"),
                        "attention": self.state.get("overview.attention", []) or [],
                        "cards": self.state.get("overview.cards", []) or [],
                    },
                    "topology": {
                        "nodes": self.state.get("topology.nodes", []) or [],
                        "edges": self.state.get("topology.edges", []) or [],
                        "failures": self.state.get("topology.failures", []) or [],
                    },
                    "services": self.state.get("platform.services", []) or [],
                    "displays": {
                        "framebuffers": self.state.get("display.framebuffers", []) or [],
                        "outputs": self.state.get("display.outputs", []) or [],
                    },
                    "containers": {
                        "available": bool(self.state.get("containers.runtime.available")),
                        "runtime": self.state.get("containers.runtime"),
                        "items": self.state.get("containers.items", []) or [],
                    },
                    "backups": {
                        "count": int(self.state.get("backups.count",0) or 0),
                        "items": self.state.get("backups.items", []) or [],
                        "last": self.state.get("backups.last"),
                    },
                }
            elif parsed.path == "/library-item":
                q = urllib.parse.parse_qs(parsed.query)
                doc_id = str(q.get("id", [""])[0])
                row = self.store.get_library_document(doc_id) if doc_id else None
                body = row if row is not None else {"error":"not found"}
            elif parsed.path == "/library":
                q = urllib.parse.parse_qs(parsed.query)
                query = str(q.get("q", [""])[0])
                try: limit = int(q.get("limit", ["50"])[0])
                except Exception: limit = 50
                try: offset = int(q.get("offset", ["0"])[0])
                except Exception: offset = 0
                rows = self.store.search_library(query, limit, offset)
                summary = self.store.library_summary(6)
                body = {"query":query,"offset":offset,"count":len(rows),"total":summary.get("total",0),"text_indexed":summary.get("text_indexed",0),"items":rows}
            elif parsed.path == "/incidents":
                q=urllib.parse.parse_qs(parsed.query)
                status=str(q.get("status", [""])[0]) or None
                try:limit=int(q.get("limit",["50"])[0])
                except Exception:limit=50
                items=self.store.recent_incidents(limit,status)
                body={"count":len(items),"open_count":sum(1 for x in items if x.get("status")=="open"),"items":items}
            elif parsed.path == "/jobs":
                q = urllib.parse.parse_qs(parsed.query)
                try: limit = int(q.get("limit", ["50"])[0])
                except Exception: limit = 50
                items = self.store.recent_jobs(limit)
                body = {"count":len(items),"items":items}
            elif parsed.path == "/search":
                q = urllib.parse.parse_qs(parsed.query)
                query = str(q.get("q", [""])[0])
                try: limit = int(q.get("limit", ["12"])[0])
                except Exception: limit = 12
                body = self.search_engine.search(query, limit) if self.search_engine is not None else {"query":query,"count":0,"groups":{}}
            elif parsed.path == "/backup-inspect":
                q = urllib.parse.parse_qs(parsed.query)
                name = str(q.get("name", [""])[0])
                if not name:
                    return await self._reply(writer, 400, {"error":"missing backup name"})
                if self.backup_manager is None:
                    body = {"ok":False,"error":"backup manager unavailable"}
                else:
                    try: body = self.backup_manager.inspect(name)
                    except Exception as exc: body = {"ok":False,"error":f"{type(exc).__name__}: {exc}"}
            elif parsed.path == "/operator-tools":
                body = self.operator_tools.catalog("observer") if self.operator_tools is not None else {"active_level":"observer","count":0,"items":[]}
            elif parsed.path == "/operator-policy":
                level = str(self.state.get("operator.policy.level") or "observer")
                body = self.operator_policy.snapshot(level) if self.operator_policy is not None else {}
            elif parsed.path == "/plugins":
                items = list(self.state.get("plugins.catalog", []) or [])
                body = {
                    "count": len(items),
                    "enabled_count": int(self.state.get("plugins.enabled_count", 0) or 0),
                    "integrated_count": int(self.state.get("plugins.integrated_count", 0) or 0),
                    "items": items,
                }
            elif parsed.path == "/history":
                q = urllib.parse.parse_qs(parsed.query)
                key = q.get("key", [""])[0]
                if not key: return await self._reply(writer, 400, {"error":"missing key"})
                try: since = float(q.get("since", ["0"])[0])
                except Exception: since = 0.0
                try: limit = int(q.get("limit", ["1000"])[0])
                except Exception: limit = 1000
                body = {"key":key,"samples":self.store.query_samples(key,since,limit)}
            elif parsed.path in {"/encounters","/beastdex"}:
                q = urllib.parse.parse_qs(parsed.query)
                try: limit = int(q.get("limit", ["24"])[0])
                except Exception: limit = 24
                try: offset = int(q.get("offset", ["0"])[0])
                except Exception: offset = 0
                query = str(q.get("q", [""])[0])
                if parsed.path == "/beastdex" or query or offset:
                    rows=self.store.search_encounters(query,limit,offset)
                    summary=self.store.encounter_summary(6)
                    body={"count":len(rows),"total":summary.get("total",0),"vendor_count":summary.get("vendor_count",0),"query":query,"offset":offset,"items":rows}
                else:
                    body = self.store.encounter_summary(limit)
            elif parsed.path == "/capture-vault":
                q=urllib.parse.parse_qs(parsed.query)
                try:limit=int(q.get("limit",["24"])[0])
                except Exception:limit=24
                body=self.store.capture_summary(limit)
            elif parsed.path == "/achievements":
                q = urllib.parse.parse_qs(parsed.query)
                kind = str(q.get("kind", ["achievements"])[0]).lower()
                if kind == "awards":
                    items = list(self.state.get('progression.awards.catalog', []) or [])
                    body = {
                        'kind':'awards',
                        'count':len(items),
                        'unlocked_count':sum(1 for r in items if isinstance(r,dict) and r.get('unlocked')),
                        'items':items,
                    }
                else:
                    items = list(self.state.get('progression.achievements.catalog', []) or [])
                    body = {
                        'kind':'achievements',
                        'count':len(items),
                        'unlocked_count':sum(1 for r in items if isinstance(r,dict) and r.get('unlocked')),
                        'rarity_counts':self.state.get('progression.achievements.rarity_counts', {}) or {},
                        'items':items,
                    }
            elif parsed.path == "/expeditions":
                q = urllib.parse.parse_qs(parsed.query)
                try: limit = int(q.get("limit", ["20"])[0])
                except Exception: limit = 20
                items = self.store.recent_expeditions(limit)
                body = {"count": len(items), "active_id": self.state.get("expedition.id"), "items": items}
            elif parsed.path == "/expedition":
                q = urllib.parse.parse_qs(parsed.query)
                expedition_id = str(q.get("id", [self.state.get("expedition.id") or ""])[0])
                if not expedition_id:
                    return await self._reply(writer, 400, {"error":"missing id"})
                try: limit = int(q.get("point_limit", ["2000"])[0])
                except Exception: limit = 2000
                body = self.store.expedition_detail(expedition_id, limit)
                if body is None:
                    return await self._reply(writer, 404, {"error":"expedition not found"})
            else:
                return await self._reply(writer, 404, {"error":"not found","endpoints":["/health","/state","/live","/events","/history","/history-batch","/telemetry","/platform-bundle","/library","/library-item","/incidents","/jobs","/search","/backup-inspect","/operator-policy","/operator-tools","/plugins","/actions","/encounters","/beastdex","/capture-vault","/achievements","/expeditions","/expedition","/ws"]})
            await self._reply(writer, 200, body)
        except Exception:
            try: await self._reply(writer, 400, {"error":"bad request"})
            except Exception: pass

    async def _websocket(self, writer: asyncio.StreamWriter, headers: dict[str,str]) -> None:
        key = headers.get("sec-websocket-key")
        if not key:
            return await self._reply(writer, 400, {"error":"missing websocket key"})
        accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        head = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
        ).encode()
        writer.write(head); await writer.drain()
        q = self.events.subscribe()
        try:
            await self._ws_send(writer, {"type":"hello","ts":time.time(),"state":self.state.snapshot(False)})
            while True:
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=20.0)
                    payload = {"type":"event","event":{
                        "id":ev.id,"ts":ev.ts,"type":ev.type,"source":ev.source,"severity":ev.severity,"data":ev.data
                    }}
                    if ev.type == "state.changed" and isinstance(ev.data.get("keys"), list):
                        payload["patch"] = self.state.snapshot_keys(ev.data["keys"], include_meta=False)
                    await self._ws_send(writer, payload)
                except asyncio.TimeoutError:
                    await self._ws_send(writer, {"type":"heartbeat","ts":time.time(),"state_seq":self.state.stats()["seq"]})
        except Exception:
            pass
        finally:
            self.events.unsubscribe(q)
            try: writer.close(); await writer.wait_closed()
            except Exception: pass

    @staticmethod
    async def _ws_send(writer: asyncio.StreamWriter, obj: Any) -> None:
        data = json.dumps(obj, separators=(",",":"), default=str).encode()
        n = len(data)
        if n < 126:
            head = bytes([0x81, n])
        elif n <= 65535:
            head = bytes([0x81, 126]) + n.to_bytes(2,"big")
        else:
            head = bytes([0x81, 127]) + n.to_bytes(8,"big")
        writer.write(head + data); await writer.drain()

    async def _reply(self, writer, status: int, body: Any) -> None:
        data = json.dumps(body, separators=(",", ":"), default=str).encode()
        reason = {200:"OK",400:"Bad Request",404:"Not Found",405:"Method Not Allowed"}.get(status,"OK")
        head = f"HTTP/1.1 {status} {reason}\r\nContent-Type: application/json\r\nContent-Length: {len(data)}\r\nConnection: close\r\n\r\n".encode()
        writer.write(head + data); await writer.drain(); writer.close(); await writer.wait_closed()
