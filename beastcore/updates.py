from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from .update_sources import GitHubReleaseChecker, TrustedSourcePolicy, normalize_repo


POLICIES = ("manual", "notify", "auto_stage", "auto_install")


class UpdatePolicyEngine:
    """Policy + trusted read-only release discovery.

    v0.19 may inspect release metadata from explicit trusted GitHub repositories.
    It still cannot download, stage or install remote updates automatically.
    """

    def __init__(
        self,
        state,
        path: str = "/var/lib/beastagotchi/ui/update_policies.json",
        *,
        cache_path: str = "/var/lib/beastagotchi/ui/update_metadata.json",
        trust_path: str = "/var/lib/beastagotchi/ui/trusted_sources.json",
        checker=None,
        clock=time.time,
        check_interval_sec: float = 3600.0,
    ) -> None:
        self.state = state
        self.path = Path(path)
        self.cache_path = Path(cache_path)
        self.trust = TrustedSourcePolicy(trust_path)
        self.checker = checker or GitHubReleaseChecker()
        self.clock = clock
        self.check_interval_sec = max(300.0, float(check_interval_sec))

    def _policies(self) -> dict[str, str]:
        try:
            obj = json.loads(self.path.read_text())
            raw = obj.get("policies") if isinstance(obj, dict) else {}
            if not isinstance(raw, dict):
                return {}
            return {str(k): str(v) for k, v in raw.items() if str(v) in POLICIES and str(k).strip()}
        except Exception:
            return {}

    def _cache(self) -> dict[str, Any]:
        try:
            obj = json.loads(self.cache_path.read_text())
            return obj if isinstance(obj, dict) else {"schema": 1, "repositories": {}}
        except Exception:
            return {"schema": 1, "repositories": {}}

    def _save_cache(self, obj: dict[str, Any]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.cache_path.with_suffix(self.cache_path.suffix + ".tmp")
        tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(self.cache_path)

    @staticmethod
    def _version_key(value: Any) -> tuple[int, ...] | None:
        nums = re.findall(r"\d+", str(value or ""))
        return tuple(int(x) for x in nums[:8]) if nums else None

    @classmethod
    def _is_newer(cls, available: Any, installed: Any) -> bool | None:
        a = cls._version_key(available)
        b = cls._version_key(installed)
        if a is None or b is None:
            return None
        n = max(len(a), len(b))
        aa = a + (0,) * (n - len(a))
        bb = b + (0,) * (n - len(b))
        return aa > bb

    def _theme_manager(self) -> dict[str, Any] | None:
        for row in self.state.get("plugins.catalog", []) or []:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or "").lower().replace("-", "_")
            if name == "theme_manager":
                return row
        return None

    def tick(self) -> dict[str, Any]:
        policies = self._policies()
        components: list[dict[str, Any]] = []

        def add(cid: str, label: str, version: Any, kind: str, *, source_type: str, source: str = "",
                default_policy: str = "notify", compatible: bool = True, blockers: list[str] | None = None) -> None:
            selected = policies.get(cid, default_policy)
            repo = normalize_repo(source) if source_type == "github_release" else ""
            components.append({
                "id": cid,
                "label": label,
                "kind": kind,
                "installed_version": str(version or "unknown"),
                "available_version": None,
                "update_available": None,
                "policy": selected if selected in POLICIES else default_policy,
                "source_type": source_type,
                "source": source,
                "repository": repo,
                "source_trusted": bool(repo and self.trust.trusted(repo)),
                "compatibility": "compatible" if compatible else "blocked",
                "blockers": list(blockers or []),
                "last_checked_at": None,
                "last_result": "not_checked",
                "verification_available": False,
                "auto_stage_eligible": False,
                "auto_install_eligible": False,
            })

        add("beastagotchi", "Beastagotchi", self.state.get("system.beast_version"),
            "core", source_type="github_release", source="patrickato/Beastagotchi")
        add("pwnagotchi", "Pwnagotchi", self.state.get("pwnagotchi.version"),
            "platform", source_type="github_release", source="jayofelony/pwnagotchi")

        theme = self._theme_manager()
        if theme:
            add("theme_manager", "Korrie71 Theme Manager", theme.get("version"),
                "integration", source_type="github_release", source="Korrie71/pwnagotchi-theme-manager")

        for pack in self.state.get("packs.items", []) or []:
            if not isinstance(pack, dict) or pack.get("origin") == "staged":
                continue
            pid = str(pack.get("id") or "").strip()
            if not pid:
                continue
            source = pack.get("source") if isinstance(pack.get("source"), dict) else {}
            blockers = list(pack.get("blockers") or [])
            add(
                f"pack:{pid}", str(pack.get("label") or pid), pack.get("version"),
                "pack", source_type=str(source.get("type") or "local"),
                source=str(source.get("url") or ""),
                compatible=bool(pack.get("requirements_met", True)),
                blockers=blockers,
            )

        docked = bool(self.state.get("dock.docked", False))
        internet = str(self.state.get("network.internet.state") or "unknown").lower()
        auto_trigger_ready = bool(docked and internet in {"online", "reachable", "up"})
        now = float(self.clock())
        cache = self._cache()
        repos = cache.get("repositories") if isinstance(cache.get("repositories"), dict) else {}
        cache["repositories"] = repos
        checked_now = 0
        errors: list[dict[str, str]] = []

        for row in components:
            repo = str(row.get("repository") or "")
            if row.get("source_type") != "github_release" or not repo:
                row["last_result"] = "local_or_unsupported_source"
                continue
            if not row.get("source_trusted"):
                row["last_result"] = "source_untrusted"
                continue

            key = repo.lower()
            cached = repos.get(key) if isinstance(repos.get(key), dict) else {}
            checked_at = float(cached.get("checked_at") or 0.0)
            # A repository with no previous successful/failed check is always due.
            # Do not make first-check behavior depend on the absolute clock value.
            due = checked_at <= 0.0 or now - checked_at >= self.check_interval_sec
            if auto_trigger_ready and due:
                try:
                    latest = self.checker.latest(repo)
                    cached = {"checked_at": now, "ok": True, "release": latest, "error": None}
                    repos[key] = cached
                    checked_now += 1
                except Exception as exc:
                    cached = {"checked_at": now, "ok": False, "release": cached.get("release"), "error": f"{type(exc).__name__}: {exc}"[:320]}
                    repos[key] = cached
                    errors.append({"repository": repo, "error": cached["error"]})

            release = cached.get("release") if isinstance(cached, dict) and isinstance(cached.get("release"), dict) else None
            row["last_checked_at"] = cached.get("checked_at") if isinstance(cached, dict) else None
            if release:
                available = str(release.get("version") or "")
                row["available_version"] = available or None
                row["update_available"] = self._is_newer(available, row["installed_version"])
                verification = release.get("verification") if isinstance(release.get("verification"), dict) else {}
                row["verification_available"] = bool(verification.get("sha256_path_available"))
                row["release_assets"] = list(release.get("assets") or [])
                row["download_stage_supported"] = row["id"] != "pwnagotchi"
                if cached.get("ok") is False:
                    row["last_result"] = "check_error_cached_release"
                elif row["update_available"] is True:
                    row["last_result"] = "update_available"
                elif row["update_available"] is False:
                    row["last_result"] = "current"
                else:
                    row["last_result"] = "version_unknown"
                row["auto_stage_eligible"] = bool(
                    row["update_available"] is True
                    and row["source_trusted"]
                    and row["verification_available"]
                    and row["compatibility"] == "compatible"
                    and row.get("download_stage_supported")
                    and any(
                        str(a.get("name") or "").lower().endswith((".zip",".tar.gz",".tgz"))
                        and not str(a.get("name") or "").lower().endswith((".sha256",".sha256.txt","_sha256.txt"))
                        for a in row["release_assets"] if isinstance(a,dict)
                    )
                )
                row["auto_install_eligible"] = bool(row["auto_stage_eligible"] and str(row.get("id") or "").startswith("pack:"))
            elif cached.get("ok") is False:
                row["last_result"] = "check_error"
            elif not auto_trigger_ready:
                row["last_result"] = "waiting_for_dock_and_internet"
            else:
                row["last_result"] = "not_checked"

        if checked_now or errors:
            self._save_cache(cache)

        counts = {p: sum(1 for c in components if c.get("policy") == p) for p in POLICIES}
        updates_found = sum(1 for c in components if c.get("update_available") is True)
        trusted_count = sum(1 for c in components if c.get("source_trusted"))
        if checked_now:
            check_state = "checked"
        elif not auto_trigger_ready:
            check_state = "waiting_for_dock_and_internet"
        else:
            check_state = "cached_or_not_due"

        return {
            "updates.components": components,
            "updates.component_count": len(components),
            "updates.update_available_count": updates_found,
            "updates.trusted_component_count": trusted_count,
            "updates.policy_counts": counts,
            "updates.allowed_policies": list(POLICIES),
            "updates.policy_path": str(self.path),
            "updates.cache_path": str(self.cache_path),
            "updates.trusted_repositories": self.trust.repositories(),
            "updates.dock_ready": docked,
            "updates.internet_state": internet,
            "updates.auto_trigger_ready": auto_trigger_ready,
            "updates.check_state": check_state,
            "updates.checked_now_count": checked_now,
            "updates.check_errors": errors,
            "updates.metadata_fetch_enabled": True,
            "updates.download_executor_enabled": True,
            "updates.executor_enabled": True,
            "updates.executor_scope": "verified_staging_plus_inert_beast_pack_transactions",
            "updates.executor_reason": (
                "trusted SHA-256 verified release staging is enabled; automatic transactional install is limited "
                "to inert Beast Packs with rollback, while core/platform integrations remain stage-only"
            ),
        }
