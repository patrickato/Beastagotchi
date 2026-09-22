from __future__ import annotations

import asyncio
import grp
import json
import os
import socket
import struct
from pathlib import Path
from typing import Any


class LocalActionServer:
    """Root-owned, allow-listed local mutation channel.

    Beast Core's public HTTP API remains read-only. Privileged changes use a
    Unix-domain socket whose filesystem permissions restrict access to the
    dedicated ``beastagotchi`` local group. Beast Studio adds its own pairing
    token at the browser boundary, so a browser never talks to this socket
    directly and there is no generic shell/command primitive here.
    """

    def __init__(self, broker, path: str = "/run/beastagotchi/action.sock", group: str = "beastagotchi") -> None:
        self.broker = broker
        self.path = Path(path)
        self.group = group
        self.server: asyncio.AbstractServer | None = None

    async def start(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        self.server = await asyncio.start_unix_server(self._handle, path=str(self.path))
        os.chmod(self.path, 0o660)
        try:
            gid = grp.getgrnam(self.group).gr_gid
            os.chown(self.path, 0, gid)
        except KeyError:
            # Development/source-test systems may not have the production group.
            # Keep the socket root-only rather than weakening permissions.
            os.chmod(self.path, 0o600)

    async def stop(self) -> None:
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    @staticmethod
    def _peer_actor(writer: asyncio.StreamWriter) -> str:
        sock = writer.get_extra_info("socket")
        try:
            raw = sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
            pid, uid, gid = struct.unpack("3i", raw)
            return f"local:uid={uid}:gid={gid}:pid={pid}"
        except Exception:
            return "local:unix"

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        response: dict[str, Any]
        try:
            raw = await asyncio.wait_for(reader.readline(), timeout=3.0)
            if len(raw) > 16_384:
                raise ValueError("request too large")
            req = json.loads(raw.decode("utf-8", errors="strict"))
            if not isinstance(req, dict):
                raise ValueError("request must be object")
            op = str(req.get("op") or "")
            action = str(req.get("action") or "")
            payload = req.get("payload") if isinstance(req.get("payload"), dict) else {}
            if op == "plan":
                plan = await asyncio.to_thread(self.broker.plan, action, payload)
                response = {"ok": True, "op": "plan", "action": action, "plan": plan}
            elif op == "perform":
                actor = self._peer_actor(writer)
                row = await asyncio.to_thread(self.broker.perform, action, payload, actor=actor)
                response = {"ok": row.get("status") == "success", "op": "perform", "action": action, "action_row": row}
            else:
                raise ValueError("unsupported operation")
        except Exception as exc:
            response = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        try:
            writer.write((json.dumps(response, separators=(",", ":"), default=str) + "\n").encode())
            await writer.drain()
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
