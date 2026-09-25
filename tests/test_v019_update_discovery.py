from __future__ import annotations

import json
from pathlib import Path

from beastcore.updates import UpdatePolicyEngine
from beastcore.update_sources import TrustedSourcePolicy, normalize_repo


class FakeState:
    def __init__(self, data):
        self.data = dict(data)

    def get(self, key, default=None):
        return self.data.get(key, default)


class FakeChecker:
    def __init__(self):
        self.calls = []

    def latest(self, repo):
        self.calls.append(repo)
        versions = {
            "patrickato/Beastagotchi": "v0.20.0",
            "jayofelony/pwnagotchi": "v2.9.5.9",
            "Korrie71/pwnagotchi-theme-manager": "v3.0.0",
        }
        return {
            "repository": repo,
            "version": versions.get(repo, "v1.0.0"),
            "published_at": "2026-09-23T00:00:00Z",
            "assets": [
                {"name": "release.tar.gz", "size_bytes": 1000, "digest": "", "download_url": "https://github.com/example/release.tar.gz"},
                {"name": "release.tar.gz.sha256", "size_bytes": 100, "digest": "", "download_url": "https://github.com/example/release.tar.gz.sha256"}
            ],
            "verification": {
                "sha256_digest_asset": False,
                "sha256_sidecar_asset": True,
                "sha256_path_available": True,
            },
        }


def base_state(**extra):
    row = {
        "system.beast_version": "0.19.0",
        "pwnagotchi.version": "2.9.5.9",
        "plugins.catalog": [],
        "packs.items": [],
        "dock.docked": True,
        "network.internet.state": "online",
    }
    row.update(extra)
    return FakeState(row)


def test_normalize_repo_accepts_repo_and_github_url():
    assert normalize_repo("patrickato/Beastagotchi") == "patrickato/Beastagotchi"
    assert normalize_repo("https://github.com/Korrie71/pwnagotchi-theme-manager/releases") == "Korrie71/pwnagotchi-theme-manager"
    assert normalize_repo("https://example.com/not-github") == ""


def test_builtin_sources_are_trusted(tmp_path: Path):
    policy = TrustedSourcePolicy(tmp_path/"trust.json")
    assert policy.trusted("patrickato/Beastagotchi")
    assert policy.trusted("Korrie71/pwnagotchi-theme-manager")
    assert not policy.trusted("randomperson/randompack")


def test_docked_online_update_check_is_cached_and_read_only(tmp_path: Path):
    checker = FakeChecker()
    now = [1000.0]
    engine = UpdatePolicyEngine(
        base_state(),
        path=str(tmp_path/"policies.json"),
        cache_path=str(tmp_path/"metadata.json"),
        trust_path=str(tmp_path/"trust.json"),
        checker=checker,
        clock=lambda: now[0],
        check_interval_sec=3600,
    )
    first = engine.tick()
    items = {x["id"]: x for x in first["updates.components"]}
    assert items["beastagotchi"]["update_available"] is True
    assert items["beastagotchi"]["available_version"] == "v0.20.0"
    assert items["beastagotchi"]["verification_available"] is True
    assert items["beastagotchi"]["auto_stage_eligible"] is True
    assert items["beastagotchi"]["auto_install_eligible"] is False
    assert items["pwnagotchi"]["update_available"] is False
    assert first["updates.download_executor_enabled"] is True
    assert first["updates.pack_auto_install_enabled"] is True
    assert first["updates.executor_enabled"] is False
    assert first["updates.executor_scope"] == "generic_component_install_locked"
    assert len(checker.calls) == 2

    # Within the check interval, cached metadata is reused and no network lookup occurs.
    second = engine.tick()
    assert len(checker.calls) == 2
    assert second["updates.check_state"] == "cached_or_not_due"


def test_untrusted_pack_source_is_not_fetched_automatically(tmp_path: Path):
    checker = FakeChecker()
    state = base_state(**{
        "packs.items": [{
            "id": "community-theme",
            "label": "Community Theme",
            "version": "0.1",
            "origin": "installed",
            "requirements_met": True,
            "blockers": [],
            "source": {"type": "github_release", "url": "https://github.com/randomperson/randompack/releases"},
        }]
    })
    engine = UpdatePolicyEngine(
        state,
        cache_path=str(tmp_path/"metadata.json"),
        trust_path=str(tmp_path/"trust.json"),
        checker=checker,
        clock=lambda:1000.0,
    )
    patch = engine.tick()
    item = next(x for x in patch["updates.components"] if x["id"] == "pack:community-theme")
    assert item["source_trusted"] is False
    assert item["last_result"] == "source_untrusted"
    assert "randomperson/randompack" not in [x.lower() for x in checker.calls]


def test_user_trust_file_can_allow_community_repo(tmp_path: Path):
    trust = tmp_path/"trust.json"
    trust.write_text(json.dumps({"github_repositories":["randomperson/randompack"]}))
    checker = FakeChecker()
    state = base_state(**{
        "packs.items": [{
            "id": "community-theme",
            "label": "Community Theme",
            "version": "0.1",
            "origin": "installed",
            "requirements_met": True,
            "blockers": [],
            "source": {"type": "github_release", "url": "https://github.com/randomperson/randompack/releases"},
        }]
    })
    engine = UpdatePolicyEngine(
        state,
        cache_path=str(tmp_path/"metadata.json"),
        trust_path=str(trust),
        checker=checker,
        clock=lambda:1000.0,
    )
    patch = engine.tick()
    item = next(x for x in patch["updates.components"] if x["id"] == "pack:community-theme")
    assert item["source_trusted"] is True
    assert "randomperson/randompack" in [x.lower() for x in checker.calls]
