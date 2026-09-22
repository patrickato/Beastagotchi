from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AppDefinition:
    id: str
    title: str
    category: str
    kind: str
    target: str
    description: str
    accent: str = "primary"


# Only implemented destinations belong here. Planned capabilities live in the
# completion matrix until code exists; the launcher never presents dead cards.
APPS: tuple[AppDefinition, ...] = (
    AppDefinition("home", "Home", "Deck", "page", "home", "Beast summary / live status", "primary"),
    AppDefinition("overview", "Overview", "Deck", "page", "overview", "Whole-device status and attention", "accent"),
    AppDefinition("dashboard", "Dashboard", "Deck", "page", "dashboard", "Six user-bound live instruments", "info"),
    AppDefinition("recon", "Recon", "Radio", "page", "recon", "Live observed Wi-Fi objects", "accent"),
    AppDefinition("networks", "Networks", "Radio", "page", "networks", "Current AP browser", "info"),
    AppDefinition("beastdex", "BeastDex", "Records", "overlay", "beastdex", "Persistent network encyclopedia", "accent"),
    AppDefinition("spectrum", "Spectrum", "Radio", "page", "spectrum", "Observed channel activity", "secondary"),
    AppDefinition("captures", "Capture Analytics", "Records", "page", "captures", "Live capture analytics", "accent"),
    AppDefinition("capture_vault", "Capture Vault", "Records", "overlay", "capture_vault", "Indexed real capture files", "secondary"),
    AppDefinition("map", "Field Map", "Field", "page", "map", "Real Expedition GPS route", "info"),
    AppDefinition("expedition", "Expeditions", "Field", "page", "expedition", "Persistent field sessions", "secondary"),
    AppDefinition("beast", "Beast", "Identity", "page", "beast", "Progression / evolution", "primary"),
    AppDefinition("system", "System", "System", "page", "system", "Health / hardware / performance", "warn"),
    AppDefinition("themes", "Theme Studio", "Studio", "overlay", "theme_library", "Theme identity + live options", "primary"),
    AppDefinition("visualizers", "Visualizer", "Studio", "overlay", "visualizer", "Renderer families", "info"),
    AppDefinition("telemetry", "Telemetry", "System", "overlay", "telemetry", "Source / freshness inspector", "accent"),
    AppDefinition("correlation", "Correlation Lab", "System", "overlay", "correlation", "Compare two real telemetry streams", "info"),
    AppDefinition("performance", "Performance", "System", "overlay", "performance", "Real service/render cost attribution", "warn"),
    AppDefinition("plugins", "Plugins", "System", "overlay", "plugins", "Pwnagotchi integration catalog", "secondary"),
    AppDefinition("timeline", "Timeline", "Records", "overlay", "timeline", "Durable Beast event history", "info"),
    AppDefinition("notifications", "Notifications", "System", "overlay", "notifications", "Warnings and important events", "warn"),
    AppDefinition("diagnostics", "Diagnostics", "System", "overlay", "diagnostics", "Collector health and failures", "warn"),
    AppDefinition("incidents", "Black Box", "System", "overlay", "incidents", "Durable incidents and recovery history", "warn"),
    AppDefinition("services", "Services", "System", "overlay", "services", "Live systemd service states", "accent"),
    AppDefinition("operations", "Operations", "System", "overlay", "operations", "Whole-platform operations snapshot", "primary"),
    AppDefinition("topology", "Topology", "System", "overlay", "topology", "Live Beast dependency graph", "info"),
    AppDefinition("tasks", "Task Center", "System", "overlay", "tasks", "Background jobs and progress", "secondary"),
    AppDefinition("field_library", "Field Library", "Records", "overlay", "field_library", "Offline indexed knowledge", "accent"),
    AppDefinition("missions", "Mission Packs", "Field", "overlay", "missions", "Declarative field/lab/home workflows", "primary"),
    AppDefinition("hardware", "Hardware", "Hardware", "overlay", "hardware", "Detected USB / capability inventory", "secondary"),
    AppDefinition("connectivity", "Connectivity", "Hardware", "overlay", "connectivity", "Interfaces, route and management connectivity", "info"),
    AppDefinition("storage", "Storage", "System", "overlay", "storage", "Mounts, space and filesystem health", "info"),
    AppDefinition("backups", "Backup Center", "System", "overlay", "backups", "Recovery archives and restore readiness", "accent"),
    AppDefinition("beast_studio", "Beast Studio", "Studio", "overlay", "studio", "Exact-frame web customizer", "primary"),
    AppDefinition("achievements", "Achievements", "Identity", "overlay", "achievements", "Badges / awards / rarity", "accent"),
    AppDefinition("help", "Controls", "System", "overlay", "help", "Interaction reference", "warn"),
)

OPTIONAL_APPS: dict[str, AppDefinition] = {
    "command_center": AppDefinition("command_center", "Command Center", "Hardware", "overlay", "command_center", "External-display / desktop capability center", "accent"),
    "ai_operator": AppDefinition("ai_operator", "Beast Operator", "System", "overlay", "ai_operator", "Optional local AI/operator capability", "primary"),
    "containers": AppDefinition("containers", "Container Center", "System", "overlay", "containers", "Optional Docker/Podman inventory", "info"),
}



class AppRegistry:
    """Expandable UI/app registry independent from the Home Deck page count."""

    def __init__(self, apps: Iterable[AppDefinition] = APPS) -> None:
        self._apps = tuple(apps)
        self._by_id = {a.id: a for a in self._apps}

    def all(self) -> list[AppDefinition]:
        return list(self._apps)

    def get(self, app_id: str) -> AppDefinition | None:
        return self._by_id.get(str(app_id))

    def categories(self) -> list[str]:
        seen=[]
        for app in self._apps:
            if app.category not in seen:seen.append(app.category)
        return seen


    def by_ids(self, ids) -> list[AppDefinition]:
        out=[]
        for app_id in ids or []:
            app=self.get(str(app_id))
            if app is not None and app not in out:out.append(app)
        return out

    def by_category(self, category: str | None) -> list[AppDefinition]:
        if not category or str(category).upper() == "ALL":
            return self.all()
        return [a for a in self._apps if a.category == str(category)]

    def page(self, offset: int = 0, size: int = 6) -> list[AppDefinition]:
        offset=max(0,int(offset));size=max(1,int(size))
        return list(self._apps[offset:offset+size])
