from __future__ import annotations

from typing import Any

from .presentation_transition import PresentationTransitionPlanner


class ExperienceTryOnPlanner:
    """Build a bounded, auto-rollback TFT preview transaction.

    Planning is read-only. Execution remains deliberately disabled until Gate 1
    off-screen acceptance and the physical Presentation Broker executor are both
    validated.
    """

    def __init__(self, state) -> None:
        self.state = state
        self.presentation = PresentationTransitionPlanner(state)

    def _experience(self, experience_id: str) -> dict[str, Any] | None:
        plan = self.state.get("experience.compiler.plan", {}) or {}
        for row in plan.get("items", []) or []:
            if isinstance(row, dict) and str(row.get("experience_id") or "") == experience_id:
                return row
        return None

    @staticmethod
    def _step(step_id: str, label: str, *, mutates: bool, rollback: str = "") -> dict[str, Any]:
        return {
            "id": step_id,
            "label": label,
            "mutates": bool(mutates),
            "rollback": str(rollback or ""),
        }

    def plan(self, experience_id: str, *, page_id: str = "home", duration_sec: int = 90) -> dict[str, Any]:
        experience_id = str(experience_id or "").strip()
        page_id = str(page_id or "home").strip().lower()
        duration = max(15, min(300, int(duration_sec or 90)))
        row = self._experience(experience_id)

        blockers: list[str] = []
        warnings: list[str] = []
        if row is None:
            blockers.append("compiled Experience plan not found")
            row = {}

        coverage = row.get("page_coverage") if isinstance(row.get("page_coverage"), dict) else {}
        implemented = list(coverage.get("implemented") or [])
        target = row.get("render_target") if isinstance(row.get("render_target"), dict) else {}
        renderer_id = str(row.get("renderer_experience_id") or row.get("experience_id") or "")

        if row and not bool(row.get("ready_for_preview")):
            blockers.append("Experience is not ready for preview")
        if page_id not in implemented:
            blockers.append(f"page renderer unavailable: {page_id}")
        if row and not bool(target.get("native_supported")):
            blockers.append("current display target requires an explicit native Scene variant")
        if row and row.get("mission_requirements_met") is False:
            blockers.append("Mission Pack requirements are not met")

        presentation = self.presentation.plan("beast")
        if not bool(presentation.get("allowed")):
            blockers.extend(str(x) for x in presentation.get("blockers") or [])

        backup = bool(self.state.get("display.handoff.backup_exists", False))
        if not backup and self.presentation.infer_owner() == "beast":
            blockers.append("no visible display rollback backup")

        offscreen_accepted = bool(self.state.get("experience.gate1.offscreen_accepted", False))
        if not offscreen_accepted:
            blockers.append("Gate 1 off-screen Experience acceptance is not recorded")

        physical_executor = bool(self.state.get("presentation.executor_enabled", False))
        if not physical_executor:
            blockers.append("physical Presentation Broker executor remains disabled")

        warnings.extend([
            "TRY ON TFT is temporary and must never persist Experience selection automatically.",
            "Automatic rollback to the previous presentation owner is mandatory unless a later validated flow explicitly confirms adoption.",
            "A successful preview is not equivalent to Gate 1 physical acceptance.",
        ])

        previous_owner = self.presentation.infer_owner()
        steps = [
            self._step(
                "snapshot.current_presentation",
                f"Snapshot current presentation owner ({previous_owner}) and active Experience preferences",
                mutates=False,
            ),
            self._step(
                "verify.rollback",
                "Verify display rollback backup and recovery path before touching ownership",
                mutates=False,
            ),
            self._step(
                "presentation.acquire_beast",
                "Acquire Beast presentation ownership using the validated Presentation Broker handoff",
                mutates=True,
                rollback=f"Return presentation ownership to {previous_owner}",
            ),
            self._step(
                "experience.preview.ephemeral",
                f"Select {experience_id}:{page_id} in ephemeral preview state only",
                mutates=True,
                rollback="Discard ephemeral Experience preview state",
            ),
            self._step(
                "experience.preview.render",
                f"Render through trusted renderer {renderer_id or '?'} on the native target",
                mutates=False,
            ),
            self._step(
                "probation.observe",
                f"Observe framebuffer/touch/service/thermal health for up to {duration} seconds",
                mutates=False,
            ),
            self._step(
                "verify.preview",
                "Verify Beast Core/UI + Pwnagotchi health, display ownership, touch and renderer output",
                mutates=False,
            ),
            self._step(
                "rollback.required",
                f"Automatically end preview and restore {previous_owner} ownership + prior presentation state",
                mutates=True,
                rollback="Use the preserved display handoff recovery path",
            ),
        ]

        return {
            "schema": 1,
            "operation": "experience.try_on_tft",
            "experience_id": experience_id,
            "page_id": page_id,
            "renderer_experience_id": renderer_id or None,
            "duration_sec": duration,
            "previous_owner": previous_owner,
            "target_owner": "beast",
            "render_target": target,
            "component_refs": dict(row.get("component_refs") or {}),
            "source": dict(row.get("source") or {}),
            "presentation_plan": presentation,
            "steps": steps,
            "warnings": warnings,
            "blockers": list(dict.fromkeys(blockers)),
            "plan_ready": not blockers,
            "executor_enabled": False,
            "execution_allowed": False,
            "auto_rollback_required": True,
            "writes_preferences": False,
            "persists_experience_selection": False,
            "reason": (
                "transaction planning is implemented; execution remains locked until Gate 1 "
                "off-screen acceptance and physical Presentation Broker execution are validated"
            ),
        }
