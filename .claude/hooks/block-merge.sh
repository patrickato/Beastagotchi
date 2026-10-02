#!/bin/bash
# PreToolUse guard for Bash: agents never merge PRs in this repo (AGENTS.md §4). The deny rules
# in settings.json cover the GitHub MCP merge tools and `gh pr merge`; this also catches merges
# and auto-merge sent straight to the GitHub API (REST or GraphQL), e.g. via `gh api` or curl.
set -euo pipefail

input=$(cat)
# Check only the command when python3 can parse the payload; otherwise check the raw payload.
cmd=$(printf '%s' "$input" | python3 -c 'import json, sys; print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))' 2>/dev/null) || cmd=$input

if printf '%s' "$cmd" | grep -Eiq 'gh[^|;&]*[[:space:]]pr[[:space:]]+merge|/pulls/[0-9]+/merge|mergePullRequest|enablePullRequestAutoMerge'; then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Agents never merge PRs in this repo (AGENTS.md §4). Patrick merges."}}'
fi
exit 0
