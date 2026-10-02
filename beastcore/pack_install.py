from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from .packs import clean_manifest, PackManifestError


class PackInstallError(RuntimeError):
    pass


_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


class PackInstallManager:
    """Transactional install/rollback for *verified, inert* Beast Packs.

    "Installed" here means copied into Beast's managed installed-pack registry.
    This class never executes pack code, installs OS/Python dependencies, enables
    a plugin, restarts a service, or changes display ownership. Activation is a
    later, pack-type-specific security boundary.
    """

    def __init__(
        self,
        state,
        *,
        staged_root: str | Path = "/var/lib/beastagotchi/packs/staged",
        installed_root: str | Path = "/var/lib/beastagotchi/packs/installed",
        transactions_root: str | Path = "/var/lib/beastagotchi/packs/transactions",
        clock=time.time,
    ) -> None:
        self.state = state
        self.staged_root = Path(staged_root)
        self.installed_root = Path(installed_root)
        self.transactions_root = Path(transactions_root)
        self.clock = clock

    @staticmethod
    def _safe_id(pack_id: str) -> str:
        value = str(pack_id or "").strip().lower()
        if not _ID_RE.fullmatch(value):
            raise PackInstallError("invalid Beast Pack id")
        return value

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            obj = json.loads(path.read_text())
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}

    def _pack_dir(self, root: Path, pack_id: str) -> Path:
        pack_id = self._safe_id(pack_id)
        base = root.resolve()
        path = (base / pack_id).resolve()
        if path.parent != base:
            raise PackInstallError("pack path escaped managed root")
        return path

    def _manifest(self, root: Path, pack_id: str) -> tuple[Path, dict[str, Any]]:
        path = self._pack_dir(root, pack_id)
        fp = path / "manifest.json"
        if not fp.is_file():
            raise PackInstallError(f"manifest missing for pack {pack_id}")
        try:
            row = clean_manifest(json.loads(fp.read_text()), source_path=str(fp))
        except (PackManifestError, json.JSONDecodeError) as exc:
            raise PackInstallError(f"invalid manifest: {type(exc).__name__}: {exc}") from exc
        if row["id"] != pack_id:
            raise PackInstallError("manifest id does not match managed directory")
        return path, row

    @staticmethod
    def _version_key(value: Any) -> tuple[int, ...] | None:
        raw = str(value or "").strip()
        if not raw:
            return None
        nums = re.findall(r"\d+", raw)
        return tuple(int(x) for x in nums[:8]) if nums else None

    @staticmethod
    def _compare_versions(a: tuple[int, ...], b: tuple[int, ...]) -> int:
        n = max(len(a), len(b))
        aa = a + (0,) * (n - len(a))
        bb = b + (0,) * (n - len(b))
        return (aa > bb) - (aa < bb)

    def _compatibility(self, manifest: dict[str, Any]) -> tuple[list[str], list[str], list[dict[str, Any]]]:
        blockers: list[str] = []
        warnings: list[str] = []
        checks: list[dict[str, Any]] = []
        comp = manifest.get("compatibility") if isinstance(manifest.get("compatibility"), dict) else {}
        targets = (
            ("beast", self.state.get("system.beast_version"), comp.get("beast_min"), comp.get("beast_max")),
            ("pwnagotchi", self.state.get("pwnagotchi.version"), comp.get("pwnagotchi_min"), comp.get("pwnagotchi_max")),
        )
        for label, current, minimum, maximum in targets:
            if not minimum and not maximum:
                continue
            cur = self._version_key(current)
            lo = self._version_key(minimum)
            hi = self._version_key(maximum)
            row = {"target": label, "current": current, "min": minimum or "", "max": maximum or "", "ok": True}
            if cur is None:
                row["ok"] = False
                blockers.append(f"cannot verify {label} version compatibility")
            if cur is not None and lo is not None and self._compare_versions(cur, lo) < 0:
                row["ok"] = False
                blockers.append(f"{label} {current} is below required {minimum}")
            if cur is not None and hi is not None and self._compare_versions(cur, hi) > 0:
                row["ok"] = False
                blockers.append(f"{label} {current} is above supported {maximum}")
            if (minimum and lo is None) or (maximum and hi is None):
                warnings.append(f"{label} compatibility bound could not be parsed numerically")
            checks.append(row)
        return blockers, warnings, checks

    def _catalog_sets(self) -> tuple[set[str], set[str]]:
        installed: set[str] = set()
        enabled: set[str] = set()
        for row in self.state.get("packs.items", []) or []:
            if not isinstance(row, dict):
                continue
            pid = str(row.get("id") or "").strip()
            if not pid:
                continue
            if row.get("origin") != "staged":
                installed.add(pid)
            if row.get("enabled"):
                enabled.add(pid)
        try:
            for fp in self.installed_root.glob("*/manifest.json"):
                installed.add(fp.parent.name)
        except Exception:
            pass
        return installed, enabled

    def plan_install(self, pack_id: str) -> dict[str, Any]:
        pack_id = self._safe_id(pack_id)
        staged, manifest = self._manifest(self.staged_root, pack_id)
        staged_state = self._read_json(staged / "state.json")
        blockers: list[str] = []
        warnings: list[str] = []
        if str(staged_state.get("state") or "").lower() != "verified":
            blockers.append("pack must be verified in staging before install")
        capabilities = set(self.state.get("capabilities.present", []) or [])
        installed, enabled = self._catalog_sets()
        missing_caps = sorted(set(manifest.get("capabilities") or []) - capabilities)
        missing_deps = sorted(set(manifest.get("dependencies") or []) - installed)
        enabled_conflicts = sorted(set(manifest.get("conflicts") or []) & enabled)
        if missing_caps:
            blockers.append("missing capabilities: " + ", ".join(missing_caps))
        if missing_deps:
            blockers.append("missing dependencies: " + ", ".join(missing_deps))
        if enabled_conflicts:
            blockers.append("enabled conflicts: " + ", ".join(enabled_conflicts))
        compatibility_blockers, compatibility_warnings, compatibility_checks = self._compatibility(manifest)
        blockers.extend(compatibility_blockers)
        warnings.extend(compatibility_warnings)

        dest = self._pack_dir(self.installed_root, pack_id)
        current = None
        if dest.is_dir():
            try:
                _, current = self._manifest(self.installed_root, pack_id)
            except PackInstallError as exc:
                blockers.append(f"existing installed copy is invalid: {exc}")
        if manifest.get("permissions"):
            warnings.append("declared permissions will require a separate activation review")
        if manifest.get("services") or manifest.get("restart_services"):
            warnings.append("declared services are not started/restarted by registry installation")
        if manifest.get("background_service"):
            warnings.append("background service remains inactive until a future activation transaction")

        return {
            "allowed": not blockers,
            "operation": "pack.install",
            "pack": manifest,
            "staged_path": str(staged),
            "destination": str(dest),
            "is_update": current is not None,
            "current": current,
            "blockers": blockers,
            "warnings": warnings,
            "missing_capabilities": missing_caps,
            "missing_dependencies": missing_deps,
            "enabled_conflicts": enabled_conflicts,
            "compatibility_checks": compatibility_checks,
            "rescue_snapshot_required": current is not None,
            "activation_included": False,
            "service_restart_included": False,
            "probation": "structural registry verification only",
        }

    @staticmethod
    def _tree_digest(root: Path) -> dict[str, Any]:
        h = hashlib.sha256()
        count = 0
        total = 0
        for fp in sorted(root.rglob("*")):
            if not fp.is_file():
                continue
            rel = str(fp.relative_to(root)).replace(os.sep, "/")
            fh = hashlib.sha256()
            with fp.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    fh.update(chunk)
            size = fp.stat().st_size
            h.update(rel.encode() + b"\0" + fh.hexdigest().encode() + b"\0")
            count += 1
            total += size
        return {"sha256": h.hexdigest(), "file_count": count, "size_bytes": total}

    def verify_installed(self, pack_id: str, *, expected_transaction: str | None = None) -> dict[str, Any]:
        pack_id = self._safe_id(pack_id)
        path, manifest = self._manifest(self.installed_root, pack_id)
        state = self._read_json(path / "state.json")
        blockers = []
        if str(state.get("state") or "").lower() not in {"installed", "disabled", "enabled"}:
            blockers.append("installed state marker is missing or invalid")
        if expected_transaction and state.get("installed_transaction_id") != expected_transaction:
            blockers.append("installed transaction marker does not match")
        digest = self._tree_digest(path)
        return {
            "ok": not blockers,
            "pack": manifest,
            "state": state,
            "path": str(path),
            "digest": digest,
            "blockers": blockers,
        }

    def _transaction_path(self, transaction_id: str) -> Path:
        raw = Path(str(transaction_id or "").strip()).name
        if not raw or not raw.startswith("pack-"):
            raise PackInstallError("invalid pack transaction id")
        root = self.transactions_root.resolve()
        path = (root / raw).resolve()
        if path.parent != root:
            raise PackInstallError("transaction path escaped managed root")
        return path

    def _journal_write(self, txn_dir: Path, row: dict[str, Any]) -> None:
        fp = txn_dir / "transaction.json"
        tmp = txn_dir / ".transaction.json.tmp"
        tmp.write_text(json.dumps(row, indent=2, sort_keys=True, default=str) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(fp)

    def history(self, limit: int = 30) -> list[dict[str, Any]]:
        rows = []
        try:
            dirs = sorted(self.transactions_root.glob("pack-*"), key=lambda p: p.stat().st_mtime, reverse=True)
        except Exception:
            dirs = []
        for path in dirs[:max(1, min(int(limit), 100))]:
            row = self._read_json(path / "transaction.json")
            if row:
                row["rollback_payload_retained"] = (path / "previous").is_dir()
                rows.append(row)
        return rows

    def _prune_old_payloads(self, keep: int = 3) -> None:
        rows = self.history(100)
        retained = 0
        for row in rows:
            tid = str(row.get("id") or "")
            if not tid:
                continue
            path = self._transaction_path(tid)
            previous = path / "previous"
            if not previous.is_dir():
                continue
            retained += 1
            if retained <= keep:
                continue
            shutil.rmtree(previous, ignore_errors=True)
            row["rollback_payload_pruned_at"] = float(self.clock())
            self._journal_write(path, row)

    def install(self, pack_id: str) -> dict[str, Any]:
        plan = self.plan_install(pack_id)
        if not plan["allowed"]:
            raise PackInstallError("; ".join(plan["blockers"]))
        pack_id = self._safe_id(pack_id)
        now = float(self.clock())
        txn_id = f"pack-{time.strftime('%Y%m%d-%H%M%S', time.localtime(now))}-{uuid.uuid4().hex[:8]}"
        self.transactions_root.mkdir(parents=True, exist_ok=True)
        self.installed_root.mkdir(parents=True, exist_ok=True)
        txn_dir = self._transaction_path(txn_id)
        txn_dir.mkdir(mode=0o700)
        dest = self._pack_dir(self.installed_root, pack_id)
        staged = self._pack_dir(self.staged_root, pack_id)
        incoming = self.installed_root / f".incoming-{txn_id}"
        previous = txn_dir / "previous"
        had_previous = dest.is_dir()

        journal: dict[str, Any] = {
            "schema": 1,
            "id": txn_id,
            "kind": "pack.install",
            "pack_id": pack_id,
            "version": plan["pack"].get("version"),
            "started_at": now,
            "status": "applying",
            "had_previous": had_previous,
            "plan": plan,
            "activation_performed": False,
            "service_restart_performed": False,
        }
        self._journal_write(txn_dir, journal)

        try:
            if had_previous:
                shutil.copytree(dest, previous)
                journal["previous_digest"] = self._tree_digest(previous)
                self._journal_write(txn_dir, journal)

            if incoming.exists():
                shutil.rmtree(incoming)
            shutil.copytree(staged, incoming)
            state = self._read_json(incoming / "state.json")
            state.update({
                "schema": 1,
                "state": "installed",
                "enabled": False,
                "installed_at": now,
                "installed_transaction_id": txn_id,
                "activation_state": "inactive",
            })
            (incoming / "state.json").write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
            os.chmod(incoming / "state.json", 0o600)
            # Validate the exact copy that will become live registry state.
            manifest = clean_manifest(json.loads((incoming / "manifest.json").read_text()), source_path=str(incoming / "manifest.json"))
            if manifest["id"] != pack_id:
                raise PackInstallError("incoming manifest changed pack identity")

            if dest.exists():
                shutil.rmtree(dest)
            os.replace(incoming, dest)
            verification = self.verify_installed(pack_id, expected_transaction=txn_id)
            if not verification["ok"]:
                raise PackInstallError("; ".join(verification["blockers"]))

            journal.update({
                "status": "installed",
                "completed_at": float(self.clock()),
                "installed_digest": verification["digest"],
                "probation": {
                    "ok": True,
                    "type": "structural",
                    "note": "registry integrity verified; no pack code was activated",
                },
            })
            self._journal_write(txn_dir, journal)
            self._prune_old_payloads()
            return {
                "ok": True,
                "installed": True,
                "enabled": False,
                "activation_performed": False,
                "transaction_id": txn_id,
                "pack": verification["pack"],
                "path": str(dest),
                "verification": verification,
                "rollback_available": had_previous,
            }
        except Exception as exc:
            try:
                if incoming.exists():
                    shutil.rmtree(incoming)
                if dest.exists():
                    shutil.rmtree(dest)
                if previous.is_dir():
                    shutil.copytree(previous, dest)
                journal["automatic_rollback"] = {
                    "attempted": True,
                    "restored_previous": previous.is_dir(),
                    "ok": previous.is_dir() or not had_previous,
                }
            except Exception as rollback_exc:
                journal["automatic_rollback"] = {
                    "attempted": True,
                    "ok": False,
                    "error": f"{type(rollback_exc).__name__}: {rollback_exc}",
                }
            journal.update({
                "status": "failed",
                "failed_at": float(self.clock()),
                "error": f"{type(exc).__name__}: {exc}",
            })
            self._journal_write(txn_dir, journal)
            raise PackInstallError(journal["error"]) from exc

    def plan_rollback(self, transaction_id: str) -> dict[str, Any]:
        txn_dir = self._transaction_path(transaction_id)
        journal = self._read_json(txn_dir / "transaction.json")
        blockers = []
        if not journal:
            blockers.append("transaction not found")
            return {"allowed": False, "operation": "pack.rollback", "transaction_id": transaction_id, "blockers": blockers}
        if journal.get("status") != "installed":
            blockers.append(f"transaction is not rollback-eligible ({journal.get('status') or 'unknown'})")
        pack_id = self._safe_id(str(journal.get("pack_id") or ""))
        dest = self._pack_dir(self.installed_root, pack_id)
        current_state = self._read_json(dest / "state.json") if dest.is_dir() else {}
        if current_state.get("installed_transaction_id") != transaction_id:
            blockers.append("a newer/different installed transaction is active for this pack")
        if journal.get("had_previous") and not (txn_dir / "previous").is_dir():
            blockers.append("rollback payload has been pruned")
        return {
            "allowed": not blockers,
            "operation": "pack.rollback",
            "transaction_id": transaction_id,
            "pack_id": pack_id,
            "had_previous": bool(journal.get("had_previous")),
            "blockers": blockers,
            "warnings": ["Rollback changes only the inert installed-pack registry; no services are restarted."],
        }

    def rollback(self, transaction_id: str) -> dict[str, Any]:
        plan = self.plan_rollback(transaction_id)
        if not plan["allowed"]:
            raise PackInstallError("; ".join(plan["blockers"]))
        txn_dir = self._transaction_path(transaction_id)
        journal = self._read_json(txn_dir / "transaction.json")
        pack_id = plan["pack_id"]
        dest = self._pack_dir(self.installed_root, pack_id)
        previous = txn_dir / "previous"
        current_digest = self._tree_digest(dest) if dest.is_dir() else None

        if dest.exists():
            shutil.rmtree(dest)
        if previous.is_dir():
            shutil.copytree(previous, dest)
            restored = self.verify_installed(pack_id)
        else:
            restored = {"ok": True, "removed_new_install": True}

        journal.update({
            "status": "rolled_back",
            "rolled_back_at": float(self.clock()),
            "pre_rollback_digest": current_digest,
            "rollback_result": restored,
        })
        self._journal_write(txn_dir, journal)
        return {
            "ok": bool(restored.get("ok")),
            "rolled_back": True,
            "transaction_id": transaction_id,
            "pack_id": pack_id,
            "restored_previous": previous.is_dir(),
            "removed_new_install": not previous.is_dir(),
            "verification": restored,
        }
