import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / ".claude" / "hooks" / "block-merge.sh"

DENY = [
    "gh pr merge 31 --merge",
    "gh -R patrickato/Beastagotchi pr merge 31 --auto --merge",
    "gh api -X PUT repos/patrickato/Beastagotchi/pulls/31/merge",
    "n=31; gh api -X PUT repos/{owner}/{repo}/pulls/$n/merge",
    "gh api -X PUT repos/o/r/pulls/$(echo 31)/merge",
    "gh api graphql -f query='mutation { enablePullRequestAutoMerge(input: {}) { clientMutationId } }'",
    'bash -c "gh pr merge 31"',
    "curl -X PUT https://api.github.com/repos/o/r/pulls/31/merge",
    "echo 31 | xargs gh pr merge",
    # round 3: wrappers with their own options must not hide the guarded command
    "env -i gh pr merge 31",
    "nice -n 5 gh pr merge 31",
    "echo 31 | xargs -n1 gh pr merge",
    "sudo -u ci gh pr merge 31",
    "timeout 10 gh pr merge 31",
    "env bash -c 'gh pr merge 31'",
    # round 3: backslash-newline continuations are joined before parsing
    "gh pr \\\nmerge 31",
    "curl -X PUT \\\n https://api.github.com/repos/o/r/pulls/31/merge",
    "gh api -X PUT \\\n repos/o/r/pulls/31/merge",
    # round 4: shell option clusters carry the command flag
    "bash -lc 'gh pr merge 31'",
    "sh -ec 'gh pr merge 31'",
    # round 4: command substitutions (quoted, unquoted, backtick) execute the merge
    'result="$(gh pr merge 31)"',
    "echo \"`gh pr merge 31`\"",
    "cat <<EOF\n$(gh pr merge 31)\nEOF",
    # round 4: the merge-queue enqueue mutation
    "gh api graphql -f query='mutation { enqueuePullRequest(input: {}) { clientMutationId } }'",
]

ALLOW = [
    "git merge origin/integration/v0.19",
    "gh pr view 31 --json state",
    "rg 'gh pr merge' .claude",
    "printf '%s\\n' 'gh pr merge is forbidden'",
    "cat > /tmp/notes.md <<'EOF'\nUse mergePullRequest carefully\ngh pr merge 31\nEOF",
    'git commit -m "gh pr merge is blocked by the guard"',
    # round 3: still allow searching/testing the guard itself, and unrelated merges
    "rg 'pulls/31/merge' .claude/hooks",
    "env FOO=bar git merge --no-ff origin/integration/v0.19",
    "grep -r enablePullRequestAutoMerge tests",
    # round 4: `gh`/endpoints as plain data, not in command position
    "echo gh pr merge",
    "curl https://example.com; rg 'pulls/31/merge' .",
    "echo 'docs: $(gh pr merge)'",
]


def _decision(command):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    out = subprocess.run(["bash", str(GUARD)], input=payload, capture_output=True, text=True, check=True).stdout
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else "allow"


@pytest.mark.parametrize("command", DENY)
def test_merge_guard_denies_merges(command):
    assert _decision(command) == "deny"


@pytest.mark.parametrize("command", ALLOW)
def test_merge_guard_allows_commands_that_only_mention_merging(command):
    assert _decision(command) == "allow"
