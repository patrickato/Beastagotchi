from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ci_runs_on_pushes_to_main_and_the_active_line_and_on_every_pull_request():
    workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text()
    assert "on:\n  push:\n    branches: [main, integration/v0.19]\n  pull_request:\n" in workflow
