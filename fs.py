from __future__ import annotations

import fnmatch
import os
from typing import Iterable


def iter_markdown_files(path: str, recursive: bool, include_glob: str) -> Iterable[str]:
    if not recursive:
        for name in os.listdir(path):
            p = os.path.join(path, name)
            if os.path.isfile(p) and fnmatch.fnmatch(name, include_glob):
                yield p
        return

    for dirpath, dirnames, filenames in os.walk(path):
        for name in filenames:
            if fnmatch.fnmatch(name, include_glob):
                yield os.path.join(dirpath, name)


def read_text(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    # Try to preserve encoding; assume utf-8 with fallback
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def write_text(
    path: str,
    text: str,
    backup: bool,
    *,
    vault_root: str | None = None,
    backup_root: str | None = None,
):
    """
    Write file and, if backup=True, save a single centralized backup alongside
    the 'backup_root' folder, mirroring the relative path from 'vault_root'.
    Returns the backup path if created, else None.
    """
    backup_path = None

    if backup and os.path.exists(path) and vault_root and backup_root:
        # Compute path inside backup_root mirroring relative path from vault_root
        rel_path = os.path.relpath(path, start=vault_root)
        backup_path = os.path.join(backup_root, rel_path) + ".bak"

        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        with open(path, "rb") as f:
            original = f.read()
        with open(backup_path, "wb") as f:
            f.write(original)

    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))

    return backup_path
