from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

from beastcore.events import EventBus
from beastcore.pack_install import PackInstallManager
from beastcore.pack_intake import PackIntakeManager
from beastcore.pack_transaction_adapter import PackInstallTransactionAdapter
from beastcore.registered_actions import RegisteredActionBroker
from beastcore.state import StateRegistry
from beastcore.thread_store import ThreadBoundStore
from beastcore.transactions import FileTransactionJournal, TransactionEngine, TransactionSpec


def _archive(path: Path, version: str) -> None:
    manifest = {
        'id': 'demo-theme',
        'label': 'Demo Theme',
        'version': version,
        'pack_type': 'theme',
        'resource_class': 'none',
        'thermal_class': 'static',
        'dependencies': [],
        'compatibility': {},
    }
    with tarfile.open(path, 'w:gz') as tf:
        for name, body in {
            'demo-theme/manifest.json': json.dumps(manifest).encode(),
            'demo-theme/theme.json': json.dumps({'version': version}).encode(),
        }.items():
            info = tarfile.TarInfo(name)
            info.size = len(body)
            tf.addfile(info, io.BytesIO(body))


def _stage(tmp_path: Path, version: str) -> Path:
    inbox = tmp_path / 'inbox'
    staged = tmp_path / 'staged'
    inbox.mkdir(exist_ok=True)
    archive = inbox / 'demo.tar.gz'
    _archive(archive, version)
    PackIntakeManager(inbox, staged).stage(archive.name, replace=True)
    return staged


def _state() -> StateRegistry:
    state = StateRegistry()
    state.update_many('test', {
        'capabilities.present': [],
        'packs.items': [],
        'system.beast_version': '0.19.0',
        'pwnagotchi.version': '2.9.5.9',
    }, priority=100)
    return state


def _manager(tmp_path: Path, state: StateRegistry, staged: Path, cls=PackInstallManager):
    return cls(
        state,
        staged_root=staged,
        installed_root=tmp_path / 'installed',
        transactions_root=tmp_path / 'pack-tx',
    )


def _engine(tmp_path: Path) -> TransactionEngine:
    return TransactionEngine(FileTransactionJournal(tmp_path / 'shared-tx'))


def test_registered_pack_install_links_action_outer_and_inner_transactions(tmp_path):
    staged = _stage(tmp_path, '1.0')
    state = _state()
    store = ThreadBoundStore(str(tmp_path / 'beast.db'))
    manager = _manager(tmp_path, state, staged)
    engine = _engine(tmp_path)
    broker = RegisteredActionBroker(
        state,
        store,
        EventBus(),
        pack_install_manager=manager,
        transaction_engine=engine,
    )
    try:
        row = broker.perform('pack.install', {'id': 'demo-theme'}, actor='pack-test')

        assert row['status'] == 'success'
        assert row['registry_generation'] == broker.action_registry.generation
        assert row['result']['transaction_status'] == 'committed'
        assert row['result']['transaction_id'].startswith('txn-pack.install-')
        assert row['result']['inner_transaction_id'].startswith('pack-')
        assert manager.verify_installed(
            'demo-theme', expected_transaction=row['result']['inner_transaction_id']
        )['ok'] is True
        outer = engine.journal.get(row['result']['transaction_id'])
        assert outer['status'] == 'committed'
        assert outer['stage_results']['apply']['inner_transaction_id'] == row['result']['inner_transaction_id']
        assert state.get('actions.last.transaction_id') == row['result']['transaction_id']
    finally:
        store.close()


def test_pack_rollback_remains_legacy_action_during_incremental_migration(tmp_path):
    staged = _stage(tmp_path, '1.0')
    state = _state()
    store = ThreadBoundStore(str(tmp_path / 'beast.db'))
    manager = _manager(tmp_path, state, staged)
    broker = RegisteredActionBroker(
        state,
        store,
        EventBus(),
        pack_install_manager=manager,
        transaction_engine=_engine(tmp_path),
    )
    try:
        installed = broker.perform('pack.install', {'id': 'demo-theme'}, actor='pack-test')
        inner_id = installed['result']['inner_transaction_id']
        rolled = broker.perform('pack.rollback', {'transaction_id': inner_id}, actor='pack-test')

        assert installed['status'] == 'success'
        assert rolled['status'] == 'success'
        assert rolled['result']['rolled_back'] is True
        assert 'registry_generation' not in rolled
        assert not (tmp_path / 'installed' / 'demo-theme').exists()
    finally:
        store.close()


class _FailOuterVerifyAdapter(PackInstallTransactionAdapter):
    def verify(self, ctx):
        return {'ok': False, 'error': 'forced outer verification failure'}


def test_outer_verification_failure_uses_inner_pack_rollback_to_restore_previous(tmp_path):
    staged = _stage(tmp_path, '1.0')
    state = _state()
    manager = _manager(tmp_path, state, staged)
    first = manager.install('demo-theme')
    assert first['ok'] is True

    _stage(tmp_path, '2.0')
    adapter = _FailOuterVerifyAdapter(manager)
    engine = _engine(tmp_path)
    spec = TransactionSpec('pack.install', adapter, reversible=True, probation_required=True, verification_required=True)

    row = engine.execute(spec, {'id': 'demo-theme'}, actor='pack-test')

    assert row['status'] == 'rolled_back'
    assert row['stage_results']['rollback']['restored_by'] == 'inner_pack_rollback'
    assert manager.verify_installed('demo-theme')['pack']['version'] == '1.0'


class _FailFirstInstallVerificationManager(PackInstallManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._force_once = True

    def verify_installed(self, pack_id: str, *, expected_transaction: str | None = None):
        if expected_transaction and self._force_once:
            self._force_once = False
            return {
                'ok': False,
                'pack': {'id': pack_id},
                'state': {},
                'path': '',
                'digest': {},
                'blockers': ['forced inner verification failure'],
            }
        return super().verify_installed(pack_id, expected_transaction=expected_transaction)


def test_inner_pack_failure_with_verified_auto_rollback_is_not_double_mutated(tmp_path):
    staged = _stage(tmp_path, '1.0')
    state = _state()
    manager = _manager(tmp_path, state, staged, cls=_FailFirstInstallVerificationManager)
    adapter = PackInstallTransactionAdapter(manager)
    engine = _engine(tmp_path)
    spec = TransactionSpec('pack.install', adapter, reversible=True, probation_required=True, verification_required=True)

    row = engine.execute(spec, {'id': 'demo-theme'}, actor='pack-test')

    assert row['status'] == 'rolled_back'
    rollback = row['stage_results']['rollback']
    assert rollback['restored_by'] == 'inner_automatic_rollback'
    assert rollback['inner_automatic_rollback']['ok'] is True
    assert not (tmp_path / 'installed' / 'demo-theme').exists()
    inner = manager.history()[0]
    assert inner['status'] == 'failed'
    assert inner['automatic_rollback']['ok'] is True
