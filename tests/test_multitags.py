# tests/test_multi_tags.py
from main import Options, process_file_text, process_path


def test_add_multiple_tags_into_empty(tmp_path):
    p = tmp_path / "m.md"
    p.write_text("BODY\n", encoding="utf-8")
    opts = Options(
        path=str(tmp_path),
        tag="legacy",  # unused because tags is provided
        tags=["a", "b", "c"],
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
    assert "tags:\n  - a\n  - b\n  - c\n" in out


def test_remove_multiple_tags_and_delete_frontmatter_when_empty(tmp_path):
    p = tmp_path / "n.md"
    p.write_text(
        """---
tags:
  - a
  - b
---
BODY
""",
        encoding="utf-8",
    )
    opts = Options(
        path=str(tmp_path),
        tag="legacy",
        tags=["a", "b"],
        mode="remove",
        recursive=True,
        dry_run=False,
        backup=False,
        order="preserve",
        include_glob="*.md",
        backup_dir=str(tmp_path / "Backups"),
    )
    process_path(opts)
    out = p.read_text(encoding="utf-8")
    assert not out.startswith("---")  # FM removed entirely
    assert out.strip() == "BODY"


def test_process_file_text_accepts_list_or_str():
    original = "BODY\n"
    # list
    out = process_file_text(original, ["x", "y"], "add", "preserve")
    assert "tags:\n  - x\n  - y\n" in out
    # single str still works
    out2 = process_file_text(original, "z", "add", "preserve")
    assert "tags:\n  - z\n" in out2
