#!/bin/bash
# PreToolUse guard for Bash: agents never merge PRs in this repo (AGENTS.md §4). The deny rules
# in settings.json cover the GitHub MCP merge tools and `gh pr merge`; this guard also catches
# merges and auto-merge sent through `gh api`, curl/wget or `bash -c`, however the PR number or
# endpoint is spelled. It parses commands (quotes, `;`/`&&`/`|`, heredocs) so text that merely
# mentions these words, such as `rg 'gh pr merge'`, is not blocked. It is a safety net against
# accidental merges, not a sandbox; separate agent identities are the real fix (AGENTS.md §5).
set -euo pipefail

input=$(cat)
deny='{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Agents never merge PRs in this repo (AGENTS.md §4). Patrick merges."}}'

verdict=$(printf '%s' "$input" | python3 -c '
import json, re, shlex, sys

REST = re.compile(r"pulls/\S*?/merge\b|pulls/.+?/merge\b")
GQL = re.compile(r"mergePullRequest|enablePullRequestAutoMerge")
SKIP = {"sudo", "command", "env", "time", "nice", "nohup", "exec", "builtin", "xargs"}
SHELLS = {"bash", "sh", "zsh", "dash"}
HTTP = {"curl", "wget", "http", "https", "xh"}
CONTROL = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}

def strip_heredocs(text):
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        out.append(lines[i])
        m = re.search(r"<<-?\s*([\x27\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", lines[i])
        i += 1
        if m:
            while i < len(lines) and lines[i].strip() != m.group(2):
                i += 1
            i += 1
    return "\n".join(out)

def blocked_segment(argv, line):
    while argv and (argv[0] in SKIP or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", argv[0])):
        argv = argv[1:]
    if not argv:
        return False
    prog, rest = argv[0].rsplit("/", 1)[-1], argv[1:]
    if prog in SHELLS and "-c" in rest and rest.index("-c") + 1 < len(rest):
        return blocked(rest[rest.index("-c") + 1])
    if prog == "eval":
        return blocked(" ".join(rest))
    if prog == "gh":
        words = [a for a in rest if not a.startswith("-")]
        if any(words[k] == "pr" and words[k + 1] == "merge" for k in range(len(words) - 1)):
            return True
        if "api" in words:
            return bool(REST.search(line) or GQL.search(line))
    if prog in HTTP:
        return bool(REST.search(line) or GQL.search(line))
    return False

def blocked(text):
    for line in strip_heredocs(text).split("\n"):
        try:
            lex = shlex.shlex(line, posix=True, punctuation_chars=True)
            lex.whitespace_split = True
            tokens = list(lex)
        except ValueError:
            if REST.search(line) or GQL.search(line) or re.search(r"\bgh\b.*\bpr\s+merge\b", line):
                return True
            continue
        seg = []
        for tok in tokens + [";"]:
            if tok in CONTROL:
                if seg and blocked_segment(seg, line):
                    return True
                seg = []
            else:
                seg.append(tok)
    return False

cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
print("deny" if blocked(cmd) else "allow")
' 2>/dev/null) || verdict=fallback

if [ "$verdict" = fallback ]; then
  # No usable python3: fall back to a conservative scan of the raw payload.
  if printf '%s' "$input" | grep -Eiq 'gh[^|;&]*[[:space:]]pr[[:space:]]+merge|pulls/[^[:space:]]*/merge|mergePullRequest|enablePullRequestAutoMerge'; then
    verdict=deny
  fi
fi
if [ "$verdict" = deny ]; then
  printf '%s\n' "$deny"
fi
exit 0
