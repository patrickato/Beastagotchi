#!/usr/bin/env python3
"""PreToolUse guard: deny Bash commands that merge PRs in this repo (AGENTS.md §4).

Both agents act as `patrickato`, so GitHub cannot stop an AI merge; this is a
best-effort safety net against *accidental* merges, not a sandbox. The real
guarantee is separate agent identities (AGENTS.md §5).

It reads the PreToolUse payload as JSON on stdin and prints `deny` or `allow`.
The decision is structural. A quote-aware preprocessor removes `#` comments,
normalizes ANSI-C (`$'…'`/`$"…"`) quoting, extracts the substitutions that
execute a command (`$(…)`, backticks, `<(…)`/`>(…)`), and splits on newlines and
operators. Heredoc bodies fed to a shell are recursed as scripts; other heredoc
bodies are inert (quoted) or scanned for substitutions (unquoted). For each
command segment it finds the program *position* by dropping assignments,
redirections, reserved words and wrappers (sudo/env/xargs/timeout/…, with their
options), then denies when that program is:

  * `gh … pr merge …` (option values between the words are consumed);
  * `gh api` / curl / wget doing a **PUT** on a REST `…/pulls/<n>/merge` endpoint
    (a GET there only reads merge status, so it stays allowed); or
  * a GraphQL merge / auto-merge / enqueue mutation.

Because it looks at the program position, text that merely mentions the words --
`rg 'gh pr merge'`, `echo gh pr merge`, a `# $(gh pr merge)` comment, a
documentation heredoc -- is allowed.

Boundary: this is static analysis, so it cannot resolve values known only at run
time -- an indirect command name (`GH=gh; $GH pr merge`), a verb held in a
variable (`m=merge; gh pr $m`), or a script piped/decoded into a shell
(`printf … | bash`, `eval "$(… base64 -d)"`). Catching those would require
executing the command. That residual gap is why the block is defence in depth
(MCP deny rules, the `gh pr merge` deny rule, this guard, agent instructions) and
why the real control is separate agent identities (AGENTS.md §5), not this hook.
"""
import json
import re
import shlex
import sys

REST = re.compile(r"pulls/\S*?/merge\b|pulls/.+?/merge\b")
GQL = re.compile(r"mergePullRequest|enablePullRequestAutoMerge|enqueuePullRequest")
GH_FALLBACK = re.compile(r"\bgh\b.*\bpr\s+merge\b")

SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
EVAL = {"eval"}
HTTP = {"curl", "wget", "http", "https", "xh"}
CONTROL = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}
RESERVED = {"if", "then", "elif", "else", "fi", "do", "done", "while", "until",
            "for", "case", "esac", "in", "{", "}", "!", "function", "select", "coproc"}
WRAPPERS = {"sudo", "doas", "env", "nice", "ionice", "chrt", "nohup", "stdbuf",
            "timeout", "setsid", "command", "exec", "builtin", "time", "xargs"}
REDIR = {">", ">>", "<", ">|", "<>", ">&", "<&", "&>", "&>>", "<<", "<<-"}
# Wrapper options that consume the following token as their argument.
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
# gh inherited/flags that take a separate value, so they don't hide a subcommand.
GH_ARG_OPTS = {"-R", "--repo", "-F", "--field", "-f", "--raw-field", "-H",
               "--header", "-q", "--jq", "-t", "--template", "-X", "--method",
               "--hostname", "--input", "-b", "--body", "-B", "--body-file", "--cache"}
ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*", re.DOTALL)
SHELL_C = re.compile(r"-[A-Za-z]*c")  # -c, and clusters like -lc / -ec
ANSI_C = {"n": " ", "t": " ", "r": " ", "\\": "\\", "'": "'", '"': '"'}
MAX_DEPTH = 25


def base(tok):
    return tok.rsplit("/", 1)[-1]


def read_ansi_c(text, i):
    """From just after `$'`, decode to the closing quote. Return (literal, index)."""
    buf, n = [], len(text)
    while i < n and text[i] != "'":
        if text[i] == "\\" and i + 1 < n:
            buf.append(ANSI_C.get(text[i + 1], text[i + 1]))
            i += 2
        else:
            buf.append(text[i])
            i += 1
    return "".join(buf), i + 1


