import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "v019_physical_acceptance.sh"


def _embedded_preflight_python() -> str:
    text = SCRIPT.read_text()
    marker = 'PREFLIGHT_DEPLOYMENT="$out/deployment-provenance.json" PYTHONPATH="$CORE_ROOT:$UI_ROOT:$BEAST_SITE" "$PY" - <<\'PY\' > "$out/preflight.json"\n'
    assert marker in text, "physical acceptance preflight heredoc marker changed"
    tail = text.split(marker, 1)[1]
    block, sep, _ = tail.partition("\nPY\n}")
    assert sep, "physical acceptance preflight heredoc terminator not found"
    return block


def test_embedded_preflight_python_executes_without_missing_imports(tmp_path):
    block = _embedded_preflight_python()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["PREFLIGHT_DEPLOYMENT"] = str(tmp_path / "no-deployment-provenance.json")

    proc = subprocess.run(
        [sys.executable, "-c", block],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert "ts" in payload
    assert "fingerprints" in payload
