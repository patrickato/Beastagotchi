from __future__ import annotations

import time
import uuid
from typing import Any

from .actions import ActionBroker
from .registry import RegistryError, SpecMetadata
from .spec_registry import ActionSpec, ActionSpecRegistry


class RegisteredActionBroker(ActionBroker):
    """Incremental typed-registry seam over the proven v0.19 ActionBroker.

    Only explicitly migrated actions execute through ActionSpecRegistry. Every
    unmigrated action falls through to the existing allow-listed dispatcher.
    This lets Beast move one action at a time without a flag-day rewrite.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.action_registry = ActionSpecRegistry()
        self._register_bootstrap_actions()
        self.action_registry.freeze()

    def _register_bootstrap_actions(self) -> None:
        self.action_registry.register(ActionSpec(
            SpecMetadata(
                'owner.expert_mode_get',
                source='beastcore.registered_actions',
                namespace_owner='core',
                trust_tier='core',
            ),
            planner=lambda payload: {
                'allowed': True,
                'operation': 'owner.expert_mode_get',
                'state': self.owner_mode.snapshot(),
                'blockers': [],
            },
            performer=lambda payload, actor: {
                'ok': True,
                'state': self.owner_mode.snapshot(),
            },
            authority='observer',
            risk='C0',
            mutation='none',
            verification='immediate_readback',
            tags=('owner', 'introspection'),
        ))
        self.action_registry.register(ActionSpec(
            SpecMetadata(
                'operator.revoke',
                source='beastcore.registered_actions',
                namespace_owner='core',
                trust_tier='core',
            ),
            planner=lambda payload: {
                'allowed': True,
                'operation': 'operator.revoke',
                'current': self.operator_sessions.current(),
                'blockers': [],
            },
            performer=lambda payload, actor: {
                'ok': True,
                'session': self.operator_sessions.revoke(),
            },
            authority='local',
            risk='C0',
            mutation='ephemeral_session',
            verification='immediate_readback',
            tags=('operator', 'session'),
        ))

    def plan(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.action_registry.maybe_get(action) is not None:
            return self.action_registry.plan(action, payload)
        return super().plan(action, payload)

    @staticmethod
    def _target(action: str, requested: dict[str, Any]) -> str:
        if action == 'doctor.known_good_save':
            return 'doctor.patient'
        return str(
            requested.get('name')
            or requested.get('unit')
            or requested.get('target')
            or requested.get('id')
            or requested.get('capability')
            or ''
        )

    def _record_registered_action(
        self,
        *,
        action_id: str,
        started: float,
        actor: str,
        action: str,
        requested: dict[str, Any],
        plan: dict[str, Any],
        result: dict[str, Any],
        status: str,
    ) -> dict[str, Any]:
        finished = time.time()
        row = {
            'id': action_id,
            'ts': started,
            'finished_at': finished,
            'actor': str(actor),
            'action': action,
            'target': self._target(action, requested),
            'status': status,
            'request': requested,
            'plan': plan,
            'result': result,
            'registry_generation': self.action_registry.generation,
        }
        self.store.add_action(row)
        ev = self.events.publish(
            'action.completed',
            'action_broker',
            {
                'id': action_id,
                'action': action,
                'target': row['target'],
                'status': status,
                'registry_generation': self.action_registry.generation,
            },
            'warning' if status not in {'success'} else 'info',
        )
        self.store.add_event(ev)
        self.state.update_many('action_broker', {
            'actions.last.id': action_id,
            'actions.last.type': action,
            'actions.last.target': row['target'],
            'actions.last.status': status,
            'actions.last.finished_at': finished,
            'actions.registry.generation': self.action_registry.generation,
            'actions.registry.registered_count': len(self.action_registry),
        }, priority=95)
        return row

    def perform(self, action: str, payload: dict[str, Any], *, actor: str = 'local') -> dict[str, Any]:
        if self.action_registry.maybe_get(action) is None:
            return super().perform(action, payload, actor=actor)

        action_id = str(uuid.uuid4())
        started = time.time()
        requested = dict(payload or {})
        plan: dict[str, Any] = {}
        try:
            plan = self.action_registry.plan(action, requested)
            if not bool(plan.get('allowed', False)):
                result = {
                    'ok': False,
                    'error': '; '.join(plan.get('blockers') or ['action blocked']),
                }
                status = 'blocked'
            else:
                result = self.action_registry.perform(action, requested, actor=actor)
                status = (
                    'success'
                    if result.get('ok')
                    else 'rolled_back'
                    if result.get('rolled_back')
                    else 'failed'
                )
        except (RegistryError, ValueError) as exc:
            result = {'ok': False, 'error': f'{type(exc).__name__}: {exc}'}
            status = 'failed'
        return self._record_registered_action(
            action_id=action_id,
            started=started,
            actor=actor,
            action=action,
            requested=requested,
            plan=plan,
            result=result,
            status=status,
        )
