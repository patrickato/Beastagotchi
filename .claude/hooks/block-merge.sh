#!/bin/bash
# PreToolUse guard for Bash: agents never merge PRs in this repo (AGENTS.md §4). The deny rules
# in settings.json cover the GitHub MCP merge tools and `gh pr merge`; this guard also catches
# merges and auto-merge sent through `gh api`, curl/wget or `bash -c`, however the PR number or
# endpoint is spelled. It parses commands (quotes, `;`/`&&`/`|`, heredocs, line continuations) so
# text that merely mentions these words, such as `rg 'gh pr merge'`, is not blocked. It is a
# safety net against accidental merges, not a sandbox; separate agent identities are the real
# fix (AGENTS.md §5).
set -euo pipefail

input=$(cat)
deny='{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Agents never merge PRs in this repo (AGENTS.md §4). Patrick merges."}}'

verdict=$(printf '%s' "$input" | python3 -c '
import json, re, shlex, sys

REST = re.compile(r"pulls/\S*?/merge\b|pulls/.+?/merge\b")
GQL = re.compile(r"mergePullRequest|enablePullRequestAutoMerge")
SHELLS = {"bash", "sh", "zsh", "dash"}
HTTP = {"curl", "wget", "http", "https", "xh"}
CONTROL = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}

def base(tok):
    # The command word may be a path (/usr/bin/gh) or a quoted phrase; compare on the basename.
    return tok.rsplit("/", 1)[-1]

def strip_heredocs(text):
    # Drop heredoc bodies so documentation of these tokens inside a heredoc is not matched.
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

def segments(tokens):
    seg, out = [], []
    for tok in tokens:
        if tok in CONTROL:
            if seg:
                out.append(seg)
            seg = []
        else:
            seg.append(tok)
    if seg:
        out.append(seg)
    return out

def words(seg):
    return [t for t in seg if not t.startswith("-")]

def gh_pr_merge(seg):
    # A standalone `gh` token (wrappers like env/sudo/nice/xargs/timeout may precede it, with any
    # options) whose later non-flag words include `pr` then `merge`. A quoted phrase such as
    # `rg \x27gh pr merge\x27` is one token, so its basename is not `gh` and it is not matched.
    for i, tok in enumerate(seg):
        if base(tok) == "gh":
            w = words(seg[i + 1:])
            if any(w[k] == "pr" and w[k + 1] == "merge" for k in range(len(w) - 1)):
                return True
    return False

def shell_recurse(seg):
    # Re-check the code carried by `bash -c <cmd>` / `eval <cmd>` (wrappers may precede the shell).
    for i, tok in enumerate(seg):
        b = base(tok)
        if b in SHELLS:
            for j in range(i + 1, len(seg)):
                if seg[j] == "-c" and j + 1 < len(seg):
                    if blocked(seg[j + 1]):
                        return True
                    break
        if b == "eval" and blocked(" ".join(seg[i + 1:])):
            return True
    return False

def has_client(tokens):
    # An HTTP client, or `gh api`, anywhere in the command gates the REST/GraphQL check below.
    if any(base(t) in HTTP for t in tokens):
        return True
    return any(base(t) == "gh" for t in tokens) and any(w == "api" for w in words(tokens))

def blocked(text):
    text = text.replace("\\\n", "")   # the shell removes backslash-newline continuations
    text = strip_heredocs(text)
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        # Unbalanced quotes: fall back to a conservative scan of this text.
        return bool(REST.search(text) or GQL.search(text)
                    or re.search(r"\bgh\b.*\bpr\s+merge\b", text))
    for seg in segments(tokens):
        if gh_pr_merge(seg) or shell_recurse(seg):
            return True
    # Variable- or substitution-built endpoints (pulls/$n/merge, pulls/$(...)/merge) are matched on
    # the text, since tokenizing splits a command substitution; the client gate stops false hits on
    # quoted paths in ordinary commands.
    if has_client(tokens) and (REST.search(text) or GQL.search(text)):
        return True
    return False

cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
print("deny" if blocked(cmd) else "allow")
' 2>/dev/null) || verdict=fallback

if [ "$verdict" = fallback ]; then
  # No usable python3: fall back to a conservative scan of the raw payload (joins continuations).
  if printf '%s' "$input" | tr -d "\\\\" | grep -Eiq 'gh[^|;&]*[[:space:]]pr[[:space:]]+merge|pulls/[^[:space:]]*/merge|mergePullRequest|enablePullRequestAutoMerge'; then
    verdict=deny
  fi
fi
if [ "$verdict" = deny ]; then
  printf '%s\n' "$deny"
fi
exit 0
