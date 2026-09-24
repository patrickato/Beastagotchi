from __future__ import annotations

import base64
import hashlib
import json
import time
import uuid
import zlib
from typing import Any

from .roster import BeastRoster


class CapsuleError(ValueError):
    pass


class BeastCapsuleCodec:
    """Transport-neutral, bounded Beast Capsule codec.

    BC1 provides canonical JSON + SHA-256 integrity + zlib/base64url transport.
    The digest detects corruption/tampering; it is deliberately not called an
    authentication/signature mechanism.
    """

    schema = 1
    prefix = "BC1."
    qr_prefix = "BCQ1"
    max_json_bytes = 512 * 1024
    max_encoded_chars = 1024 * 1024
    max_frames = 512

    @staticmethod
    def _canonical(obj: Any) -> bytes:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    @classmethod
    def build(
        cls,
        capsule_type: str,
        payload: dict[str, Any],
        *,
        created_at: float | None = None,
        capsule_id: str | None = None,
        producer: dict[str, Any] | None = None,
        privacy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ctype = str(capsule_type or "").strip().lower()
        if not ctype or len(ctype) > 64 or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789._-" for c in ctype):
            raise CapsuleError("invalid capsule type")
        if not isinstance(payload, dict):
            raise CapsuleError("capsule payload must be an object")
        envelope: dict[str, Any] = {
            "schema": cls.schema,
            "capsule_type": ctype,
            "capsule_id": str(capsule_id or ("capsule-" + uuid.uuid4().hex))[:96],
            "created_at": float(time.time() if created_at is None else created_at),
            "producer": dict(producer or {"name": "Beastagotchi"}),
            "privacy": dict(privacy or {}),
            "payload": payload,
        }
        body = cls._canonical(envelope)
        if len(body) > cls.max_json_bytes:
            raise CapsuleError("capsule exceeds maximum JSON size")
        envelope["integrity"] = {
            "algorithm": "sha256",
            "digest": hashlib.sha256(body).hexdigest(),
            "authenticated": False,
        }
        return envelope

    @classmethod
    def verify(cls, envelope: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(envelope, dict):
            raise CapsuleError("capsule must be an object")
        if int(envelope.get("schema") or 0) != cls.schema:
            raise CapsuleError("unsupported capsule schema")
        integrity = envelope.get("integrity")
        if not isinstance(integrity, dict) or integrity.get("algorithm") != "sha256":
            raise CapsuleError("capsule integrity metadata missing")
        expected = str(integrity.get("digest") or "")
        unsigned = dict(envelope)
        unsigned.pop("integrity", None)
        actual = hashlib.sha256(cls._canonical(unsigned)).hexdigest()
        if not expected or expected != actual:
            raise CapsuleError("capsule integrity check failed")
        ctype = str(envelope.get("capsule_type") or "").strip().lower()
        if not ctype:
            raise CapsuleError("capsule type missing")
        if not isinstance(envelope.get("payload"), dict):
            raise CapsuleError("capsule payload missing")
        return envelope

    @classmethod
    def encode(cls, envelope: dict[str, Any]) -> str:
        cls.verify(envelope)
        raw = cls._canonical(envelope)
        packed = zlib.compress(raw, 9)
        token = base64.urlsafe_b64encode(packed).decode("ascii").rstrip("=")
        encoded = cls.prefix + token
        if len(encoded) > cls.max_encoded_chars:
            raise CapsuleError("encoded capsule exceeds maximum size")
        return encoded

    @classmethod
    def decode(cls, encoded: str) -> dict[str, Any]:
        text = str(encoded or "").strip()
        if not text.startswith(cls.prefix):
            raise CapsuleError("unsupported capsule encoding")
        if len(text) > cls.max_encoded_chars:
            raise CapsuleError("encoded capsule exceeds maximum size")
        token = text[len(cls.prefix):]
        try:
            token += "=" * ((4 - len(token) % 4) % 4)
            packed = base64.urlsafe_b64decode(token.encode("ascii"))
        except Exception as exc:
            raise CapsuleError("invalid capsule base64") from exc
        try:
            dec = zlib.decompressobj()
            raw = dec.decompress(packed, cls.max_json_bytes + 1)
            if len(raw) > cls.max_json_bytes or dec.unconsumed_tail:
                raise CapsuleError("capsule decompressed size exceeds maximum")
            raw += dec.flush()
            if len(raw) > cls.max_json_bytes:
                raise CapsuleError("capsule decompressed size exceeds maximum")
        except CapsuleError:
            raise
        except Exception as exc:
            raise CapsuleError("invalid compressed capsule") from exc
        try:
            obj = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise CapsuleError("invalid capsule JSON") from exc
        return cls.verify(obj)

    @classmethod
    def qr_frames(cls, encoded: str, *, max_frame_chars: int = 700) -> list[str]:
        text = str(encoded or "").strip()
        if not text.startswith(cls.prefix):
            raise CapsuleError("QR frames require a BC1 capsule")
        size = max(128, min(2400, int(max_frame_chars)))
        # Reserve ample room for framing metadata.
        payload_size = max(64, size - 64)
        parts = [text[i:i + payload_size] for i in range(0, len(text), payload_size)]
        if not parts:
            parts = [""]
        if len(parts) > cls.max_frames:
            raise CapsuleError("capsule requires too many QR frames")
        session = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
        total = len(parts)
        out = []
        for idx, part in enumerate(parts, 1):
            crc = f"{zlib.crc32(part.encode('utf-8')) & 0xffffffff:08x}"
            out.append(f"{cls.qr_prefix}|{session}|{idx}|{total}|{crc}|{part}")
        return out

    @classmethod
    def reassemble_qr_frames(cls, frames: list[str]) -> str:
        if not isinstance(frames, list) or not frames:
            raise CapsuleError("no QR frames supplied")
        if len(frames) > cls.max_frames:
            raise CapsuleError("too many QR frames")
        session = None
        total = None
        parts: dict[int, str] = {}
        for frame in frames:
            bits = str(frame or "").split("|", 5)
            if len(bits) != 6 or bits[0] != cls.qr_prefix:
                raise CapsuleError("invalid QR frame")
            _, sid, idx_s, total_s, crc, part = bits
            try:
                idx = int(idx_s)
                count = int(total_s)
            except ValueError as exc:
                raise CapsuleError("invalid QR frame index") from exc
            if count < 1 or count > cls.max_frames or idx < 1 or idx > count:
                raise CapsuleError("invalid QR frame range")
            if session is None:
                session, total = sid, count
            if sid != session or count != total:
                raise CapsuleError("QR frames belong to different capsules")
            actual_crc = f"{zlib.crc32(part.encode('utf-8')) & 0xffffffff:08x}"
            if actual_crc != crc:
                raise CapsuleError("QR frame checksum failed")
            prior = parts.get(idx)
            if prior is not None and prior != part:
                raise CapsuleError("conflicting duplicate QR frame")
            parts[idx] = part
        assert total is not None and session is not None
        if len(parts) != total:
            missing = [str(i) for i in range(1, total + 1) if i not in parts]
            raise CapsuleError("missing QR frame(s): " + ",".join(missing[:16]))
        text = "".join(parts[i] for i in range(1, total + 1))
        if hashlib.sha256(text.encode("utf-8")).hexdigest()[:12] != session:
            raise CapsuleError("reassembled QR capsule checksum failed")
        cls.decode(text)
        return text


class BeastCapsuleEngine:
    """Privacy-curated Beast Capsule producer/inspector.

    v0.19 implements lineage export and transport encoding only. Import is
    preview-only; it does not create roster entries or remote ancestry.
    """

    NAMESPACE_KEY = "capsule.namespace_id"

    def __init__(self, store, roster: BeastRoster | None = None, *, beast_version: str = "", clock=time.time) -> None:
        self.store = store
        self.conn = store.conn
        self.roster = roster or BeastRoster(store)
        self.beast_version = str(beast_version or "")
        self.clock = clock

    def _meta_get(self, key: str) -> str:
        row = self.conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row else ""

    def _meta_set(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value)),
            )

    def namespace_id(self, *, create: bool = False) -> str | None:
        value = self._meta_get(self.NAMESPACE_KEY).strip()
        if value:
            return value
        if not create:
            return None
        value = "capsulepub-" + uuid.uuid4().hex
        self._meta_set(self.NAMESPACE_KEY, value)
        return value

    @staticmethod
    def _public_creature_id(namespace: str, creature_id: str) -> str:
        return "creature-" + hashlib.sha256(f"{namespace}|{creature_id}".encode()).hexdigest()[:20]

    def _public_id_map(self, namespace: str) -> dict[str, str]:
        return {
            str(beast["id"]): self._public_creature_id(namespace, str(beast["id"]))
            for beast in self.roster.list()
        }

    @staticmethod
    def _safe_appearance(beast: dict[str, Any]) -> dict[str, Any]:
        appearance = beast.get("appearance") if isinstance(beast.get("appearance"), dict) else {}
        traits = appearance.get("traits") if isinstance(appearance.get("traits"), dict) else {}
        safe_traits: dict[str, Any] = {}
        for key, value in list(traits.items())[:64]:
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe_traits[str(key)[:64]] = value
        out: dict[str, Any] = {}
        if safe_traits:
            out["traits"] = safe_traits
        mutation = appearance.get("mutation")
        if isinstance(mutation, (str, int, float, bool)) or mutation is None:
            if mutation is not None:
                out["mutation"] = mutation
        return out

    def lineage_payload(
        self,
        beast_id: str | None = None,
        *,
        include_name: bool = True,
        include_achievements: bool = False,
        include_appearance: bool = True,
    ) -> dict[str, Any]:
        beast = self.roster.get(str(beast_id)) if beast_id else self.roster.active()
        namespace = self.namespace_id(create=True)
        assert namespace
        id_map = self._public_id_map(namespace)
        public_id = id_map[str(beast["id"])]
        parents = [id_map[x] for x in beast.get("parents") or [] if x in id_map]
        row: dict[str, Any] = {
            "format": "lineage_v1",
            "creature_id": public_id,
            "kind": str(beast.get("kind") or "beast")[:32],
            "lineage": str(beast.get("lineage_id") or "")[:80],
            "generation": int(beast.get("generation") or 0),
            "level": int(beast.get("level") or 1),
            "stage": str(beast.get("stage") or "")[:64],
            "legend": bool(beast.get("legend")),
            "parents": parents,
        }
        if include_name:
            row["name"] = str(beast.get("name") or "")[:64]
        if include_appearance:
            safe_appearance = self._safe_appearance(beast)
            if safe_appearance:
                row["appearance"] = safe_appearance
        if include_achievements:
            row["achievements"] = [
                str(x)[:160] for x in list(beast.get("achievements") or [])[:256] if str(x).strip()
            ]
        row["achievement_count"] = len(beast.get("achievements") or [])
        return row

    def export_lineage(
        self,
        beast_id: str | None = None,
        *,
        include_name: bool = True,
        include_achievements: bool = False,
        include_appearance: bool = True,
        qr_max_chars: int = 700,
    ) -> dict[str, Any]:
        payload = self.lineage_payload(
            beast_id,
            include_name=include_name,
            include_achievements=include_achievements,
            include_appearance=include_appearance,
        )
        envelope = BeastCapsuleCodec.build(
            "lineage",
            payload,
            created_at=float(self.clock()),
            producer={"name": "Beastagotchi", "version": self.beast_version, "format": "beast_capsule_v1"},
            privacy={
                "local_ids_included": False,
                "credentials_included": False,
                "captures_included": False,
                "network_history_included": False,
                "exact_location_included": False,
                "logs_included": False,
                "achievements_included": bool(include_achievements),
                "name_included": bool(include_name),
            },
        )
        encoded = BeastCapsuleCodec.encode(envelope)
        frames = BeastCapsuleCodec.qr_frames(encoded, max_frame_chars=qr_max_chars)
        return {
            "ok": True,
            "capsule_type": "lineage",
            "envelope": envelope,
            "encoded": encoded,
            "encoded_chars": len(encoded),
            "qr": {
                "transport": "animated_qr_text_frames",
                "frame_count": len(frames),
                "max_frame_chars": max(128, min(2400, int(qr_max_chars))),
                "frames": frames,
                "renderer_required": True,
                "renderer_bundled": False,
            },
            "import_performed": False,
        }

    @staticmethod
    def inspect(encoded: str) -> dict[str, Any]:
        envelope = BeastCapsuleCodec.decode(encoded)
        payload = envelope["payload"]
        ctype = str(envelope.get("capsule_type") or "")
        blockers: list[str] = []
        if ctype == "lineage":
            if str(payload.get("format") or "") != "lineage_v1":
                blockers.append("unsupported lineage payload format")
            if not str(payload.get("creature_id") or "").startswith("creature-"):
                blockers.append("lineage creature id missing or invalid")
        return {
            "ok": not blockers,
            "capsule_type": ctype,
            "capsule_id": envelope.get("capsule_id"),
            "created_at": envelope.get("created_at"),
            "producer": envelope.get("producer") or {},
            "privacy": envelope.get("privacy") or {},
            "integrity": envelope.get("integrity") or {},
            "payload": payload,
            "blockers": blockers,
            "import_supported": False,
            "import_performed": False,
        }