def quote_single(s):
    return "'" + s.replace("'", "'\\''") + "'"


def read_paren(text, i):
    """From just after an opening `(`, find the matching `)`, respecting quotes."""
    depth, n, q, start = 1, len(text), None, i
    while i < n and depth:
        ch = text[i]
        if q:
            if ch == "\\" and q == '"' and i + 1 < n:
                i += 2
                continue
            if ch == q:
                q = None
            i += 1
            continue
        if ch in ("'", '"'):
            q = ch
        elif ch == "\\" and i + 1 < n:
            i += 2
            continue
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if not depth:
                return text[start:i], i + 1
        i += 1
    return text[start:i], i


def strip_comments(text):
    """Remove `#` comments at top level (outside quotes, substitutions, backticks)."""
    out, i, n, q, depth, bt = [], 0, len(text), None, 0, False
    while i < n:
        ch = text[i]
        if q == "'":
            out.append(ch)
            if ch == "'":
                q = None
            i += 1
        elif q == '"':
            if ch == "\\" and i + 1 < n:
                out.append(ch + text[i + 1])
                i += 2
                continue
            out.append(ch)
            if ch == '"':
                q = None
            i += 1
        elif ch == "\\" and i + 1 < n:
            out.append(ch + text[i + 1])
            i += 2
        elif ch in ("'", '"'):
            q = ch
            out.append(ch)
            i += 1
        elif ch == "`":
            bt = not bt
            out.append(ch)
            i += 1
        elif ch == "$" and i + 1 < n and text[i + 1] == "(":
            depth += 1
            out.append("$(")
            i += 2
        elif ch == "(":
            depth += 1
            out.append(ch)
            i += 1
        elif ch == ")":
            depth = max(0, depth - 1)
            out.append(ch)
            i += 1
        elif ch == "#" and depth == 0 and not bt and (not out or out[-1][-1] in " \t\n;&|()"):
            while i < n and text[i] != "\n":
                i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def normalize_ansic(text):
    """Rewrite ANSI-C `$'…'` and `$"…"` to ordinary quoting that shlex understands."""
    out, i, n, q = [], 0, len(text), None
    while i < n:
        ch = text[i]
        if q:
            out.append(ch)
            if ch == q:
                q = None
            i += 1
        elif ch == "\\" and i + 1 < n:
            out.append(ch + text[i + 1])
            i += 2
        elif ch == "$" and i + 1 < n and text[i + 1] == "'":
            lit, j = read_ansi_c(text, i + 2)
            out.append(quote_single(lit))
            i = j
        elif ch == "$" and i + 1 < n and text[i + 1] == '"':
            out.append('"')
            q = '"'
            i += 2
        elif ch in ("'", '"'):
            q = ch
            out.append(ch)
            i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def extract_subs(text):
    """Blank `$(…)`, `<(…)`/`>(…)` and backtick substitutions; return (clean, inner_codes).

    Single-quoted spans are inert, so their contents are left untouched. Each
    substitution becomes a space so a split endpoint like `pulls/$(id)/merge`
    still reads as `pulls/ /merge`.
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
            buf.append(ch + text[i + 1])
            i += 2
        elif (ch == "$" or ch in "<>") and i + 1 < n and text[i + 1] == "(":
            inner, j = read_paren(text, i + 2)
            out.append(inner)
            buf.append(" ")
            i = j
        elif ch == "`":
            j, m = i + 1, len(text)
            while j < m and text[j] != "`":
                j += 2 if text[j] == "\\" else 1
            out.append(text[i + 1:j])
            buf.append(" ")
            i = j + 1
        else:
            buf.append(ch)
            i += 1
    return "".join(buf), out


def opener_is_shell(pre):
    try:
        toks = shlex.split(pre)
    except ValueError:
        toks = pre.split()
    cmd = command(toks)
    return bool(cmd) and base(cmd[0]) in (SHELLS | EVAL)


def strip_heredocs(text):
    """Return (text_without_bodies, shell_script_bodies, unquoted_bodies).

    A body redirected into a shell is executed as a script. A quoted delimiter
    makes an ordinary body inert; an unquoted one still expands substitutions.
    """
    lines, out, scripts, unquoted, i = text.split("\n"), [], [], [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = re.search(r"<<-?\s*([\"\x27]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
        i += 1
        if m:
            quoted, body = bool(m.group(1)), []
            while i < len(lines) and lines[i].strip() != m.group(2):
                body.append(lines[i])
                i += 1
            i += 1  # terminator line
            text_body = "\n".join(body)
            if opener_is_shell(line[:m.start()]):
                scripts.append(text_body)
            elif not quoted:
                unquoted.append(text_body)
    return "\n".join(out), scripts, unquoted


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


def strip_redirects(tokens):
    """Drop redirection operators and their targets (an optional leading fd too)."""
    out, i, n = [], 0, len(tokens)
    while i < n:
        tok = tokens[i]
        if re.fullmatch(r"\d+", tok) and i + 1 < n and tokens[i + 1] in REDIR:
            i += 3  # fd, operator, target
        elif tok in REDIR:
            i += 2  # operator, target
        else:
            out.append(tok)
            i += 1
    return out


def command(tokens):
    """Return [program, *args] after dropping assignments, reserved words and wrappers."""
    toks = list(tokens)
    while toks and (ASSIGN.fullmatch(toks[0]) or base(toks[0]) in RESERVED):
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
                i += 1
        if w == "env":
            while i < len(rest) and ASSIGN.fullmatch(rest[i]):
                i += 1
        if w == "timeout" and i < len(rest):
            i += 1  # the positional DURATION
        return command(rest[i:])
    return toks


def positional(args, arg_opts):
    """Non-option words, with option-values removed, so flags can't hide a word."""
    out, i = [], 0
    while i < len(args):
        a = args[i]
        if a.startswith("-"):
            i += 2 if a in arg_opts else 1
        else:
            out.append(a)
            i += 1
    return out


