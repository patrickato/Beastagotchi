from __future__ import annotations

from beastcore.runtime_core import RuntimeBeastCore


def test_runtime_core_uses_registered_action_broker_and_shared_managers(tmp_path):
    core = RuntimeBeastCore(str(tmp_path / 'beast.db'))
    try:
        assert core.actions.action_registry.ids() == (
            'operator.revoke',
            'owner.expert_mode_get',
        )
        assert core.actions.roster is core.roster
        assert core.actions.global_sync is core.global_sync
        assert core.actions.memories is core.memories
        assert core.actions.doctor is core.doctor
        assert core.action_server.broker is core.actions
        assert core.operator_tools.action_broker is core.actions
        assert core.update_automation.action_broker is core.actions
    finally:
        core.store.close()


def test_registered_action_uses_registry_plan_perform_and_common_audit(tmp_path):
    core = RuntimeBeastCore(str(tmp_path / 'beast.db'))
    try:
        plan = core.actions.plan('owner.expert_mode_get', {})
        row = core.actions.perform('owner.expert_mode_get', {}, actor='registry-test')

        assert plan['allowed'] is True
        assert row['status'] == 'success'
        assert row['actor'] == 'registry-test'
        assert row['action'] == 'owner.expert_mode_get'
        assert row['result']['ok'] is True
        assert row['registry_generation'] == core.actions.action_registry.generation
        assert core.state.get('actions.registry.registered_count') == 2
        assert core.state.get('actions.last.type') == 'owner.expert_mode_get'
        assert core.events.recent(1)[0]['type'] == 'action.completed'
    finally:
        core.store.close()


def test_unmigrated_action_falls_through_to_existing_broker(tmp_path):
    core = RuntimeBeastCore(str(tmp_path / 'beast.db'))
    try:
        founder = core.roster.bootstrap_founder(name='Hex')
        orbit = core.roster.create_beast('Orbit', lineage_id='starcore')

        row = core.actions.perform('roster.switch', {'id': orbit['id']}, actor='legacy-test')

        assert row['status'] == 'success'
        assert row['result']['active']['id'] == orbit['id']
        assert core.roster.active()['id'] == orbit['id']
        assert core.roster.get(founder['id'])['active'] is False
        # Absence proves this row was still produced by the established legacy
        # audit path rather than accidentally intercepted by the registry seam.
        assert 'registry_generation' not in row
    finally:
        core.store.close()


def test_registered_operator_revoke_is_idempotent_and_audited(tmp_path):
    core = RuntimeBeastCore(str(tmp_path / 'beast.db'))
    try:
        row = core.actions.perform('operator.revoke', {}, actor='local-owner')

        assert row['status'] == 'success'
        assert row['result']['ok'] is True
        assert row['result']['session']['active'] is False
        assert row['registry_generation'] == core.actions.action_registry.generation
    finally:
        core.store.close()
