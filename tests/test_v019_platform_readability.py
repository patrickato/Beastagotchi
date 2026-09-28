from pathlib import Path

from beastui.engine import BeastUI


ROOT = Path(__file__).resolve().parents[1]


def test_platform_readability_patch_is_installed():
    assert BeastUI._platform_surface_v2_installed is True
    assert hasattr(BeastUI, "_platform_rows_v1")
    assert hasattr(BeastUI, "_platform_browser_v1")


def test_platform_surface_source_uses_physical_readability_font_tiers():
    text = (ROOT / "beastui" / "platform_surfaces_v2.py").read_text()
    assert 'font=f["body"]' in text
    assert 'font=f["small"]' in text
    assert "7px" not in text


def test_hardware_rows_split_device_identity_from_bus_metadata(tmp_path):
    ui = BeastUI(root=ROOT / "beastui", output=str(tmp_path / "hardware.png"), theme_id="classic")
    ui.state = {
        "platform.hardware": [
            {
                "raw": "Bus 001 Device 002: ID 1546:01a7 u-blox AG [u-blox 7]",
                "id": "1546:01a7",
            }
        ]
    }
    rows = ui._platform_rows("hardware")
    assert rows[0]["title"] == "u-blox AG [u-blox 7]"
    assert rows[0]["subtitle"] == "Bus 001 Device 002: · 1546:01a7"
    assert rows[0]["value"] == "1546:01a7"


def test_connectivity_internet_copy_keeps_route_truth_explicit(tmp_path):
    ui = BeastUI(root=ROOT / "beastui", output=str(tmp_path / "connectivity.png"), theme_id="classic")
    ui.state = {
        "network.route.available": True,
        "network.default.dev": "eth0",
        "network.default.gateway": "192.0.2.1",
        "network.internet.state": "unknown",
        "network.interfaces": [],
    }
    rows = ui._platform_rows("connectivity")
    internet = next(row for row in rows if row["title"] == "INTERNET")
    assert internet["value"] == "UNKNOWN"
    assert "does not prove Internet reachability" in internet["subtitle"]
