"""Drift guard for the consolidated canonical data-key spec (v7).

v1-v6 fragmented the canonical state keys across six files, none of which the code loaded, so the
spec silently drifted from the machine. v7 is the single consolidated spec. These tests enforce,
as ongoing invariants, what the consolidation promised:

- the ``beast`` namespace holds *exactly* what Beast Core produces for a Beast -- both the
  ``PersonalityEngine.tick()`` expression keys and the ADR-0009 temperament axes published by
  ``core._sync_temperament`` -- verified against the real producers, both directions, so the spec
  can neither miss a produced key nor invent an unproduced one (ADR-0008 live-truth);
- no key from any archived v1-v6 spec was dropped (ADR-0007): every one is live, legacy, or deferred;
- keys the code does not produce stay out of the live namespaces.

Only the ``beast`` namespace is producer-verified here; the other namespaces are a faithful
consolidation whose key-level completeness is guarded by ``test_no_prior_key_was_dropped``.
"""
from __future__ import annotations

import json
import types
from pathlib import Path

from beastcore.core import BeastCore
from beastcore.heritage import TEMPERAMENT_AXES
from beastcore.needs import NeedsEngine
from beastcore.personality import PersonalityEngine
from beastcore.roster import BeastRosterError
from beastcore.state import StateRegistry

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "docs" / "Beastagotchi_Canonical_Data_Keys_v7.json").read_text())
NAMESPACES = SPEC["namespaces"]
LEGACY = SPEC["legacy_keys"]
DEFERRED = SPEC["deferred_keys"]
LIVE_KEYS = {k for keys in NAMESPACES.values() for k in keys}
ARCHIVE = ROOT / "docs" / "archive" / "superseded-specs"


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


class _FakeRoster:
    def __init__(self, beasts):
        self.beasts = dict(beasts)

    def get(self, beast_id):
        try:
            return self.beasts[beast_id]
        except KeyError:
            raise BeastRosterError("Beast not found")


def _emitted_beast_keys():
    out = PersonalityEngine(FakeState({}), clock=lambda: 0.0).tick()
    return {k for k in out if k.startswith("beast.")}


def _produced_temperament_keys():
    # Exercise the real producer (BeastCore._sync_temperament) against a stand-in roster and read the
    # beast.temperament.* keys it actually publishes -- so the spec is checked against the producer,
    # not merely declared.
    state = StateRegistry()
    state.update_many("progression", {"progression.beast.id": "A"}, priority=87)
    parent = {"lineage_id": "standard", "identity": {"traits": {"temperament": {a: 50 for a in TEMPERAMENT_AXES}}}}
    core = types.SimpleNamespace(state=state, roster=_FakeRoster({"A": parent}), _temperament_beast_id=None)
    BeastCore._sync_temperament(core)
    return {k for k in state.snapshot(include_meta=False) if k.startswith("beast.temperament.")}


def _prior_keys():
    """Full-key set from the archived specs: v1-v3 are suffix snapshots, v4/v5/v6 are deltas."""
    keys = set()
    for fn in ("beastagotchi_v1_canonical_data_keys.json",
               "Beastagotchi_Canonical_Data_Keys_v2.json",
               "Beastagotchi_Canonical_Data_Keys_v3.json"):
        for ns, ks in json.loads((ARCHIVE / fn).read_text()).get("namespaces", {}).items():
            keys.update(f"{ns}.{k}" for k in ks)
    for fn in ("Beastagotchi_Canonical_Data_Keys_v4.json", "Beastagotchi_Canonical_Data_Keys_v5.json"):
        for ns, ks in json.loads((ARCHIVE / fn).read_text()).get("new_namespaces", {}).items():
            keys.update(ks)
    keys.update(json.loads((ARCHIVE / "Beastagotchi_Canonical_Data_Keys_v6.json").read_text()).get("added_in_v0.9", []))
    return keys


def test_spec_is_v7_and_wellformed():
    assert SPEC["schema_version"] == 7
    assert isinstance(NAMESPACES, dict) and NAMESPACES
    for ns, keys in NAMESPACES.items():
        assert isinstance(keys, list) and keys, ns
        for k in keys:
            assert k.split(".", 1)[0] == ns, f"{k} is not under namespace {ns}"


def test_beast_namespace_matches_all_producers():
    # Bidirectional: the live beast namespace must equal exactly what Beast Core produces for a
    # Beast -- tick()'s expression keys plus core._sync_temperament's temperament axes. No produced
    # key missing, no unproduced key invented (ADR-0008 live-truth; ADR-0009).
    produced = _emitted_beast_keys() | _produced_temperament_keys()
    assert set(NAMESPACES.get("beast", [])) == produced


def test_temperament_is_live_and_matches_heritage_axes():
    beast = set(NAMESPACES.get("beast", []))
    expected = {f"beast.temperament.{a}" for a in TEMPERAMENT_AXES}
    assert expected <= beast                           # all five axes documented live (ADR-0009)
    assert _produced_temperament_keys() == expected    # and the producer emits exactly those
    assert not DEFERRED                                # nothing left deferred now that F5 is in-tree


def test_no_prior_key_was_dropped():
    # Every key from the archived v1-v6 specs must still be accounted for -- live, legacy, or
    # deferred (ADR-0007). Key-level, so it catches a key removed even when its namespace survives.
    documented = LIVE_KEYS | set(LEGACY) | set(DEFERRED)
    missing = _prior_keys() - documented
    assert not missing, f"prior canonical keys dropped from v7: {sorted(missing)}"


def test_prior_namespaces_are_covered():
    expected = {
        "system", "storage", "radio", "wifi", "captures", "gps", "pwnagotchi", "bettercap",
        "beast", "platform", "context", "health", "history", "session",
        "power", "dock", "network", "capabilities", "plugins", "progression",
        "rare", "ambient", "celestial",
    }
    assert expected <= set(NAMESPACES)


def test_legacy_keys_documented_and_not_live():
    assert not (set(LEGACY) & LIVE_KEYS)
    for k in ("beast.boredom", "beast.current_expression", "beast.current_animation"):
        assert k in LEGACY


def test_needs_namespace_matches_the_engine():
    # The needs namespace holds exactly the keys NeedsEngine produces (ADR-0010) -- producer-verified,
    # like the beast namespace, so the spec can't drift from the engine.
    produced = set(NeedsEngine(FakeState({}), clock=lambda: 0.0).tick())
    assert set(NAMESPACES.get("needs", [])) == produced
