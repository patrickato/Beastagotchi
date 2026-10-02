#!/bin/bash
# PreToolUse guard for Bash: agents never merge PRs in this repo (AGENTS.md §4). The deny rules in
# settings.json cover the GitHub MCP merge tools and `gh pr merge`; this guard also catches merges
# and auto-merge sent through `gh api`, curl/wget, `bash -c`, substitutions or wrappers, however the
# PR number or endpoint is spelled. The parsing lives in block-merge.py (so it can be read and
# tested on its own); this wrapper feeds it the PreToolUse payload and emits the deny decision. It
# is a safety net against accidental merges, not a sandbox; separate agent identities are the real
# fix (AGENTS.md §5).
set -euo pipefail

input=$(cat)
deny='{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Agents never merge PRs in this repo (AGENTS.md §4). Patrick merges."}}'
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

verdict=$(printf '%s' "$input" | python3 "$here/block-merge.py" 2>/dev/null) || verdict=fallback

if [ "$verdict" = fallback ]; then
  # No usable python3: fall back to a conservative scan of the raw payload (joins continuations).
  if printf '%s' "$input" | tr -d '\\' | grep -Eiq 'gh[^|;&]*[[:space:]]pr[[:space:]]+merge|pulls/[^[:space:]]*/merge|mergePullRequest|enablePullRequestAutoMerge|enqueuePullRequest'; then
    verdict=deny
  fi
fi
if [ "$verdict" = deny ]; then
  printf '%s\n' "$deny"
fi
exit 0
