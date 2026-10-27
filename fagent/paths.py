"""Canonical declared-scope locking; this is not an operating-system sandbox."""
from pathlib import Path

from .protocol import require, strings

PROTECTED = {".git", ".agents", ".codex", ".fagent"}


def canonical(root, relative):
    require(isinstance(relative, str) and bool(relative), "Invalid relative path")
    require(relative == relative.strip() and
            not any(char in relative for char in '\\:*?[]{}<>|"') and
            not any(ord(char) < 32 for char in relative) and
            not relative.startswith("/") and
            all(part and part not in (".", "..") for part in relative.rstrip("/").split("/")),
            "Scope must be project-relative using forward slashes")
    require(relative.split("/")[0].casefold() not in PROTECTED, "Protected runtime/metadata path")
    resolved = (Path(root) / relative).resolve()
    require(resolved.is_relative_to(Path(root).resolve()), "Scope escapes the target project")
    parts = resolved.relative_to(Path(root).resolve()).parts
    require(not parts or parts[0].casefold() not in PROTECTED, "Resolved scope targets protected metadata")
    return resolved.as_posix().casefold().rstrip("/")


def overlap(left, right):
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def scope_keys(root, paths):
    return [canonical(root, path) for path in paths]


def changed_files(root, declared, reported):
    strings(reported, "changed_files")
    keys = scope_keys(root, declared)
    for path in reported:
        require(not path.endswith("/") and not (Path(root) / path).is_dir(),
                "changed_files must report files, not directories")
        actual = canonical(root, path)
        allowed = any(actual == key or (scope.endswith("/") and actual.startswith(key + "/"))
                      for scope, key in zip(declared, keys))
        require(allowed, f"Reported change outside declared scope: {path}")


def conflicting(left, right):
    return any(overlap(a, b) for a in left for b in right)
