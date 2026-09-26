from __future__ import annotations

import time
import uuid
from typing import Any

from .actions import ActionBroker
from .pack_install import PackInstallError, PackInstallManager
from .pack_transaction_adapter import PackInstallTransactionAdapter
from .registry import RegistryError, SpecMetadata
from .spec_registry import ActionSpec, ActionSpecRegistry
from .transactions import TransactionEngine, TransactionError, TransactionSpec


class RegisteredActionBroker(ActionBroker):
    """Incremental typed-registry seam over the proven v0.19 ActionBroker.

    Only explicitly migrated actions execute through ActionSpecRegistry. Every
    unmigrated action falls through to the existing allow-listed dispatcher.
    This lets Beast move one action at a time without a flag-day rewrite.
    """

    def __init__(
        self,
        *args,
        transaction_engine: TransactionEngine | None = None,
        pack_install_manager: PackInstallManager | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if pack_install_manager is not None:
            self.pack_installer = pack_install_manager
        self.transaction_engine = transaction_engine or TransactionEngine()
        self.pack_install_transaction = PackInstallTransactionAdapter(self.pack_installer)
        self.pack_install_transaction_spec = TransactionSpec(
            'pack.install',
            self.pack_install_transaction,
            risk='C2',
            reversible=True,
            probation_required=True,
            verification_required=True,
            authority='maintainer',
            definition_version='1',
            tags=('pack', 'content', 'filesystem'),
        )
        self.action_registry = ActionSpecRegistry()
        self._register_bootstrap_actions()
        self.action_registry.freeze()

    def _perform_pack_install(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        transaction = self.transaction_engine.execute(
            self.pack_install_transaction_spec,
            payload,
            actor=actor,
        )
        txn_status = str(transaction.get('status') or '')
        stage_results = transaction.get('stage_results') if isinstance(transaction.get('stage_results'), dict) else {}
        applied = stage_results.get('apply') if isinstance(stage_results.get('apply'), dict) else {}
        committed = stage_results.get('commit') if isinstance(stage_results.get('commit'), dict) else {}
        inner_id = applied.get('inner_transaction_id') or committed.get('inner_transaction_id')
        return {
            'ok': txn_status == 'committed',
            'rolled_back': txn_status == 'rolled_back',
            'transaction_id': transaction.get('id'),
            'transaction_status': txn_status,
            'inner_transaction_id': inner_id,
            'transaction': transaction,
        }

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
        self.action_registry.register(ActionSpec(
            SpecMetadata(
                'pack.install',
                source='beastcore.registered_actions',
                namespace_owner='core',
                trust_tier='core',
            ),
            planner=lambda payload: self.pack_installer.plan_install(str(payload.get('id') or '')),
            performer=lambda payload, actor: self._perform_pack_install(payload, actor),
            authority='maintainer',
            risk='C2',
            mutation='installed_pack_registry',
            verification='shared_transaction_structural_verify',
            tags=('pack', 'content', 'transaction'),
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
                'transaction_id': result.get('transaction_id'),
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
            'actions.last.transaction_id': result.get('transaction_id'),
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
        except (RegistryError, TransactionError, PackInstallError, ValueError) as exc:
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
