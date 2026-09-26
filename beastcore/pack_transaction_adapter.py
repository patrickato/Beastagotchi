from __future__ import annotations

from typing import Any

from .pack_install import PackInstallError, PackInstallManager
from .transactions import TransactionContext


class PackInstallTransactionAdapter:
    """Adapt the proven Pack installer to Beast's shared Transaction Engine.

    The existing PackInstallManager remains the mutation authority during this
    migration stage.  It still creates its own rescue copy, inner journal,
    structural verification and automatic rollback.  This adapter adds the
    common outer transaction lifecycle/provenance without weakening those
    safeguards.  Once the shared engine is proven in production, duplicated
    Pack-specific orchestration can be retired deliberately rather than all at
    once.
    """

    def __init__(self, manager: PackInstallManager) -> None:
        self.manager = manager

    @staticmethod
    def _pack_id(ctx: TransactionContext) -> str:
        return str(ctx.request.get("id") or "").strip()

    def subject(self, request: dict[str, Any]) -> str:
        return f"pack:{str(request.get('id') or '').strip()}"

    def plan(self, ctx: TransactionContext) -> dict[str, Any]:
        return self.manager.plan_install(self._pack_id(ctx))

    def prepare(self, ctx: TransactionContext) -> dict[str, Any]:
        pack_id = self._pack_id(ctx)
        history = self.manager.history(100)
        baseline_ids = [str(row.get("id")) for row in history if row.get("id")]
        current = None
        try:
            current = self.manager.verify_installed(pack_id)
        except Exception:
            # A first install legitimately has no current installed copy.
            current = None
        return {
            "ok": True,
            "pack_id": pack_id,
            "baseline_inner_transaction_ids": baseline_ids,
            "current_installed": current,
        }

    def _new_inner_row(self, ctx: TransactionContext) -> dict[str, Any] | None:
        prepared = ctx.data.get("prepare") if isinstance(ctx.data.get("prepare"), dict) else {}
        before = set(prepared.get("baseline_inner_transaction_ids") or [])
        pack_id = self._pack_id(ctx)
        for row in self.manager.history(100):
            if str(row.get("id") or "") in before:
                continue
            if str(row.get("pack_id") or "") != pack_id:
                continue
            return row
        return None

    def apply(self, ctx: TransactionContext) -> dict[str, Any]:
        pack_id = self._pack_id(ctx)
        try:
            result = self.manager.install(pack_id)
            return {
                "ok": bool(result.get("ok")),
                "pack_id": pack_id,
                "inner_transaction_id": result.get("transaction_id"),
                "inner_status": "installed" if result.get("ok") else "unknown",
                "install_result": result,
                "mutation_started": True,
            }
        except PackInstallError as exc:
            inner = self._new_inner_row(ctx)
            automatic = inner.get("automatic_rollback") if isinstance(inner, dict) else None
            return {
                "ok": False,
                "pack_id": pack_id,
                "error": f"PackInstallError: {exc}",
                "inner_transaction_id": inner.get("id") if isinstance(inner, dict) else None,
                "inner_status": inner.get("status") if isinstance(inner, dict) else None,
                "inner_automatic_rollback": automatic,
                "mutation_started": inner is not None,
            }

    def probation(self, ctx: TransactionContext) -> dict[str, Any]:
        applied = ctx.data.get("apply") if isinstance(ctx.data.get("apply"), dict) else {}
        inner_id = str(applied.get("inner_transaction_id") or "")
        if not inner_id:
            return {"ok": False, "error": "Pack install did not return an inner transaction id"}
        verification = self.manager.verify_installed(self._pack_id(ctx), expected_transaction=inner_id)
        return {
            "ok": bool(verification.get("ok")),
            "type": "structural",
            "inner_transaction_id": inner_id,
            "verification": verification,
        }

    def verify(self, ctx: TransactionContext) -> dict[str, Any]:
        applied = ctx.data.get("apply") if isinstance(ctx.data.get("apply"), dict) else {}
        inner_id = str(applied.get("inner_transaction_id") or "")
        if not inner_id:
            return {"ok": False, "error": "missing inner Pack transaction id"}
        verification = self.manager.verify_installed(self._pack_id(ctx), expected_transaction=inner_id)
        return {
            "ok": bool(verification.get("ok")),
            "inner_transaction_id": inner_id,
            "verification": verification,
        }

    def commit(self, ctx: TransactionContext) -> dict[str, Any]:
        applied = ctx.data.get("apply") if isinstance(ctx.data.get("apply"), dict) else {}
        return {
            "ok": True,
            "pack_id": self._pack_id(ctx),
            "inner_transaction_id": applied.get("inner_transaction_id"),
            "note": "Shared transaction committed after Pack install structural verification",
        }

    def rollback(self, ctx: TransactionContext) -> dict[str, Any]:
        applied = ctx.data.get("apply") if isinstance(ctx.data.get("apply"), dict) else {}
        inner_id = str(applied.get("inner_transaction_id") or "")

        # If the inner installer itself failed, first trust only its durable
        # automatic-rollback evidence.  Do not claim success merely because an
        # exception was caught by the outer engine.
        if applied.get("ok") is False:
            auto = applied.get("inner_automatic_rollback")
            if isinstance(auto, dict):
                if auto.get("ok") is True:
                    return {
                        "ok": True,
                        "pack_id": self._pack_id(ctx),
                        "inner_transaction_id": inner_id or None,
                        "restored_by": "inner_automatic_rollback",
                        "inner_automatic_rollback": auto,
                    }
                return {
                    "ok": False,
                    "pack_id": self._pack_id(ctx),
                    "inner_transaction_id": inner_id or None,
                    "error": str(auto.get("error") or "inner Pack automatic rollback failed"),
                    "inner_automatic_rollback": auto,
                }
            if not applied.get("mutation_started"):
                return {
                    "ok": True,
                    "pack_id": self._pack_id(ctx),
                    "inner_transaction_id": None,
                    "restored_by": "no_mutation_detected",
                }
            return {
                "ok": False,
                "pack_id": self._pack_id(ctx),
                "inner_transaction_id": inner_id or None,
                "error": "Pack mutation started but no verified rollback result is available",
            }

        # A successful inner install that later fails outer probation/verification
        # is reversed through the existing proven Pack rollback implementation.
        if not inner_id:
            return {"ok": False, "error": "cannot roll back Pack install without inner transaction id"}
        try:
            result = self.manager.rollback(inner_id)
        except PackInstallError as exc:
            return {
                "ok": False,
                "pack_id": self._pack_id(ctx),
                "inner_transaction_id": inner_id,
                "error": f"PackInstallError: {exc}",
            }
        return {
            "ok": bool(result.get("ok")),
            "pack_id": self._pack_id(ctx),
            "inner_transaction_id": inner_id,
            "restored_by": "inner_pack_rollback",
            "rollback_result": result,
        }
