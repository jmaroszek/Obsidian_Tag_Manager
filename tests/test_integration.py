import os

from main import Options, process_file_text, process_path


def test_add_creates_frontmatter_when_absent(sample_bodies):
    original = sample_bodies["simple"]
    updated = process_file_text(original, "newtag", "add", "preserve")
    assert updated.startswith("---\n")
    assert "tags:\n  - newtag\n" in updated


def test_add_preserves_body_and_ignores_inline_tags(sample_bodies):
    original = sample_bodies["with_inline"]
    updated = process_file_text(original, "x", "add", "preserve")
    # unchanged body tail
    assert updated.endswith(sample_bodies["with_inline"])


def test_remove_whole_frontmatter_when_empty_after_removal():
    text = """---
tags:
  - solo
---
body
"""
    updated = process_file_text(text, "solo", "remove", "preserve")
    assert not updated.startswith("---")
    assert updated.strip() == "body"


def test_recursive_flag_controls_depth(tmp_path):
    # Layout:
    # tmp/a.md (processed)
    # tmp/dir/b.md (processed only if recursive=True)
    top = tmp_path
    (top / "a.md").write_text("Body A\n", encoding="utf-8")
    os.makedirs(top / "dir", exist_ok=True)
    (top / "dir" / "b.md").write_text("Body B\n", encoding="utf-8")

    opts = Options(
        path=str(top),
        tag="t",
        mode="add",
        recursive=False,
        dry_run=False,
        backup=False,
        order="preserve",
        include_glob="*.md",
        backup_dir=str(top / "Backups"),
    )
    process_path(opts)
    a = (top / "a.md").read_text(encoding="utf-8")
    b = (top / "dir" / "b.md").read_text(encoding="utf-8")
    assert a.startswith("---\n")
    assert not b.startswith("---\n")

    # Now recursive
    opts.recursive = True
    process_path(opts)
    b2 = (top / "dir" / "b.md").read_text(encoding="utf-8")
    assert b2.startswith("---\n")


def test_order_alpha_sorts_keys_and_lists_on_write(tmp_path):
    p = tmp_path / "k.md"
    p.write_text(
        """---
zzz: 1
tags: [b, a]
aliases: [z, a]
---
body
""",
        encoding="utf-8",
    )
    opts = Options(
        path=str(tmp_path),
        tag="m",
        mode="add",
        recursive=True,
        dry_run=False,
        backup=False,
        order="alpha",
        include_glob="*.md",
        backup_dir=str(tmp_path / "Backups"),
    )
    process_path(opts)
    out = p.read_text(encoding="utf-8")
    # keys alphabetical: aliases, tags, zzz
    assert out.index("aliases:") < out.index("tags:")
    assert out.index("tags:") < out.index("zzz:")
    # lists sorted
    assert "aliases:\n  - a\n  - z\n" in out
    assert "tags:\n  - a\n  - b\n  - m\n" in out


def test_backup_and_dry_run_behaviors(tmp_path, capsys):
    p = tmp_path / "x.md"
    p.write_text("BODY\n", encoding="utf-8")
    backup_root = tmp_path / "Backups"

    # Dry run: no file change, no backup anywhere
    opts = Options(
        path=str(tmp_path),
        tag="t",
        mode="add",
        recursive=True,
        dry_run=True,
        backup=True,
        order="preserve",
        include_glob="*.md",
        backup_dir=str(backup_root),
    )
    process_path(opts)
    assert not any(backup_root.rglob("*.bak"))
    assert not p.read_text(encoding="utf-8").startswith("---")

    # Actual write with backup to centralized folder
    opts.dry_run = False
    process_path(opts)
    # backup should exist under backup_root with same relative path
    expected_backup = backup_root / "x.md.bak"
    assert expected_backup.exists()
    # no adjacent .bak next to the note
    assert not (tmp_path / "x.md.bak").exists()
    assert p.read_text(encoding="utf-8").startswith("---")

    # Also confirm the summary line is printed
    captured = capsys.readouterr().out
    assert f"Backups saved under: {str(backup_root)}" in captured


def test_normalizes_scalar_tags_and_dedup(tmp_path):
    p = tmp_path / "y.md"
    p.write_text(
        """---
tags: alpha
---
body
""",
        encoding="utf-8",
    )
    opts = Options(
        path=str(tmp_path),
        tag="alpha",
        mode="add",
        recursive=True,
        dry_run=False,
        backup=False,
        order="preserve",
        include_glob="*.md",
        backup_dir=str(tmp_path / "Backups"),
    )
    process_path(opts)
    out = p.read_text(encoding="utf-8")
    # ensures list representation
    assert "tags:\n  - alpha\n" in out

    # now add beta
    opts.tag = "beta"
    process_path(opts)
    out2 = p.read_text(encoding="utf-8")
    assert "tags:\n  - alpha\n  - beta\n" in out2
