from __future__ import annotations

from typing import Any


LEVELS = {
    "observer": {
        "description": "Read Beast state, history, documentation and records.",
        "capabilities": ["read.state","read.history","read.library","read.logs"],
    },
    "operator": {
        "description": "Perform ordinary allow-listed Beast actions through Action Broker.",
        "capabilities": ["action.services","action.plugins","action.profiles","action.backups","action.hardware"],
    },
    "maintainer": {
        "description": "Change validated configuration and perform repair workflows with rollback.",
        "capabilities": ["config.write","dependencies.manage","repair.execute","files.managed_write"],
    },
    "administrator": {
        "description": "Time-limited owner-authorized administrative session.",
        "capabilities": ["shell.controlled","system.admin","packages.manage"],
    },
}


class OperatorPolicy:
    """Policy description for future local/remote AI operators.

    This does not run a model and does not grant privileges. It defines the
    contract the future Beast Operator must obey: all mutations still travel
    through audited Beast actions/transactions and administrator mode must be
    explicit and time-limited.
    """

    def snapshot(self, active_level: str = "observer") -> dict[str, Any]:
        level = active_level if active_level in LEVELS else "observer"
        allowed: list[str] = []
        order = ["observer","operator","maintainer","administrator"]
        for name in order[: order.index(level) + 1]:
            allowed.extend(LEVELS[name]["capabilities"])
        return {
            "operator.policy.level": level,
            "operator.policy.levels": [{"id": k, **v} for k,v in LEVELS.items()],
            "operator.policy.capabilities": list(dict.fromkeys(allowed)),
            "operator.policy.direct_root": False,
            "operator.policy.mutations_via_action_broker": True,
            "operator.policy.admin_session_required": level == "administrator",
        }
