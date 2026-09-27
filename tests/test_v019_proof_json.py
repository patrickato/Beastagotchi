import json
from dataclasses import dataclass
from pathlib import Path

from beastui.beast_shell import reading
from tools.proof_json import json_safe


@dataclass(frozen=True)
class _Nested:
    name: str
    path: Path


def test_json_safe_preserves_reading_truth_as_plain_data():
    row = reading({
        "system.temp.cpu_c": 48.5,
        "system.temp.cpu_c.quality": "captured",
        "system.temp.cpu_c.source": "fixture",
        "system.temp.cpu_c.age_s": 3.0,
    }, "system.temp.cpu_c", unit="°C")

    safe = json_safe({"reading": row})
    assert safe["reading"]["key"] == "system.temp.cpu_c"
    assert safe["reading"]["value"] == 48.5
    assert safe["reading"]["quality"] == "captured"
    assert safe["reading"]["source"] == "fixture"
    assert json.loads(json.dumps(safe)) == safe


def test_json_safe_recurses_dataclasses_collections_and_paths():
    safe = json_safe({
        "nested": _Nested("proof", Path("artifacts/proof.png")),
        "values": (1, 2, {3, 4}),
    })
    assert safe["nested"] == {"name": "proof", "path": "artifacts/proof.png"}
    assert safe["values"][0:2] == [1, 2]
    assert sorted(safe["values"][2]) == [3, 4]
    json.dumps(safe)
