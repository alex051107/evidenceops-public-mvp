"""Portable path labels for reports that may be committed publicly."""

from __future__ import annotations

from pathlib import Path


def portable_report_path(path: Path, repository_root: Path) -> str:
    resolved = path.resolve()
    root = repository_root.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        return f"<external-path>/{path.name}"
    if relative == Path("."):
        return "<repo-root>"
    return f"<repo-root>/{relative.as_posix()}"
