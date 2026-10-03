"""Reproduce (and now close) the mood-distribution finding F1 from
BEASTAGOTCHI_CREATURE_IDEAS_AND_FINDINGS_2026-09-26.md.

Runs the *real* beastcore pipeline -- NeedsEngine then PersonalityEngine, exactly as
``core._personality_loop`` does -- against simulated real-world signals. Nothing touches a
device, database or service.

Before the F1 fix the Beast sat in one or two moods forever (``quiet`` reset on any AP-count
churn; ``hunting``/``gps-searching`` gated on the always-true ``expedition.active``;
``celebrating`` keyed on an unpublished signal). After the fix mood is derived from genuine
novelty, real motion, real captures and the live ``needs.*`` drives, so it varies over a day and
two Beasts diverge.

Usage (from the repository root, or pass the root explicitly):
    python3 collaboration/claude/tools/personality_mood_sim.py [REPO_ROOT]
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from beastcore.needs import NeedsEngine  # noqa: E402
from beastcore.personality import PersonalityEngine  # noqa: E402
from beastcore.progression import level_for_xp, stage_for_level, xp_threshold  # noqa: E402

H = 3600.0

BASE = {
    "health.core.state": "healthy", "governor.mode": "FULL", "pwnagotchi.service.state": "active",
    "bettercap.state": "active", "progression.level": 7, "system.cpu.total": 18.0,
}


class FakeState(dict):
    def get(self, key, default=None):
        return dict.get(self, key, default)


def simulate(world, hours: float, temperament: dict | None = None, tick_sec: int = 10) -> dict[str, float]:
    """Tick NeedsEngine then PersonalityEngine once per ``tick_sec`` simulated seconds, feeding the
    needs output back into state exactly as Core does, and tally the expressed mood."""
    clock = [0.0]
    state = FakeState({})
    if temperament:
        state.update({f"beast.temperament.{k}": v for k, v in temperament.items()})
    needs = NeedsEngine(state, clock=lambda: clock[0])
    pers = PersonalityEngine(state, clock=lambda: clock[0])
    counts: dict[str, int] = {}
    for second in range(0, int(hours * H), tick_sec):
        clock[0] = float(second)
        state.update(world(second))                  # real signals at this moment
        for key, value in needs.tick().items():      # needs first (mood consumes them), None = unavailable
            state[key] = value
        mood = pers.tick()["beast.mood"]
        counts[mood] = counts.get(mood, 0) + 1
    total = sum(counts.values()) or 1
    return {k: round(v * 100 / total, 1) for k, v in sorted(counts.items(), key=lambda kv: -kv[1])}


# --- worlds: each maps a simulated second to the real signals at that moment -----------------

def home(t: float) -> dict:
    """Sitting at home: GPS plugged in but no fix, a few new networks on arrival then nothing new,
    one neighbour early, cool and on mains; day drifts into evening then night."""
    new = 100 + min(3, int(t // 400))            # +1 new network every ~7 min, up to 3, then flat
    phase = "day" if t < 4 * H else ("evening" if t < 5 * H else "night")
    return {**BASE,
            "gps.state": "connected_no_fix", "gps.fix": False, "context.motion.state": "unknown",
            "wifi.ap_count": 24, "wifi.encounters.session_unique": new,
            "wifi.encounters.lifetime_unique": 1000 + new,
            "peerdex.last_seen_at": (60.0 if t >= 60 else None),
            "system.temp.cpu_c": 52.0, "power.battery.percent_estimate": 80.0,
            "ambient.day_phase": phase}


def walk(t: float) -> dict:
    """Out for a walk: GPS fixed and moving, a steady trickle of genuinely new networks."""
    new = 200 + int(t // 120)                     # a new network about every 2 min on foot
    return {**BASE,
            "gps.state": "fixed", "gps.fix": True, "context.motion.state": "walking",
            "gps.session_distance_m": 1.4 * t,     # ~walking pace
            "wifi.ap_count": 30, "wifi.encounters.session_unique": new,
            "wifi.encounters.lifetime_unique": 2000 + new,
            "peerdex.last_seen_at": 1800.0 if t >= 1800 else None,
            "system.temp.cpu_c": 58.0, "power.battery.percent_estimate": 70.0,
            "ambient.day_phase": "day"}


def wardrive(t: float) -> dict:
    """Driving a loop: fast motion, a flood of new networks, the odd handshake captured."""
    new = 300 + int(t // 20)                       # a new network every ~20 s
    caps = int(t // 900)                           # a capture about every 15 min
    return {**BASE,
            "gps.state": "fixed", "gps.fix": True, "context.motion.state": "wardrive",
            "gps.session_distance_m": 13.0 * t, "captures.total": caps,
            "wifi.ap_count": 45, "wifi.encounters.session_unique": new,
            "wifi.encounters.lifetime_unique": 3000 + new,
            "system.temp.cpu_c": 64.0, "power.battery.percent_estimate": 60.0,
            "ambient.day_phase": "day"}


def hot_night(t: float) -> dict:
    """A hot spell then a long night on a draining battery, nothing new happening -- neglect."""
    hot = t < 1.5 * H
    temp = 86.0 if hot else 55.0
    batt = max(8.0, 60.0 - t / H * 12.0)           # drains ~12%/h toward empty
    return {**BASE,
            "governor.mode": "REDUCED" if hot else "FULL",
            "gps.state": "unavailable", "gps.fix": False, "context.motion.state": "unknown",
            "wifi.ap_count": 12, "wifi.encounters.session_unique": 400,   # flat: nothing new
            "wifi.encounters.lifetime_unique": 4000,
            "system.temp.cpu_c": temp, "power.battery.percent_estimate": batt,
            "ambient.day_phase": "day" if hot else "night"}


def day_in_the_life(t: float) -> dict:
    """A whole day stitched together: home -> walk -> wardrive -> hot afternoon -> night in."""
    if t < 3 * H:
        return home(t)
    if t < 4 * H:
        return walk(t - 3 * H)
    if t < 5 * H:
        return wardrive(t - 4 * H)
    return hot_night(t - 5 * H)


def main() -> None:
    print("Mood share (real NeedsEngine + PersonalityEngine), neutral Beast:")
    for label, world, hours in (
        ("Home all day, GPS no fix (day->night)", home, 6),
        ("Out for a walk, GPS fixed", walk, 3),
        ("Wardrive with captures", wardrive, 3),
        ("Hot spell then a long night", hot_night, 6),
        ("A day in the life (home->walk->drive->hot->night)", day_in_the_life, 8),
    ):
        print(f"  {label:50s} {simulate(world, hours)}")

    print()
    print("Same day in the life, different heritage (two Beasts diverge) -- findings F5 + needs:")
    for label, temperament in (
        ("neutral", {}),
        ("curious + nocturnal", {"curiosity": 95, "nocturnal": 95, "social": 80}),
        ("timid + diurnal", {"curiosity": 10, "nocturnal": 10, "boldness": 15}),
    ):
        print(f"  {label:26s} {simulate(day_in_the_life, 8, temperament)}")

    print()
    print("Temperament effect on expressed scalars (identical idle state, different Beasts):")
    idle = {**BASE, "gps.state": "fixed", "ambient.day_phase": "day", "system.cpu.total": 0.0}
    for label, temperament in (
        ("neutral (or no heritage)", {}),
        ("curious + bold", {"curiosity": 95, "boldness": 95}),
        ("timid + incurious", {"curiosity": 5, "boldness": 5}),
    ):
        state = FakeState({**idle, **{f"beast.temperament.{k}": v for k, v in temperament.items()}})
        out = PersonalityEngine(state, clock=lambda: 0.0).tick()
        print(f"  {label:26s} energy={out['beast.energy']:3d} focus={out['beast.focus']:3d} "
              f"curiosity={out['beast.curiosity']:3d} stress={out['beast.stress']:3d}")

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
    level = level_for_xp(xp)
    print()
    print(f"Uptime-only XP after one year powered 24/7: {xp:,} -> level {level} ({stage_for_level(level)})")
    print(f"XP needed: level 30 = {xp_threshold(30):,}, level 50 = {xp_threshold(50):,}, level 100 = {xp_threshold(100):,}")


if __name__ == "__main__":
    main()
