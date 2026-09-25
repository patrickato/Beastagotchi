from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import tomllib
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

_PLUGIN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")

# Beast itself depends on this adapter. It can be serviced explicitly from SSH,
# but should never disappear because someone casually tapped a toggle.
PROTECTED_PLUGINS = {"beast_bridge"}
# These plugins are known to own/draw the Pwnagotchi display. Beast can catalog
# them, but enabling them while Beast UI owns the panel creates competing writers.
DISPLAY_OWNERS = {"theme_manager", "fancygotchi"}


@dataclass
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class PluginBrokerError(RuntimeError):
    pass


class PluginBroker:
    """Transactional mutation layer for Pwnagotchi plugin enable/disable.

    The broker deliberately delegates the actual config mutation to Pwnagotchi's
    supported CLI instead of rewriting its main TOML itself. Beast snapshots the
    relevant config, verifies the resulting state, restarts/observes Pwnagotchi,
    and rolls the exact snapshot back on failure.

    It is intentionally *not* an HTTP API. A separate authenticated ActionBroker
    will decide who may request these operations.
    """

    def __init__(
        self,
        *,
        config_path: str = "/etc/pwnagotchi/config.toml",
        conf_d: str = "/etc/pwnagotchi/conf.d",
        custom_plugins: str = "/etc/pwnagotchi/custom-plugins",
        snapshot_root: str = "/var/lib/beastagotchi/config-snapshots",
        pwnagotchi_cli: str | None = None,
        runner: Callable[[list[str]], CommandResult] | None = None,
        service_active: Callable[[str], bool] | None = None,
        service_restart: Callable[[str], CommandResult] | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.config_path = Path(config_path)
        self.conf_d = Path(conf_d)
        self.custom_plugins = Path(custom_plugins)
        self.snapshot_root = Path(snapshot_root)
        self.pwnagotchi_cli = pwnagotchi_cli or shutil.which("pwnagotchi") or "/usr/local/bin/pwnagotchi"
        self.runner = runner or self._run
        self.service_active = service_active or self._service_active
        self.service_restart = service_restart or self._service_restart
        self.sleep = sleep
        self.clock = clock

    @staticmethod
    def _run(cmd: list[str]) -> CommandResult:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=90, check=False)
        return CommandResult(int(p.returncode), p.stdout or "", p.stderr or "")

    @staticmethod
    def _service_active(unit: str) -> bool:
        p = subprocess.run(["systemctl", "is-active", "--quiet", unit], timeout=8, check=False)
        return p.returncode == 0

    @staticmethod
    def _service_restart(unit: str) -> CommandResult:
        p = subprocess.run(["systemctl", "restart", unit], text=True, capture_output=True, timeout=60, check=False)
        return CommandResult(int(p.returncode), p.stdout or "", p.stderr or "")

    @staticmethod
    def _safe_name(name: str) -> str:
        value = str(name or "").strip()
        if not _PLUGIN_RE.fullmatch(value):
            raise PluginBrokerError("invalid plugin name")
        return value

    def _config(self) -> dict[str, Any]:
        try:
            obj = tomllib.loads(self.config_path.read_text(errors="replace"))
            return obj if isinstance(obj, dict) else {}
        except Exception as exc:
            raise PluginBrokerError(f"cannot parse Pwnagotchi config: {type(exc).__name__}") from exc

    def _plugin_opts(self, name: str) -> dict[str, Any] | None:
        cfg = self._config()
        main = cfg.get("main") if isinstance(cfg, dict) else None
        plugins = main.get("plugins") if isinstance(main, dict) else None
        row = plugins.get(name) if isinstance(plugins, dict) else None
        return row if isinstance(row, dict) else None

    def current_enabled(self, name: str) -> bool | None:
        name = self._safe_name(name)
        opts = self._plugin_opts(name)
        return bool(opts.get("enabled", False)) if opts is not None else None

    def installed_or_configured(self, name: str) -> bool:
        name = self._safe_name(name)
        if self._plugin_opts(name) is not None:
            return True
        return (self.custom_plugins / f"{name}.py").is_file()

    def plan_toggle(
        self,
        name: str,
        enabled: bool,
        *,
        beast_ui_active: bool | None = None,
        owner_override: bool = False,
        expert_mode: bool = False,
    ) -> dict[str, Any]:
        name = self._safe_name(name)
        current = self.current_enabled(name)
        exists = self.installed_or_configured(name)
        display_conflict = name.lower().replace("-", "_") in {x.replace("-", "_") for x in DISPLAY_OWNERS}
        protected = name.lower().replace("-", "_") in {x.replace("-", "_") for x in PROTECTED_PLUGINS}
        if beast_ui_active is None:
            beast_ui_active = self.service_active("beast-ui.service")
        technical_blockers: list[str] = []
        policy_blockers: list[str] = []
        warnings: list[str] = []
        if not exists:
            technical_blockers.append("plugin is not installed/configured")
        if protected and not enabled:
            policy_blockers.append("protected Beast bridge cannot be disabled from Plugin Manager")
        if enabled and display_conflict and beast_ui_active:
            policy_blockers.append("legacy display plugin conflicts with active Beast UI display ownership")
        if display_conflict:
            warnings.append("legacy display-owner plugin; Beast isolates its UI output")
        owner_override_available = bool(policy_blockers) and not technical_blockers
        owner_override_executed = bool(
            owner_override_available and bool(owner_override) and bool(expert_mode)
        )
        effective_policy_blockers = [] if owner_override_executed else list(policy_blockers)
        blockers = [*technical_blockers, *effective_policy_blockers]
        if bool(owner_override) and policy_blockers and not expert_mode:
            warnings.append("owner override requested but Expert Mode is not enabled")
        if owner_override_executed:
            warnings.append("owner override accepted; managed support/compatibility policy is being bypassed")
        return {
            "plugin": name,
            "current_enabled": current,
            "requested_enabled": bool(enabled),
            "installed_or_configured": exists,
            "protected": protected,
            "display_conflict": display_conflict,
            "beast_ui_active": bool(beast_ui_active),
            "restart_required": current is not None and current != bool(enabled),
            "technical_blockers": technical_blockers,
            "policy_blockers": policy_blockers,
            "overridden_policy_blockers": list(policy_blockers) if owner_override_executed else [],
            "owner_override_requested": bool(owner_override),
            "owner_override_available": owner_override_available,
            "owner_override_executed": owner_override_executed,
            "expert_mode": bool(expert_mode),
            "managed_allowed": not technical_blockers and not policy_blockers,
            "blockers": blockers,
            "warnings": warnings,
            "allowed": not blockers,
            "no_change": current is not None and current == bool(enabled),
        }

    @staticmethod
    def _sha256(path: Path) -> str | None:
        try:
            h = hashlib.sha256()
            with path.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            return h.hexdigest()
        except OSError:
            return None

    def snapshot(self, *, reason: str, plugin: str) -> Path:
        self.snapshot_root.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(self.clock()))
        dest = self.snapshot_root / f"{stamp}-{uuid.uuid4().hex[:8]}-{plugin}"
        dest.mkdir(mode=0o700)
        manifest: dict[str, Any] = {
            "created_at": self.clock(),
            "reason": reason,
            "plugin": plugin,
            "files": [],
        }
        if self.config_path.is_file():
            target = dest / "config.toml"
            shutil.copy2(self.config_path, target)
            manifest["files"].append({"kind": "config", "source": str(self.config_path), "name": target.name, "sha256": self._sha256(target)})
        if self.conf_d.is_dir():
            drop = dest / "conf.d"
            drop.mkdir(mode=0o700)
            for src in sorted(self.conf_d.glob("*.toml")):
                target = drop / src.name
                shutil.copy2(src, target)
                manifest["files"].append({"kind": "dropin", "source": str(src), "name": f"conf.d/{src.name}", "sha256": self._sha256(target)})
        (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        os.chmod(dest / "manifest.json", 0o600)
        return dest

    def restore(self, snapshot: Path) -> None:
        snapshot = Path(snapshot)
        manifest_path = snapshot / "manifest.json"
        if not manifest_path.is_file():
            raise PluginBrokerError("snapshot manifest missing")
        manifest = json.loads(manifest_path.read_text())
        rows = manifest.get("files") or []
        config_src = snapshot / "config.toml"
        if config_src.is_file():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(config_src, self.config_path)
        # Restore the complete TOML drop-in set as it existed at snapshot time.
        expected = {Path(str(r.get("name"))).name for r in rows if r.get("kind") == "dropin"}
        self.conf_d.mkdir(parents=True, exist_ok=True)
        for current in self.conf_d.glob("*.toml"):
            if current.name not in expected:
                current.unlink()
        drop = snapshot / "conf.d"
        if drop.is_dir():
            for src in drop.glob("*.toml"):
                shutil.copy2(src, self.conf_d / src.name)

    def _verify_enabled(self, name: str, expected: bool) -> bool:
        actual = self.current_enabled(name)
        return actual is not None and actual is bool(expected)

    def toggle(
        self,
        name: str,
        enabled: bool,
        *,
        restart: bool = True,
        observe_seconds: float = 2.0,
        owner_override: bool = False,
        expert_mode: bool = False,
    ) -> dict[str, Any]:
        plan = self.plan_toggle(
            name,
            enabled,
            owner_override=owner_override,
            expert_mode=expert_mode,
        )
        if not plan["allowed"]:
            raise PluginBrokerError("; ".join(plan["blockers"]))
        if plan["no_change"]:
            return {"ok": True, "changed": False, "rolled_back": False, "plan": plan, "snapshot": None}

        snapshot = self.snapshot(reason="plugin.toggle", plugin=plan["plugin"])
        action = "enable" if enabled else "disable"
        command = [self.pwnagotchi_cli, "plugins", action, plan["plugin"]]
        cli = self.runner(command)
        result: dict[str, Any] = {
            "ok": False,
            "changed": True,
            "rolled_back": False,
            "plan": plan,
            "snapshot": str(snapshot),
            "command": command,
            "cli": {"returncode": cli.returncode, "stdout": cli.stdout[-2000:], "stderr": cli.stderr[-2000:]},
        }
        try:
            if cli.returncode != 0:
                raise PluginBrokerError(f"Pwnagotchi plugin CLI returned {cli.returncode}")
            if not self._verify_enabled(plan["plugin"], bool(enabled)):
                raise PluginBrokerError("config verification did not match requested enabled state")
            if restart:
                sr = self.service_restart("pwnagotchi.service")
                result["restart"] = {"returncode": sr.returncode, "stdout": sr.stdout[-1000:], "stderr": sr.stderr[-1000:]}
                if sr.returncode != 0:
                    raise PluginBrokerError("Pwnagotchi restart failed")
                self.sleep(max(0.0, float(observe_seconds)))
                if not self.service_active("pwnagotchi.service"):
                    raise PluginBrokerError("Pwnagotchi failed post-change health observation")
            result["ok"] = True
            result["final_enabled"] = self.current_enabled(plan["plugin"])
            return result
        except Exception as exc:
            # Any failure after taking a snapshot restores the exact config/drop-in
            # set and restarts Pwnagotchi so the running state follows the rollback.
            rollback_error = None
            try:
                self.restore(snapshot)
                rr = self.service_restart("pwnagotchi.service") if restart else CommandResult(0)
                if restart:
                    self.sleep(max(0.0, min(float(observe_seconds), 2.0)))
                if rr.returncode != 0 or (restart and not self.service_active("pwnagotchi.service")):
                    rollback_error = "rollback config restored but Pwnagotchi health did not recover"
            except Exception as rb_exc:
                rollback_error = f"rollback failed: {type(rb_exc).__name__}: {rb_exc}"
            result["rolled_back"] = rollback_error is None
            result["rollback_error"] = rollback_error
            result["error"] = f"{type(exc).__name__}: {exc}"
            result["final_enabled"] = self.current_enabled(plan["plugin"])
            return result
