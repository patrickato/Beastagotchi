from __future__ import annotations

import pytest

from beastcore.registry import (
    DuplicateSpecError,
    RegistryError,
    RegistryFrozenError,
    SpecMetadata,
    StaleRegistryCandidateError,
)
from beastcore.spec_registry import (
    ActionSpec,
    ActionSpecRegistry,
    EventSpec,
    EventSpecRegistry,
    SignalSpec,
    SignalSpecRegistry,
)


def test_action_registry_orders_ids_and_exposes_metadata():
    reg = ActionSpecRegistry()
    reg.register(ActionSpec(SpecMetadata('zeta.action'), authority='maintainer', risk='C2'))
    reg.register(ActionSpec(SpecMetadata('alpha.action'), authority='operator', risk='C1'))

    snap = reg.snapshot()

    assert reg.ids() == ('alpha.action', 'zeta.action')
    assert snap['kind'] == 'action'
    assert snap['count'] == 2
    assert [row['id'] for row in snap['items']] == ['alpha.action', 'zeta.action']
    assert snap['items'][0]['authority'] == 'operator'
    assert snap['items'][1]['risk'] == 'C2'


def test_registry_rejects_duplicate_and_post_freeze_direct_registration():
    reg = ActionSpecRegistry()
    reg.register(ActionSpec(SpecMetadata('owner.inspect')))
    with pytest.raises(DuplicateSpecError):
        reg.register(ActionSpec(SpecMetadata('owner.inspect')))

    reg.freeze()
    with pytest.raises(RegistryFrozenError):
        reg.register(ActionSpec(SpecMetadata('owner.other')))


def test_candidate_activation_is_atomic_and_rejects_stale_generation():
    reg = ActionSpecRegistry()
    reg.register(ActionSpec(SpecMetadata('owner.inspect')))
    reg.freeze()

    candidate = reg.build_candidate([
        ActionSpec(SpecMetadata('owner.other')),
    ], merge=True)
    stale = reg.build_candidate([], merge=True)

    generation = reg.activate_candidate(candidate)
    assert generation == reg.generation
    assert reg.ids() == ('owner.inspect', 'owner.other')

    with pytest.raises(StaleRegistryCandidateError):
        reg.activate_candidate(stale)


def test_candidate_rejects_duplicate_incoming_ids_even_when_replacing_active_id():
    reg = ActionSpecRegistry()
    reg.register(ActionSpec(SpecMetadata('owner.inspect')))
    reg.freeze()
    replacement = ActionSpec(SpecMetadata('owner.inspect'))

    with pytest.raises(DuplicateSpecError):
        reg.build_candidate([replacement, replacement], merge=True)


def test_lower_trust_cannot_shadow_core_spec():
    reg = ActionSpecRegistry()
    reg.register(ActionSpec(SpecMetadata('owner.inspect', trust_tier='core')))
    reg.freeze()

    lower = ActionSpec(SpecMetadata(
        'owner.inspect',
        source='community.pack',
        namespace_owner='community.pack',
        trust_tier='verified_declarative',
    ))
    with pytest.raises(RegistryError):
        reg.build_candidate([lower], merge=True)


def test_signal_registry_forbids_privacy_downgrade():
    reg = SignalSpecRegistry()
    reg.register(SignalSpec(
        SpecMetadata('gps.position'),
        value_type='object',
        privacy='sensitive_location',
        publication='never',
    ))
    reg.freeze()

    lower_privacy = SignalSpec(
        SpecMetadata('gps.position'),
        value_type='object',
        privacy='public',
        publication='policy',
    )
    with pytest.raises(RegistryError):
        reg.build_candidate([lower_privacy], merge=True)


def test_event_registry_forbids_privacy_downgrade():
    reg = EventSpecRegistry()
    reg.register(EventSpec(
        SpecMetadata('captures.created'),
        privacy='sensitive_capture',
    ))
    reg.freeze()

    with pytest.raises(RegistryError):
        reg.build_candidate([
            EventSpec(SpecMetadata('captures.created'), privacy='local')
        ], merge=True)


def test_action_registry_executes_registered_plan_and_performer():
    calls = []
    reg = ActionSpecRegistry()
    reg.register(ActionSpec(
        SpecMetadata('demo.action'),
        planner=lambda payload: {
            'allowed': bool(payload.get('ok')),
            'operation': 'demo.action',
            'blockers': [] if payload.get('ok') else ['blocked'],
        },
        performer=lambda payload, actor: calls.append((payload, actor)) or {
            'ok': True,
            'actor': actor,
        },
    ))

    assert reg.plan('demo.action', {'ok': True})['allowed'] is True
    row = reg.perform('demo.action', {'ok': True}, actor='test')
    assert row == {'ok': True, 'actor': 'test'}
    assert calls == [({'ok': True}, 'test')]
