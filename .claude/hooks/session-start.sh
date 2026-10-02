#!/bin/bash
# Claude Code on the web: when a session starts, build an isolated Python environment with the
# test and render dependencies, so pytest, compileall and the render tools work immediately
# (see AGENTS.md §12). The venv keeps the container's Debian packages out of the way; their
# `cryptography` build breaks `import pypdf` under the image's own python3.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
VENV="$CLAUDE_PROJECT_DIR/.venv"
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --quiet --disable-pip-version-check --root-user-action=ignore -r requirements-dev.txt

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  # Shell-escape the literal paths with %q so a clone path containing spaces or shell
  # metacharacters ($HOME, $(...), backticks) is preserved verbatim when the file is sourced,
  # while $PATH and $PYTHONPATH are still expanded at that time on purpose.
  {
    printf 'export VIRTUAL_ENV=%q\n' "$VENV"
    printf 'export PATH=%q:"$PATH"\n' "$VENV/bin"
    # The import root is the repo root (there is no conftest.py); keep any existing entries.
    printf 'export PYTHONPATH=%q${PYTHONPATH:+:"$PYTHONPATH"}\n' "$CLAUDE_PROJECT_DIR"
  } >> "$CLAUDE_ENV_FILE"
fi
