from __future__ import annotations

import json
from pathlib import Path


ALLOWED_STATUS = {
    'planned',
    'adapter_available',
    'partially_migrated',
    'canonical',
    'legacy_retained',
    'legacy_removable',
}


def _ledger():
    path = Path(__file__).resolve().parents[1] / 'docs' / 'architecture_migration_ledger.json'
    return json.loads(path.read_text())


def test_architecture_migration_ledger_has_unique_ids_and_known_statuses():
    obj = _ledger()
    rows = obj['items']
    ids = [row['id'] for row in rows]

    assert obj['schema'] == 1
    assert len(ids) == len(set(ids))
    assert set(obj['status_vocabulary']) == ALLOWED_STATUS
    assert all(row['status'] in ALLOWED_STATUS for row in rows)


def test_canonical_migrations_have_runtime_paths_and_evidence():
    rows = _ledger()['items']
    canonical = [row for row in rows if row['status'] == 'canonical']

    assert canonical
    for row in canonical:
        assert row['runtime_path']
        assert row['evidence']


def test_planned_migrations_do_not_pretend_to_have_runtime_implementation():
    rows = _ledger()['items']
    planned = [row for row in rows if row['status'] == 'planned']

    assert planned
    for row in planned:
        assert row['runtime_path'] is None


def test_action_registry_migration_stays_explicitly_partial_until_legacy_dispatch_is_removed():
    rows = {row['id']: row for row in _ledger()['items']}
    action = rows['registry.action_specs']

    assert action['status'] == 'partially_migrated'
    assert 'fallback' in action['legacy_path'].lower()


def test_physical_validation_requirements_are_explicit_booleans():
    for row in _ledger()['items']:
        assert isinstance(row['physical_validation_required'], bool)
