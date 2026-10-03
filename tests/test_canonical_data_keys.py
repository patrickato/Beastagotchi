"""Drift guard for the consolidated canonical data-key spec (v7).

v1-v6 fragmented the canonical state keys across six files, none of which the code loaded, so the
spec silently drifted from the machine. v7 is the single consolidated spec. These tests enforce,
as ongoing invariants, what the consolidation promised:

- the ``beast`` namespace holds *exactly* the ``beast.*`` keys ``PersonalityEngine`` actually emits
  -- both directions, so the spec can neither miss an emitted key nor invent an unproduced one
  (ADR-0008 live-truth);
- no key from any archived v1-v6 spec was dropped (ADR-0007): every one is live, legacy, or deferred;
- keys the code does not produce stay out of the live namespaces.

Only the ``beast`` namespace is producer-verified here; the other namespaces are a faithful
consolidation whose key-level completeness is guarded by ``test_no_prior_key_was_dropped``.
"""
from __future__ import annotations

import json
from pathlib import Path

from beastcore.personality import PersonalityEngine

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


def _emitted_beast_keys():
    out = PersonalityEngine(FakeState({}), clock=lambda: 0.0).tick()
    return {k for k in out if k.startswith("beast.")}


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


def test_beast_namespace_is_exactly_the_engine_output():
    # Bidirectional: the live beast namespace must equal what PersonalityEngine actually emits --
    # no emitted key missing, and no unproduced key invented (ADR-0008 live-truth). Temperament is
    # not in tick() output, so this also enforces that it stays deferred, not live.
    assert set(NAMESPACES.get("beast", [])) == _emitted_beast_keys()


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


def test_legacy_and_deferred_keys_are_not_live():
    # Documented-but-not-produced keys must never leak into the live namespaces.
    assert not ((set(LEGACY) | set(DEFERRED)) & LIVE_KEYS)
    # The round-1 reclassifications are recorded (factual notes, no supersession/rename asserted).
    for k in ("beast.boredom", "beast.current_expression", "beast.current_animation"):
        assert k in LEGACY
    for axis in ("curiosity", "social", "focus", "boldness", "nocturnal"):
        assert f"beast.temperament.{axis}" in DEFERRED
