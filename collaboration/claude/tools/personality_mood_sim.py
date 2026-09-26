"""Reproduce the mood-distribution and uptime-XP findings in
BEASTAGOTCHI_CREATURE_IDEAS_AND_FINDINGS_2026-09-26.md.

Runs the real beastcore PersonalityEngine and progression curve against
simulated state; nothing touches a device, database or service.

Usage (from the repository root, or pass the root explicitly):
    python3 collaboration/claude/tools/personality_mood_sim.py [REPO_ROOT]
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from beastcore.personality import PersonalityEngine  # noqa: E402
from beastcore.progression import level_for_xp, stage_for_level, xp_threshold  # noqa: E402


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


def mood_distribution(base: dict, ap_change_prob: float, seconds: int = 3600) -> dict[str, float]:
    """Tick once per simulated second; the AP count drifts by +/-1 with the given probability."""
    clock = [0.0]
    state = FakeState(base)
    engine = PersonalityEngine(state, clock=lambda: clock[0])
    rng = random.Random(1)
    aps = 30
    counts: dict[str, int] = {}
    for second in range(seconds):
        clock[0] = float(second)
        if ap_change_prob and rng.random() < ap_change_prob:
            aps = max(0, aps + rng.choice([-1, 1]))
        state["wifi.ap_count"] = aps
        mood = engine.tick()["beast.mood"]
        counts[mood] = counts.get(mood, 0) + 1
    return {k: round(v * 100 / seconds, 1) for k, v in sorted(counts.items(), key=lambda kv: -kv[1])}


def uptime_only_xp_after_one_year() -> int:
    """1 XP per 600 s of runtime plus runtime and level achievement bonuses (progression.py)."""
    runtime_xp = 365 * 24 * 6
    runtime_bonus = 20 + 50 + 200 + 500 + 1000
    level_bonuses = [(5, 15), (10, 25), (20, 50), (35, 100), (50, 200), (70, 350), (85, 600), (100, 1500)]
    xp = runtime_xp + runtime_bonus
    for _ in range(10):
        level = level_for_xp(xp)
        new_xp = runtime_xp + runtime_bonus + sum(b for lvl, b in level_bonuses if level >= lvl)
        if new_xp == xp:
            break
        xp = new_xp
    return xp


def main() -> None:
    common = {
        "health.core.state": "healthy", "governor.mode": "FULL", "system.temp.cpu_c": 55.0,
        "pwnagotchi.service.state": "active", "bettercap.state": "active",
        "expedition.active": True,  # ExpeditionEngine always keeps an expedition active
        "semantic.capture.recent": False, "system.cpu.total": 20.0, "progression.level": 7,
    }
    scenarios = [
        ("Indoors, GPS plugged in, no fix (day)", {"gps.state": "connected_no_fix", "ambient.day_phase": "day"}, 0.05),
        ("Indoors, GPS plugged in, no fix (night)", {"gps.state": "connected_no_fix", "ambient.day_phase": "night"}, 0.05),
        ("No GPS, AP count drifts ~every 20 s (night)", {"gps.state": "unavailable", "ambient.day_phase": "night"}, 0.05),
        ("No GPS, AP count perfectly static (night)", {"gps.state": "unavailable", "ambient.day_phase": "night"}, 0.0),
        ("GPS fixed, AP count drifts ~every 20 s", {"gps.state": "fixed", "ambient.day_phase": "day"}, 0.05),
    ]
    print("Mood share over one simulated hour:")
    for label, extra, drift in scenarios:
        print(f"  {label:46s} {mood_distribution({**common, **extra}, drift)}")

    xp = uptime_only_xp_after_one_year()
    level = level_for_xp(xp)
    print()
    print(f"Uptime-only XP after one year powered 24/7: {xp:,} -> level {level} ({stage_for_level(level)})")
    print(f"XP needed: level 30 = {xp_threshold(30):,}, level 50 = {xp_threshold(50):,}, level 100 = {xp_threshold(100):,}")


if __name__ == "__main__":
    main()
