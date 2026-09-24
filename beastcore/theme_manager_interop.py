from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any


_VERSION_RE = re.compile(r'__version__\\s*=\\s*["\\']([^"\\']+)["\\']')
_MAX_SOURCE_BYTES = 1_500_000


class ThemeManagerProbe:
    """Read-only capability probe for Korrie71 Theme Manager.

    The probe never imports or executes the plugin. It inspects the installed
    source file, caches by mtime/size, and reports only interoperability
    capabilities Beast can use to choose an adapter strategy.

    Capability detection is intentionally conservative. In particular, managed
    presentation handoff is only reported when an explicit release/acquire API
    is present; a clean on_unload path is useful compatibility evidence but is
    not equivalent to a supported managed-mode contract.
    """

    def __init__(self, *, max_bytes: int = _MAX_SOURCE_BYTES) -> None:
        self.max_bytes = max(64 * 1024, int(max_bytes))
        self._cache: dict[str, tuple[tuple[int, int], dict[str, Any]]] = {}

    @staticmethod
    def _empty(path: str | None = None) -> dict[str, Any]:
        return {
            "inspectable": False,
            "path": str(path or ""),
            "version": None,
            "capabilities": [],
            "managed_handoff_supported": False,
            "compatibility_handoff_evidence": False,
            "reason": "theme_manager source is not available for inspection",
        }

    @staticmethod
    def _method_names(tree: ast.AST) -> set[str]:
        for node in getattr(tree, "body", []):
            if isinstance(node, ast.ClassDef) and node.name == "ThemeManager":
                return {
                    child.name
                    for child in node.body
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
        return set()

    @staticmethod
    def _top_level_names(tree: ast.AST) -> set[str]:
        names: set[str] = set()
        for node in getattr(tree, "body", []):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
        return names

    @staticmethod
    def _managed_contract(source: str, methods: set[str]) -> bool:
        # Prefer an explicit future API over guessing from private internals.
        method_contracts = (
            {"prepare_release", "release_presentation", "acquire_presentation"},
            {"presentation_prepare_release", "presentation_release", "presentation_acquire"},
        )
        if any(contract <= methods for contract in method_contracts):
            return True
        endpoint_markers = (
            "api/presentation/prepare_release",
            "api/presentation/release",
            "api/presentation/acquire",
        )
        return all(marker in source for marker in endpoint_markers)

    def probe(self, path: str | Path | None) -> dict[str, Any]:
        if not path:
            return self._empty()
        fp = Path(path)
        try:
            st = fp.stat()
            sig = (int(st.st_mtime_ns), int(st.st_size))
        except OSError:
            return self._empty(str(fp))

        key = str(fp)
        cached = self._cache.get(key)
        if cached and cached[0] == sig:
            return dict(cached[1])

        if st.st_size > self.max_bytes:
            row = self._empty(key)
            row["reason"] = f"theme_manager source exceeds bounded probe size ({st.st_size} bytes)"
            self._cache[key] = (sig, row)
            return dict(row)

        try:
            source = fp.read_text(errors="replace")
            tree = ast.parse(source, filename=key)
        except (OSError, SyntaxError, ValueError) as exc:
            row = self._empty(key)
            row["reason"] = f"theme_manager source could not be inspected: {type(exc).__name__}"
            self._cache[key] = (sig, row)
            return dict(row)

        methods = self._method_names(tree)
        names = self._top_level_names(tree)
        caps: list[str] = []

        def cap(name: str, condition: bool) -> None:
            if condition:
                caps.append(name)

        cap("stat_source", "STAT_SOURCE" in names and "STAT_SOURCE(key)" in source)
        cap("clean_unload", "on_unload" in methods and "self._orig_render" in source)
        cap("live_install", "_install_live" in methods)
        cap("timed_try", "try_theme" in methods and "_end_try" in methods)
        cap("structural_themes", "render_structure" in methods and all(x in source for x in ('"layout"', '"sizes"', '"hide"', '"panels"')))
        cap("doctor", "doctor" in methods and "def diagnose(" in source)
        cap("gallery", "library_rows" in methods and 'path == "api/library"' in source)
        cap("changed_row_writer", "_present" in methods and "np.flatnonzero" in source and ".mm.write(" in source)
        cap("raw_touch", "_touch_loop" in methods and "find_touch_device" in source)
        cap("pwa", '"manifest.json"' in source and '"sw.js"' in source)
        cap("nodes", "node_rows" in methods and "_mesh_peers" in source)
        cap("wardrive", "wardrive_status" in methods and "start_wardrive" in methods)

        match = _VERSION_RE.search(source)
        managed = self._managed_contract(source, methods)
        compatibility = "clean_unload" in caps and "live_install" in caps

        row = {
            "inspectable": True,
            "path": key,
            "version": match.group(1) if match else None,
            "capabilities": sorted(caps),
            "managed_handoff_supported": managed,
            "compatibility_handoff_evidence": compatibility,
            "reason": (
                "explicit managed presentation contract detected"
                if managed
                else "no explicit managed presentation release/acquire contract detected"
            ),
        }
        self._cache[key] = (sig, row)
        return dict(row)
