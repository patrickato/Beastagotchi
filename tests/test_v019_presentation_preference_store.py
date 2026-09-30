from __future__ import annotations

import json
import threading

from beastui.presentation_preferences import (
    PREFERENCE_SCHEMA_VERSION,
    PresentationPreferenceStore,
)


def test_preference_store_round_trip_is_atomic_private_and_bounded(tmp_path):
    path = tmp_path / 'ui' / 'preferences.json'
    store = PresentationPreferenceStore(path, clock=lambda: 1000.0)
    row = store.write({
        'theme': 'classic',
        'face_profile': 'builtin',
        'renderers': {'recon': 'radar'},
        'ignored_future_or_hostile_key': 'not-persisted',
    })
    assert row['changed'] is True
    assert store.read()['theme'] == 'classic'
    assert 'ignored_future_or_hostile_key' not in json.loads(path.read_text())
    assert (path.stat().st_mode & 0o777) == 0o600
    assert not list(path.parent.glob('*.tmp'))
    assert store.metadata()['schema_version'] == PREFERENCE_SCHEMA_VERSION


def test_preference_store_preserves_backups_and_change_gates_identical_payload(tmp_path):
    path = tmp_path / 'preferences.json'
    store = PresentationPreferenceStore(path, backup_keep=2, clock=lambda: 1000.0)
    first = store.write({'theme': 'classic'})
    same = store.write({'theme': 'classic'}, create_backup=True)
    second = store.write({'theme': 'blackice'}, create_backup=True)
    third = store.write({'theme': 'hunter'}, create_backup=True)
    fourth = store.write({'theme': 'lcars'}, create_backup=True)

    assert first['changed'] is True
    assert same['changed'] is False
    assert second['backup']
    assert third['backup']
    assert fourth['backup']
    backups = sorted(path.parent.joinpath('backups').glob('preferences-*.json'))
    assert len(backups) == 2
    assert store.read()['theme'] == 'lcars'


def test_preference_store_malformed_file_falls_back_without_destroying_it(tmp_path):
    path = tmp_path / 'preferences.json'
    path.write_text('{broken-json')
    store = PresentationPreferenceStore(path)
    assert store.read() == {}
    assert path.read_text() == '{broken-json'


def test_preference_store_serializes_concurrent_writers_to_complete_json(tmp_path):
    path = tmp_path / 'preferences.json'
    store = PresentationPreferenceStore(path)
    errors = []

    def writer(n):
        try:
            for i in range(20):
                store.write({'theme': f'theme-{n}-{i}', 'renderers': {'recon': 'radar'}})
        except Exception as exc:  # pragma: no cover - assertion captures unexpected races
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(n,)) for n in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert errors == []
    data = json.loads(path.read_text())
    assert data['theme'].startswith('theme-')
    assert data['renderers'] == {'recon': 'radar'}
