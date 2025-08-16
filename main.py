from __future__ import annotations

import argparse
import difflib
from dataclasses import dataclass
from typing import Optional

from config import Settings, settings
from fm_yaml import build_file_text, load_frontmatter, split_frontmatter
from fs import iter_markdown_files, read_text, write_text
from tag_ops import add_tag, remove_tag


@dataclass
class Options:
    path: str
    tag: str
    mode: str  # 'add' or 'remove'
    recursive: bool
    dry_run: bool
    backup: bool
    order: str  # 'preserve' or 'alpha'
    include_glob: str
    backup_dir: str


def from_settings(cfg: Settings) -> Options:
    return Options(
        path=cfg.path,
        tag=cfg.tag,
        mode=cfg.mode,
        recursive=cfg.recursive,
        dry_run=cfg.dry_run,
        backup=cfg.backup,
        order=cfg.order,
        include_glob=cfg.include_glob,
        backup_dir=cfg.backup_dir,
    )


def process_file_text(text: str, tag: str, mode: str, order: str) -> str:
    yaml_text, body, nl = split_frontmatter(text)
    meta = load_frontmatter(yaml_text)

    if mode == "add":
        meta, changed = add_tag(meta, tag, order)
        if not changed and yaml_text is not None:
            # No change in tags and FM existed -> return original
            return text
        # If FM didn't exist, we still add it
        new_text = build_file_text(meta, body, nl)
        return new_text

    elif mode == "remove":
        meta, changed, fm_empty = remove_tag(meta, tag, order)
        if not changed:
            return text

        if fm_empty:
            # Remove entire frontmatter block
            # Ensure body has no leading blank line accidentally left
            body_only = body.lstrip("\r\n")
            return body_only
        else:
            new_text = build_file_text(meta, body, nl)
            return new_text
    else:
        raise ValueError("mode must be 'add' or 'remove'")


# main.py (inside process_path)
def process_path(opts: Options) -> int:
    total = 0
    changed = 0
    backups_made = False

    for path in iter_markdown_files(opts.path, opts.recursive, opts.include_glob):
        total += 1
        original = read_text(path)
        updated = process_file_text(original, opts.tag, opts.mode, opts.order)

        if updated != original:
            changed += 1
            if opts.dry_run:
                print(f"[DRY-RUN] Would modify: {path}")
                diff = difflib.unified_diff(
                    original.splitlines(True),
                    updated.splitlines(True),
                    fromfile=path + " (old)",
                    tofile=path + " (new)",
                )
                print("".join(diff))
            else:
                backup_path = write_text(
                    path,
                    updated,
                    backup=opts.backup,
                    vault_root=opts.path,
                    backup_root=opts.backup_dir,
                )
                print(f"Modified: {path}")
                if backup_path:
                    backups_made = True

    print(
        f"Processed {total} file(s). {'Changed ' + str(changed) if changed else 'No changes.'}"
    )
    if backups_made and opts.backup:
        print(f"Backups saved under: {opts.backup_dir}")
    return changed


def parse_bool(s: Optional[str]) -> Optional[bool]:
    if s is None:
        return None
    return s.lower() in ("1", "true", "t", "yes", "y")


def main():
    parser = argparse.ArgumentParser(description="Obsidian Tag Manager")
    parser.add_argument("--path")
    parser.add_argument("--tag")
    parser.add_argument("--mode", choices=["add", "remove"])
    parser.add_argument("--recursive", choices=["true", "false"])
    parser.add_argument("--dry-run", dest="dry_run", choices=["true", "false"])
    parser.add_argument("--backup", choices=["true", "false"])
    parser.add_argument("--order", choices=["preserve", "alpha"])
    parser.add_argument("--include-glob")
    args = parser.parse_args()

    cfg = settings

    # CLI overrides
    if args.path is not None:
        cfg.path = args.path
    if args.tag is not None:
        cfg.tag = args.tag
    if args.mode is not None:
        cfg.mode = args.mode
    if args.recursive is not None:
        cfg.recursive = args.recursive == "true"
    if args.dry_run is not None:
        cfg.dry_run = args.dry_run == "true"
    if args.backup is not None:
        cfg.backup = args.backup == "true"
    if args.order is not None:
        cfg.order = args.order
    if args.include_glob is not None:
        cfg.include_glob = args.include_glob

    opts = from_settings(cfg)
    process_path(opts)


if __name__ == "__main__":
    main()
