from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable


PREFERENCE_SCHEMA_VERSION = 1
DEFAULT_PREFERENCE_PATH = Path('/var/lib/beastagotchi/ui/preferences.json')
PREFERENCE_KEYS = (
    'theme',
    'face_profile',
    'animation_profile',
    'renderers',
    'theme_options',
    'dashboard_widgets',
    'custom_boards',
    'context_decks',
    'active_context_deck',
    'palette_overrides',
    'correlation_keys',
)


class PresentationPreferenceError(ValueError):
    pass


class PresentationPreferenceStore:
    """One atomic persistence contract for Beast presentation preferences.

    Dynamic catalog validation (installed themes/faces/apps/etc.) remains with
    the caller because that truth depends on the current runtime. This store owns
    the file contract: allowed keys, schema identity, atomicity, backups,
    generation/signature and concurrent writers.
    """

    def __init__(
        self,
        path: str | Path = DEFAULT_PREFERENCE_PATH,
        *,
        backup_keep: int = 12,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.path = Path(path)
        self.backup_keep = max(0, min(int(backup_keep), 50))
        self.clock = clock
        self._lock = threading.RLock()
        self._generation = 0

    @staticmethod
    def _clean_payload(value: dict[str, Any] | None) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise PresentationPreferenceError('presentation preferences must be a JSON object')
        return {key: deepcopy(value[key]) for key in PREFERENCE_KEYS if key in value}

    @staticmethod
    def _serialize(value: dict[str, Any]) -> bytes:
        return (json.dumps(value, indent=2, sort_keys=True, default=str) + '\n').encode('utf-8')

    @staticmethod
    def _digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def read(self) -> dict[str, Any]:
        with self._lock:
            try:
                raw = self.path.read_bytes()
                obj = json.loads(raw.decode('utf-8'))
                return self._clean_payload(obj)
            except FileNotFoundError:
                return {}
            except (OSError, UnicodeError, json.JSONDecodeError, PresentationPreferenceError):
                # Preserve existing BeastUI behavior: a malformed/missing visual
                # preference file never prevents the safe defaults from booting.
                return {}

    def signature(self) -> tuple[int, int] | None:
        try:
            st = self.path.stat()
            return int(st.st_mtime_ns), int(st.st_size)
        except OSError:
            return None

    def fingerprint(self) -> str | None:
        try:
            return self._digest(self.path.read_bytes())
        except OSError:
            return None

    def metadata(self) -> dict[str, Any]:
        return {
            'schema_version': PREFERENCE_SCHEMA_VERSION,
            'path': str(self.path),
            'generation': self._generation,
            'signature': self.signature(),
            'fingerprint': self.fingerprint(),
        }

    def _backup_locked(self) -> Path | None:
        if self.backup_keep <= 0 or not self.path.is_file():
            return None
        bdir = self.path.parent / 'backups'
        bdir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime('%Y%m%d-%H%M%S', time.localtime(float(self.clock())))
        # Same-second writes are possible from Studio/TFT. Keep both rather than
        # letting one silently replace the other's recovery point.
        candidate = bdir / f'preferences-{stamp}.json'
        if candidate.exists():
            suffix = 1
            while (bdir / f'preferences-{stamp}-{suffix:02d}.json').exists():
                suffix += 1
            candidate = bdir / f'preferences-{stamp}-{suffix:02d}.json'
        candidate.write_bytes(self.path.read_bytes())
        try:
            os.chmod(candidate, 0o600)
        except OSError:
            pass
        backups = sorted(
            bdir.glob('preferences-*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for old in backups[self.backup_keep:]:
            try:
                old.unlink()
            except OSError:
                pass
        return candidate

    def write(
        self,
        value: dict[str, Any],
        *,
        create_backup: bool = False,
    ) -> dict[str, Any]:
        payload = self._clean_payload(value)
        encoded = self._serialize(payload)
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            current = None
            try:
                current = self.path.read_bytes()
            except OSError:
                pass
            if current == encoded:
                return {
                    'changed': False,
                    'generation': self._generation,
                    'fingerprint': self._digest(encoded),
                    'signature': self.signature(),
                    'backup': None,
                }
            backup = self._backup_locked() if create_backup else None
            tmp = self.path.with_name(f'.{self.path.name}.{os.getpid()}.{threading.get_ident()}.tmp')
            try:
                with tmp.open('wb') as fh:
                    fh.write(encoded)
                    fh.flush()
                    os.fsync(fh.fileno())
                os.chmod(tmp, 0o600)
                os.replace(tmp, self.path)
            finally:
                try:
                    tmp.unlink()
                except FileNotFoundError:
                    pass
            self._generation += 1
            return {
                'changed': True,
                'generation': self._generation,
                'fingerprint': self._digest(encoded),
                'signature': self.signature(),
                'backup': str(backup) if backup else None,
            }
