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
  {
    echo "export VIRTUAL_ENV=\"$VENV\""
    echo "export PATH=\"$VENV/bin:\$PATH\""
    # The import root is the repo root (there is no conftest.py).
    echo "export PYTHONPATH=\"$CLAUDE_PROJECT_DIR\""
  } >> "$CLAUDE_ENV_FILE"
fi