def has_put(seg):
    up = {t.upper() for t in seg}
    return "PUT" in up or bool(up & {"-XPUT", "--METHOD=PUT", "--REQUEST=PUT", "-X=PUT"})


def seg_blocked(seg, depth):
    cmd = command(strip_redirects(seg))
    if not cmd:
        return False
    prog, args = base(cmd[0]), cmd[1:]
    if prog in SHELLS:
        for k, tok in enumerate(args):
            if (SHELL_C.fullmatch(tok) or tok == "<<<") and k + 1 < len(args):
                return blocked(args[k + 1], depth + 1)
        return False
    if prog in EVAL:
        return blocked(" ".join(args), depth + 1)
    if prog == "gh":
        words = positional(args, GH_ARG_OPTS)
        if any(words[k] == "pr" and words[k + 1] == "merge" for k in range(len(words) - 1)):
            return True
        if "api" in words:
            joined = " ".join(seg)
            return bool(GQL.search(joined) or (REST.search(joined) and has_put(seg)))
        return False
    if prog in HTTP:
        joined = " ".join(seg)
        return bool(GQL.search(joined) or (REST.search(joined) and has_put(seg)))
    return False


def blocked(text, depth=0):
    if depth > MAX_DEPTH:
        return True  # pathological nesting: fail safe
    text = text.replace("\\\n", "")  # the shell removes backslash-newline continuations
    clean, scripts, unquoted = strip_heredocs(text)
    clean = normalize_ansic(strip_comments(clean))
    clean, subs = extract_subs(clean)
    for body in scripts:
        if blocked(body, depth + 1):
            return True
    for body in unquoted:
        subs.extend(extract_subs(body)[1])
    for sub in subs:
        if blocked(sub, depth + 1):
            return True
    for line in clean.split("\n"):
        if not line.strip():
            continue
        try:
            lex = shlex.shlex(line, posix=True, punctuation_chars=True)
            lex.whitespace_split = True
            tokens = list(lex)
        except ValueError:
            if REST.search(line) or GQL.search(line) or GH_FALLBACK.search(line):
                return True
            continue
        for seg in segments(tokens):
            if seg_blocked(seg, depth):
                return True
    return False


def main():
    cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    print("deny" if blocked(cmd) else "allow")


if __name__ == "__main__":
    main()
