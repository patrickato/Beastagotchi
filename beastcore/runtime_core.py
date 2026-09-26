from __future__ import annotations

from .action_server import LocalActionServer
from .core import BeastCore
from .operator_tools import OperatorToolRegistry
from .registered_actions import RegisteredActionBroker
from .update_automation import UpdateAutomationEngine


class RuntimeBeastCore(BeastCore):
    """Production Core adapter for incremental architecture migration.

    v0.19's existing BeastCore composition root remains intact while the runtime
    can adopt new contracts one seam at a time. This adapter is intentionally
    temporary and should disappear once the migrated services are native members
    of the future composition root.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        actions = RegisteredActionBroker(
            self.state,
            self.store,
            self.events,
            owner_mode=self.owner_mode,
            provider_preferences=self.provider_preferences,
        )
        # Preserve the one-runtime-owner invariant established earlier in this
        # tranche. RegisteredActionBroker may be constructed independently, but
        # the production Core always uses the Core-owned domain managers.
        actions.roster = self.roster
        actions.global_sync = self.global_sync
        actions.memories = self.memories
        actions.doctor = self.doctor
        self.actions = actions

        # Rewire only components that retain an ActionBroker reference. All
        # other BeastCore services remain the exact instances created by base
        # BeastCore.
        self.update_automation = UpdateAutomationEngine(self.state, self.actions)
        self.operator_tools = OperatorToolRegistry(
            self.state,
            self.store,
            self.search,
            self.actions,
        )
        self.api.backup_manager = self.actions.backup_manager
        self.api.operator_tools = self.operator_tools
        self.action_server = LocalActionServer(self.actions)

        self.state.update_many('action_registry', {
            'actions.registry.kind': 'action',
            'actions.registry.generation': self.actions.action_registry.generation,
            'actions.registry.registered_count': len(self.actions.action_registry),
            'actions.registry.migration_mode': 'incremental_fallback',
        }, priority=96)
