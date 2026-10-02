#!/usr/bin/env python3
"""PreToolUse guard: deny Bash commands that merge PRs in this repo (AGENTS.md §4).

Both agents act as `patrickato`, so GitHub cannot stop an AI merge; this is a
best-effort safety net against *accidental* merges, not a sandbox. The real
guarantee is separate agent identities (AGENTS.md §5).

It reads the PreToolUse payload as JSON on stdin and prints `deny` or `allow`.
The decision is structural rather than a raw-string scan: it joins line
continuations, drops inert (quoted) heredoc bodies, recurses into the shell
constructs that actually execute a command -- `$(...)`/backtick substitutions
(respecting single-quoting), `bash -c`/`eval`, unquoted heredoc substitutions,
operators and subshells -- and, for each segment, finds the command *position*
by stripping env assignments and wrappers (sudo/env/nice/xargs/timeout/..., with
their options). A merge is denied when that command is:

  * `gh ... pr merge ...`,
  * `gh api` / curl / wget hitting a REST `.../pulls/<n>/merge` endpoint, or
  * a GraphQL merge/auto-merge/enqueue mutation.

Because it looks at the command position, text that merely mentions the words --
`rg 'gh pr merge'`, `echo gh pr merge`, a documentation heredoc -- is allowed.
"""
import json
import re
import shlex
import sys

REST = re.compile(r"pulls/\S*?/merge\b|pulls/.+?/merge\b")
GQL = re.compile(r"mergePullRequest|enablePullRequestAutoMerge|enqueuePullRequest")
GH_FALLBACK = re.compile(r"\bgh\b.*\bpr\s+merge\b")

SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
HTTP = {"curl", "wget", "http", "https", "xh"}
CONTROL = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}
WRAPPERS = {"sudo", "doas", "env", "nice", "ionice", "chrt", "nohup", "stdbuf",
            "timeout", "setsid", "command", "exec", "builtin", "time", "xargs"}
