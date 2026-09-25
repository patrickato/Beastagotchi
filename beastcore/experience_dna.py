from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


VISUAL_FAMILIES: dict[str, dict[str, Any]] = {
    "expedition": {
        "label": "Expedition / Field",
        "intent": "navigation, journey, field awareness, rugged glanceability",
        "examples": ["Atlas", "Trailhead", "Outpost", "Surveyor", "Waypoint", "Ranger"],
    },
    "scientific": {
        "label": "Scientific / Instrument",
        "intent": "measured truth, graphs, spectra, correlation and research",
        "examples": ["Observatory", "Spectra", "Signal Lab", "Vector", "Helix", "Workbench"],
    },
    "operations": {
        "label": "Operations / Command",
        "intent": "state, incidents, remote operations, mission awareness and coordination",
        "examples": ["Mission Control", "Sentinel", "Watchtower", "Relay", "Ops Grid", "Command Deck"],
    },
    "industrial": {
        "label": "Industrial / Machine",
        "intent": "hardware, power, storage, services and physical-machine presence",
        "examples": ["Forge", "Foundry", "Engine Room", "Machine Bay", "Switchgear", "Workshop"],
    },
    "companion": {
        "label": "Creature / Companion",
        "intent": "identity, mood, growth, relationship, habitat and personality",
        "examples": ["Habitat", "Vivarium", "Sanctum", "Nest", "Caretaker", "Menagerie"],
    },
    "arcane": {
        "label": "Arcane / Hidden",
        "intent": "rares, secrets, lore, ciphers, uncanny reveals and unlockable worlds",
        "examples": ["Cipher", "Relic", "Vault", "Obsidian Archive", "Warden", "Haunt"],
    },
    "premium": {
        "label": "Premium / Modern",
        "intent": "calm polish, product-grade hierarchy, elegant motion and restraint",
        "examples": ["Monolith", "Prism", "Slate", "Halo", "Studio", "Aurum"],
    },
    "archival": {
        "label": "Archive / Paper",
        "intent": "history, notes, dossiers, logs, patient charts and post-run review",
        "examples": ["Dossier", "Field Notes", "Ledger", "Archive", "Operator Journal", "Atlas Book"],
    },
    "ecological": {
        "label": "Ecological / Organic",
        "intent": "environment, weather, growth, ambient sensing and biome-like behavior",
        "examples": ["Canopy", "Mycelium", "Tidepool", "Biome", "Terrarium", "Weathered"],
    },
    "nautical": {
        "label": "Nautical / Marine",
        "intent": "AIS, weather, navigation, water travel and Great Lakes field context",
        "examples": ["Harbor", "Bridge", "Sonar", "Buoy", "Chartroom", "Lighthouse"],
    },
    "aviation": {
        "label": "Aviation / Flight",
        "intent": "ADS-B, tracks, altitude, movement, airspace and spotting",
        "examples": ["Flightline", "Radar Room", "Airframe", "Tower", "Approach", "Vector Flight"],
    },
    "analog": {
        "label": "Analog / Electromechanical",
        "intent": "meters, dials, relays, paper tape, physical controls and tactile nostalgia",
        "examples": ["Bench Meter", "Relay Panel", "Gaugeworks", "Teletype", "Patchbay", "Control Cabinet"],
    },
    "urban": {
        "label": "Urban / Street",
        "intent": "dense local context, city movement, discovery and layered environmental signals",
        "examples": ["Street Grid", "Transit", "Night Walk", "Blockwatch", "City Survey", "District"],
    },
    "educational": {
        "label": "Educational / Explain",
        "intent": "learning, transparent causality, guided inspection and system understanding",
        "examples": ["Tutor", "Explainer", "Signal School", "Anatomy", "Lab Notes", "Guided Mode"],
    },
    "meditative": {
        "label": "Calm / Ambient",
        "intent": "low-noise companionship, subtle awareness and reduced cognitive load",
        "examples": ["Stillwater", "Quiet Room", "Night Watch", "Low Tide", "Ember", "Drift"],
    },
    "developer": {
        "label": "Developer / Bench",
        "intent": "debugging, exact state, profiling, introspection and rapid iteration",
        "examples": ["Bench", "Trace", "Inspector", "Wireframe", "Profiler", "Sandbox"],
    },
}

LAYOUT_FAMILIES = {
    "hero_scene", "split_console", "radial", "telemetry_stack", "map_first",
    "creature_first", "module_grid", "notebook", "terminal_first", "immersive_hud",
    "sidebar_strip", "bottom_dock", "cockpit_cluster", "timeline", "canvas_freeform",
}

