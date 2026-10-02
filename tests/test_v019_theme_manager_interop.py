from __future__ import annotations

from pathlib import Path

from beastcore.plugin_integration import PluginIntegrationEngine
from beastcore.presentation import PresentationBroker
from beastcore.theme_manager_interop import ThemeManagerProbe


class FakeState:
    def __init__(self, data=None):
        self.data = dict(data or {})

    def get(self, key, default=None):
        return self.data.get(key, default)


def theme_source(*, managed: bool = False) -> str:
    managed_methods = """
    def prepare_release(self): pass
    def release_presentation(self): pass
    def acquire_presentation(self): pass
""" if managed else ""
    return """__version__ = "3.0.0"
STAT_SOURCE = None

def diagnose(): pass
def _mesh_peers(): pass

class ThemeManager:
    def on_unload(self): self._orig_render = None
    def _install_live(self): pass
    def try_theme(self): pass
    def _end_try(self): pass
    def render_structure(self):
        return {"layout": {}, "sizes": {}, "hide": [], "panels": []}
    def doctor(self): return diagnose()
    def library_rows(self): pass
    def _present(self):
        np.flatnonzero([])
        fbm.mm.write(b"")
    def _touch_loop(self): return find_touch_device()
    def node_rows(self): return _mesh_peers()
    def wardrive_status(self): pass
    def start_wardrive(self): pass
%s

def placeholder(key):
    if STAT_SOURCE is not None:
        return STAT_SOURCE(key)

def web(path):
    if path == "api/library": pass
    if path == "manifest.json": pass
    if path == "sw.js": pass
""" % managed_methods


def test_theme_manager_probe_detects_current_interop_without_importing(tmp_path: Path):
    fp = tmp_path / "theme_manager.py"
    fp.write_text(theme_source())
    row = ThemeManagerProbe().probe(fp)

    assert row["inspectable"] is True
    assert row["version"] == "3.0.0"
    assert row["managed_handoff_supported"] is False
    assert row["compatibility_handoff_evidence"] is True
    assert {
        "stat_source", "clean_unload", "live_install", "timed_try",
        "structural_themes", "doctor", "gallery", "changed_row_writer",
        "raw_touch", "pwa", "nodes", "wardrive",
    } <= set(row["capabilities"])


def test_theme_manager_probe_requires_explicit_managed_contract(tmp_path: Path):
    fp = tmp_path / "theme_manager.py"
    fp.write_text(theme_source(managed=True))
    row = ThemeManagerProbe().probe(fp)
    assert row["managed_handoff_supported"] is True


def test_plugin_catalog_surfaces_theme_manager_probe(tmp_path: Path):
    fp = tmp_path / "theme_manager.py"
    fp.write_text(theme_source())
    state = FakeState({
        "platform.plugins": [{
            "name": "theme_manager",
            "enabled": True,
            "configured": True,
            "installed_custom": True,
            "path": str(fp),
        }]
    })
    patch = PluginIntegrationEngine(state).tick()
    row = patch["plugins.catalog"][0]

    assert row["interop"]["version"] == "3.0.0"
    assert patch["plugins.theme_manager.inspectable"] is True
    assert patch["plugins.theme_manager.version"] == "3.0.0"
    assert patch["plugins.theme_manager.managed_handoff_supported"] is False
    assert patch["plugins.theme_manager.compatibility_handoff_evidence"] is True


def test_presentation_broker_uses_probe_truth_but_keeps_executor_locked(tmp_path: Path):
    interop = {
        "version": "3.0.0",
        "capabilities": ["clean_unload", "live_install", "stat_source"],
        "managed_handoff_supported": False,
        "compatibility_handoff_evidence": True,
    }
    state = FakeState({
        "pwnagotchi.service.state": "active",
        "platform.services": [],
        "plugins.catalog": [{"name": "theme_manager", "enabled": False, "interop": interop}],
    })
    row = PresentationBroker(state, path=str(tmp_path / "presentation.json")).tick()

    assert row["presentation.theme_manager.version"] == "3.0.0"
    assert "stat_source" in row["presentation.theme_manager.capabilities"]
    assert row["presentation.theme_manager.compatibility_handoff_evidence"] is True
    assert row["presentation.theme_manager.managed_handoff_supported"] is False
    assert row["presentation.executor_enabled"] is False
