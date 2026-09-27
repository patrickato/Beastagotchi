from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def json_safe(value: Any) -> Any:
    """Recursively convert proof/manifest data to plain JSON-compatible values.

    Renderers are allowed to use rich immutable semantic objects such as
    ``Reading`` internally. Proof artifacts should preserve that information
    without forcing the runtime model to become dict-only just for json.dumps.
    """

    if is_dataclass(value) and not isinstance(value, type):
        return json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    # Proof tooling should remain robust to future lightweight semantic wrappers
    # while making an unsupported value obvious in the manifest rather than
    # crashing the entire render job.
    return str(value)