DENSITIES = {"glance", "balanced", "dense", "expert", "diagnostic"}
MOTION_PROFILES = {
    "still", "subtle", "calm_ambient", "playful", "reactive", "tactical",
    "premium", "arcade", "ominous", "scientific",
}
CREATURE_PRESENCE = {"hidden", "ambient", "supporting", "prominent", "dominant"}
UTILITY_BIAS = {"companion", "balanced", "instrument", "operations"}
PLAYFULNESS = {"none", "low", "moderate", "high"}
ALERT_STYLES = {"quiet", "clinical", "field", "tactical", "dramatic", "companion"}
INPUT_MODELS = {"touch_first", "mixed", "remote_first", "headless_first", "physical_controls"}
DOCTOR_VISIBILITY = {"background", "contextual", "prominent", "operations_first"}
MYSTERY_LEVELS = {"none", "subtle", "discoverable", "deep"}
QUALITY_VARIANTS = {"constrained", "compact", "full", "enhanced"}


@dataclass(frozen=True)
class ExperienceDNA:
    id: str
    label: str
    visual_family: str
    layout_family: str
    density: str = "balanced"
    motion_profile: str = "subtle"
    creature_presence: str = "prominent"
    utility_bias: str = "balanced"
    playfulness: str = "moderate"
    alert_style: str = "field"
    hardware_fit: tuple[str, ...] = ("reference", "medium", "large", "desktop")
    input_model: str = "touch_first"
    doctor_visibility: str = "contextual"
    mystery_level: str = "subtle"
    mission_bias: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    description: str = ""

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.id or self.id.lower() != self.id:
            errors.append("id must be non-empty lowercase")
        if self.visual_family not in VISUAL_FAMILIES:
            errors.append(f"unknown visual_family: {self.visual_family}")
        if self.layout_family not in LAYOUT_FAMILIES:
            errors.append(f"unknown layout_family: {self.layout_family}")
        for value, allowed, field in (
            (self.density, DENSITIES, "density"),
            (self.motion_profile, MOTION_PROFILES, "motion_profile"),
            (self.creature_presence, CREATURE_PRESENCE, "creature_presence"),
            (self.utility_bias, UTILITY_BIAS, "utility_bias"),
            (self.playfulness, PLAYFULNESS, "playfulness"),
            (self.alert_style, ALERT_STYLES, "alert_style"),
            (self.input_model, INPUT_MODELS, "input_model"),
            (self.doctor_visibility, DOCTOR_VISIBILITY, "doctor_visibility"),
            (self.mystery_level, MYSTERY_LEVELS, "mystery_level"),
        ):
            if value not in allowed:
                errors.append(f"unknown {field}: {value}")
        return tuple(errors)

    def as_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["schema"] = 1
        return row


BUILTIN_EXPERIENCE_DNA: dict[str, ExperienceDNA] = {
    "atlas": ExperienceDNA(
        id="atlas", label="Atlas", visual_family="expedition", layout_family="map_first",
        density="balanced", motion_profile="calm_ambient", creature_presence="supporting",
        utility_bias="instrument", playfulness="low", alert_style="field",
        doctor_visibility="contextual", mystery_level="discoverable",
        mission_bias=("expedition", "location", "journey", "field"),
        tags=("gps", "map", "waypoint", "travel"),
        description="A rugged field atlas where journey, location, nearby discoveries and expedition history lead.",
    ),
    "forge": ExperienceDNA(
        id="forge", label="Forge", visual_family="industrial", layout_family="cockpit_cluster",
        density="dense", motion_profile="reactive", creature_presence="ambient",
        utility_bias="operations", playfulness="low", alert_style="tactical",
        doctor_visibility="prominent", mystery_level="none",
        mission_bias=("hardware", "power", "storage", "services", "bench"),
        tags=("machine", "hardware", "thermal", "doctor"),
        description="An industrial machine-room experience centered on the Pi, peripherals, health and control.",
    ),
    "observatory": ExperienceDNA(
        id="observatory", label="Observatory", visual_family="scientific", layout_family="split_console",
        density="expert", motion_profile="scientific", creature_presence="supporting",
        utility_bias="instrument", playfulness="low", alert_style="clinical",
        doctor_visibility="contextual", mystery_level="subtle",
        mission_bias=("spectrum", "telemetry", "research", "correlation"),
        tags=("graphs", "signals", "spectrum", "truth"),
        description="A measured research instrument where live signals, history and correlation dominate the visual hierarchy.",
    ),
    "habitat": ExperienceDNA(
        id="habitat", label="Habitat", visual_family="companion", layout_family="creature_first",
        density="glance", motion_profile="playful", creature_presence="dominant",
        utility_bias="companion", playfulness="high", alert_style="companion",
        doctor_visibility="background", mystery_level="deep",
        mission_bias=("companion", "growth", "memory", "rares", "daily"),
        tags=("beast", "mood", "growth", "secrets"),
        description="A living companion space where the Beast, mood, growth, memories and discoveries lead.",
    ),
    "monolith": ExperienceDNA(
        id="monolith", label="Monolith", visual_family="premium", layout_family="immersive_hud",
        density="balanced", motion_profile="premium", creature_presence="prominent",
        utility_bias="balanced", playfulness="moderate", alert_style="quiet",
        doctor_visibility="contextual", mystery_level="discoverable",
        mission_bias=("daily", "showpiece", "companion", "field"),
        tags=("premium", "minimal", "product", "showpiece"),
        description="A calm premium flagship identity with deliberate hierarchy, subtle motion and strong creature presence.",
    ),
    "dossier": ExperienceDNA(
        id="dossier", label="Dossier", visual_family="archival", layout_family="notebook",
        density="dense", motion_profile="still", creature_presence="ambient",
        utility_bias="instrument", playfulness="none", alert_style="clinical",
        doctor_visibility="prominent", mystery_level="discoverable",
        mission_bias=("history", "doctor", "notes", "postrun", "archive"),
        tags=("logs", "patient-chart", "timeline", "evidence"),
        description="A document-like archival experience for histories, Doctor evidence, notes and post-run analysis.",
    ),
    "stillwater": ExperienceDNA(
        id="stillwater", label="Stillwater", visual_family="meditative", layout_family="hero_scene",
        density="glance", motion_profile="calm_ambient", creature_presence="prominent",
        utility_bias="companion", playfulness="low", alert_style="quiet",
        doctor_visibility="background", mystery_level="subtle",
        mission_bias=("night", "daily", "companion", "low_power"),
        tags=("calm", "night", "reduced-motion", "low-noise"),
        description="A low-noise ambient mode for quiet daily use, night operation and reduced cognitive load.",
    ),
    "bench": ExperienceDNA(
        id="bench", label="Bench", visual_family="developer", layout_family="module_grid",
        density="diagnostic", motion_profile="still", creature_presence="hidden",
        utility_bias="operations", playfulness="none", alert_style="clinical",
        doctor_visibility="operations_first", mystery_level="none",
        mission_bias=("development", "debug", "profile", "doctor", "benchlink"),
        tags=("developer", "trace", "performance", "exact-state"),
        description="A transparent developer surface for profiling, exact state, Doctor findings and BenchLink work.",
    ),
}


