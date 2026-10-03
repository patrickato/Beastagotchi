"""Creature finding F5, Core side: `BeastCore._sync_temperament` publishes the active Beast's
heritage temperament to canonical state, and never leaves a previous Beast's values live
(ADR-0008 / ADR-0009: stale data must never be shown as live).

These cover the production synchronisation path that the PersonalityEngine tests do not: the roster
lookup, active-id caching, switching Beasts, the empty / invalid-id guards, exception behaviour, and
that a real axis value of 0 survives (it is not coerced to neutral). `_sync_temperament` only uses
`self.state`, `self.roster` and `self._temperament_beast_id`, so it is exercised against a real
`StateRegistry` and a fake roster via the unbound method — no database or async loop required.
"""
from __future__ import annotations

import types

from beastcore.core import BeastCore
from beastcore.heritage import TEMPERAMENT_AXES
from beastcore.roster import BeastRosterError
from beastcore.state import StateRegistry


def _parent(**axes):
    """A `roster.get()`-shaped parent whose explicit temperament overrides lineage defaults."""
    return {"lineage_id": "standard", "identity": {"traits": {"temperament": dict(axes)}}}


class FakeRoster:
    def __init__(self, beasts):
        self.beasts = dict(beasts)
        self.calls = 0

    def get(self, beast_id):
        self.calls += 1
        try:
            return self.beasts[beast_id]
        except KeyError:
            raise BeastRosterError("Beast not found")


def _core(beasts, active):
    state = StateRegistry()
    if active is not None:
        state.update_many("progression", {"progression.beast.id": active}, priority=87)
    return types.SimpleNamespace(state=state, roster=FakeRoster(beasts), _temperament_beast_id=None)


def _set_active(core, beast_id):
    core.state.update_many("progression", {"progression.beast.id": beast_id}, priority=87)


def _temp(core, axis):
    return core.state.get("beast.temperament." + axis)


def test_publishes_active_beast_temperament():
    core = _core({"A": _parent(curiosity=90, focus=20, boldness=70, nocturnal=10, social=40)}, "A")
    BeastCore._sync_temperament(core)
    assert _temp(core, "curiosity") == 90
    assert _temp(core, "focus") == 20
    assert _temp(core, "boldness") == 70
    assert core._temperament_beast_id == "A"
    # The whole declared contract is published, not just the four axes the engine reads.
    for axis in TEMPERAMENT_AXES:
        assert _temp(core, axis) is not None


def test_switch_overwrites_previous_beast_no_stale():
    core = _core(
        {
            "A": _parent(curiosity=95, focus=95, boldness=95, nocturnal=95, social=95),
            "B": _parent(curiosity=5, focus=5, boldness=5, nocturnal=5, social=5),
        },
        "A",
    )
    BeastCore._sync_temperament(core)
    assert _temp(core, "curiosity") == 95
    _set_active(core, "B")
    BeastCore._sync_temperament(core)
    # B's values, not A's -- no stale data survives the switch (ADR-0008).
    assert _temp(core, "curiosity") == 5
    assert _temp(core, "boldness") == 5
    assert core._temperament_beast_id == "B"


def test_empty_active_id_clears_to_neutral():
    core = _core({"A": _parent(curiosity=95, focus=95, boldness=95, nocturnal=95, social=95)}, "A")
    BeastCore._sync_temperament(core)
    assert _temp(core, "curiosity") == 95
    _set_active(core, "")  # no active Beast
    BeastCore._sync_temperament(core)
    # A's 95 must not linger; neutral (50) is the honest "no temperament".
    for axis in TEMPERAMENT_AXES:
        assert _temp(core, axis) == 50
    assert core._temperament_beast_id == ""


def test_lookup_failure_clears_to_neutral_without_raising():
    core = _core({"A": _parent(curiosity=95, focus=95, boldness=95, nocturnal=95, social=95)}, "A")
    BeastCore._sync_temperament(core)
    assert _temp(core, "curiosity") == 95
    _set_active(core, "ghost")  # not in the roster -> roster.get raises BeastRosterError
    BeastCore._sync_temperament(core)  # must not propagate the exception
    for axis in TEMPERAMENT_AXES:
        assert _temp(core, axis) == 50


def test_zero_axis_is_preserved_not_coerced_to_neutral():
    core = _core({"A": _parent(curiosity=0, focus=0, boldness=0, nocturnal=0, social=0)}, "A")
    BeastCore._sync_temperament(core)
    # 0 is a valid heritage value (0..100); it must publish as 0, never neutral 50 (F5/P2).
    assert _temp(core, "curiosity") == 0
    assert _temp(core, "boldness") == 0


def test_unchanged_active_id_is_a_hot_path_noop():
    core = _core({"A": _parent(curiosity=70, focus=70, boldness=70, nocturnal=70, social=70)}, "A")
    BeastCore._sync_temperament(core)
    assert core.roster.calls == 1
    # Same active id on the next tick: no second roster lookup, no recompute.
    BeastCore._sync_temperament(core)
    assert core.roster.calls == 1