# Wrapper options that consume the following token as their argument (exact match;
# a combined form like `-n5` is a single token and needs no extra skip).
ARG_OPTS = {
    "env": {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"},
    "nice": {"-n", "--adjustment"},
    "ionice": {"-c", "-n", "-p"},
    "chrt": {"-T", "-R"},
    "sudo": {"-u", "--user", "-g", "--group", "-U", "-C", "-D", "--chdir",
             "-h", "-p", "--prompt", "-r", "-t", "-T", "-R"},
    "doas": {"-u", "-C"},
    "timeout": {"-s", "--signal", "-k", "--kill-after"},
    "stdbuf": {"-i", "--input", "-o", "--output", "-e", "--error"},
    "time": {"-o", "--output", "-f", "--format"},
    "xargs": {"-a", "--arg-file", "-E", "-e", "--eof", "-I", "-i", "-L",
              "--max-lines", "-n", "--max-args", "-P", "--max-procs", "-s",
              "--max-chars", "-d", "--delimiter"},
}
ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*", re.DOTALL)
SHELL_C = re.compile(r"-[A-Za-z]*c")  # -c, and clusters like -lc / -ec
MAX_DEPTH = 25


def base(tok):
    return tok.rsplit("/", 1)[-1]


def strip_heredocs(text):
    """Remove heredoc bodies. Return (text_without_bodies, unquoted_body_texts).

    A quoted delimiter (`<<'EOF'`) makes the body inert, so it is simply dropped.
    An unquoted delimiter still expands `$(...)`/backticks, so its body is handed
    back for substitution scanning.
    """
    lines, out, bodies, i = text.split("\n"), [], [], 0
    while i < len(lines):
        out.append(lines[i])
        m = re.search(r"<<-?\s*([\"\x27]?)([A-Za-z_][A-Za-z0-9_]*)\1", lines[i])
        i += 1
        if m:
            quoted, body = bool(m.group(1)), []
            while i < len(lines) and lines[i].strip() != m.group(2):
                body.append(lines[i])
                i += 1
            i += 1  # skip the terminator line
            if not quoted:
                bodies.append("\n".join(body))
    return "\n".join(out), bodies


def extract_subs(text):
    """Blank out `$(...)` and backtick substitutions and return (clean, inner_codes).

    Single-quoted spans are inert, so their contents are left untouched and not
    returned. Each substitution is replaced by a space so the surrounding text
    still tokenizes and a split endpoint such as `pulls/$(id)/merge` still reads
    as `pulls/ /merge`.
    """
    out, buf, i, n, q = [], [], 0, len(text), None
    while i < n:
        ch = text[i]
        if q == "'":
            buf.append(ch)
            if ch == "'":
                q = None
            i += 1
        elif ch == "'" and q is None:
            q = "'"
            buf.append(ch)
            i += 1
        elif ch == '"':
            q = None if q == '"' else '"'
            buf.append(ch)
            i += 1
        elif ch == "\\" and i + 1 < n:
            buf.append(ch)
            buf.append(text[i + 1])
            i += 2
        elif ch == "$" and i + 1 < n and text[i + 1] == "(":
            depth, j = 1, i + 2
            while j < n and depth:
                depth += (text[j] == "(") - (text[j] == ")")
                j += 1
            out.append(text[i + 2:j - 1])
            buf.append(" ")
            i = j
        elif ch == "`":
            j = i + 1
            while j < n and text[j] != "`":
                j += 2 if text[j] == "\\" else 1
            out.append(text[i + 1:j])
            buf.append(" ")
            i = j + 1
        else:
            buf.append(ch)
            i += 1
    return "".join(buf), out


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


def command(tokens):
    """Return [program, *args] after stripping env assignments and wrapper prefixes."""
    toks = list(tokens)
    while toks and ASSIGN.fullmatch(toks[0]):
        toks = toks[1:]
    if not toks:
        return []
    w = base(toks[0])
    if w in WRAPPERS:
        rest, argopts, i = toks[1:], ARG_OPTS.get(w, set()), 0
        while i < len(rest) and rest[i].startswith("-"):
            opt = rest[i]
            i += 1
            if opt == "--":
                break
            if opt in argopts and i < len(rest):
                i += 1  # skip this option's argument
        if w == "env":  # env NAME=VALUE ... command
            while i < len(rest) and ASSIGN.fullmatch(rest[i]):
                i += 1
        if w == "timeout" and i < len(rest):
            i += 1  # the leading positional DURATION
        return command(rest[i:])
    return toks


def blocked(text, depth=0):
    if depth > MAX_DEPTH:
        return True  # pathological nesting: fail safe
    text = text.replace("\\\n", "")  # the shell removes backslash-newline continuations
    clean, bodies = strip_heredocs(text)
    clean, subs = extract_subs(clean)
    for body in bodies:  # unquoted heredoc bodies: only their substitutions execute
        subs.extend(extract_subs(body)[1])
    for sub in subs:
        if blocked(sub, depth + 1):
            return True
    try:
        lex = shlex.shlex(clean, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        return bool(REST.search(clean) or GQL.search(clean) or GH_FALLBACK.search(clean))
    for seg in segments(tokens):
        cmd = command(seg)
        if not cmd:
            continue
        prog, args = base(cmd[0]), cmd[1:]
        if prog in SHELLS:
            for k, tok in enumerate(args):
                if SHELL_C.fullmatch(tok) and k + 1 < len(args):
                    if blocked(args[k + 1], depth + 1):
                        return True
                    break
        elif prog == "eval":
            if blocked(" ".join(args), depth + 1):
                return True
        elif prog == "gh":
            words = [a for a in args if not a.startswith("-")]
            if any(words[k] == "pr" and words[k + 1] == "merge" for k in range(len(words) - 1)):
                return True
            if "api" in words and (REST.search(" ".join(seg)) or GQL.search(" ".join(seg))):
                return True
        elif prog in HTTP:
            if REST.search(" ".join(seg)) or GQL.search(" ".join(seg)):
                return True
    return False


def main():
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    print("deny" if blocked(cmd) else "allow")


if __name__ == "__main__":
    main()