# These remain valid presets/themes, but intentionally do not define the product taxonomy.
LEGACY_REFERENCE_IDENTITIES = {
    "classic", "cyberpunk", "blackice", "wopr_norad", "lcars", "hunter",
    "matrix", "retro_crt", "synthwave", "amber_tactical", "starcore",
}


def get_experience_dna(experience_id: str) -> ExperienceDNA | None:
    return BUILTIN_EXPERIENCE_DNA.get(str(experience_id or "").strip().lower())


def list_experience_families() -> list[dict[str, Any]]:
    return [
        {"id": key, **value}
        for key, value in sorted(VISUAL_FAMILIES.items(), key=lambda item: item[1]["label"])
    ]


def compile_experience_variant(
    dna: ExperienceDNA,
    platform_profile: dict[str, Any] | None,
    *,
    context: str | None = None,
) -> dict[str, Any]:
    """Resolve an Experience's quality ladder without changing its identity.

    This is intentionally guidance, not a hard capability blocker. The future
    Experience Compiler and Resource Governor may refine it using measured cost.
    """
    errors = dna.validate()
    if errors:
        raise ValueError("; ".join(errors))

    profile = dict(platform_profile or {})
    tier = str(profile.get("compute_tier") or "full")
    if tier not in QUALITY_VARIANTS:
        tier = "full"
    display = str(profile.get("display_class") or "reference")

    density_order = ["glance", "balanced", "dense", "expert", "diagnostic"]
    density = dna.density
    motion = dna.motion_profile
    creature = dna.creature_presence

    if tier == "constrained":
        density = density_order[max(0, density_order.index(density) - 2)]
        if motion not in {"still", "subtle"}:
            motion = "subtle"
    elif tier == "compact":
        density = density_order[max(0, density_order.index(density) - 1)]
        if motion in {"arcade", "reactive", "tactical"}:
            motion = "subtle"

    if display == "micro":
        density = "glance"
        if creature == "dominant":
            creature = "prominent"
    elif display in {"large", "desktop"} and tier in {"full", "enhanced"}:
        idx = min(len(density_order) - 1, density_order.index(density) + 1)
        density = density_order[idx]

    if str(context or "").lower() in {"night", "low_power"}:
        motion = "subtle" if motion != "still" else "still"

    doctor_visibility = dna.doctor_visibility
    if str(context or "").lower() in {"recovery", "doctor", "incident"}:
        doctor_visibility = "operations_first"

    return {
        "schema": 1,
        "experience_id": dna.id,
        "identity_preserved": True,
        "quality_variant": tier,
        "display_class": display,
        "context": str(context or "default"),
        "visual_family": dna.visual_family,
        "layout_family": dna.layout_family,
        "density": density,
        "motion_profile": motion,
        "creature_presence": creature,
        "utility_bias": dna.utility_bias,
        "doctor_visibility": doctor_visibility,
        "hardware_fit": list(dna.hardware_fit),
        "mission_bias": list(dna.mission_bias),
        "tags": list(dna.tags),
    }


def validate_builtin_experiences(rows: Iterable[ExperienceDNA] | None = None) -> dict[str, tuple[str, ...]]:
    rows = list(rows if rows is not None else BUILTIN_EXPERIENCE_DNA.values())
    return {row.id: row.validate() for row in rows if row.validate()}
