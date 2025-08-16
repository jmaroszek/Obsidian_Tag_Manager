from fm_yaml import build_file_text, load_frontmatter, split_frontmatter
from tag_ops import add_tag, remove_tag


def fm(yaml_str):
    text = f"""---
{yaml_str}---
BODY
"""
    y, body, nl = split_frontmatter(text)
    meta = load_frontmatter(y)
    return meta, body, nl


def full(meta, body, nl):
    return build_file_text(meta, body, nl)


# ---------- Add cases


def test_add_to_no_frontmatter_creates_block():
    text = "Just body\n"
    meta, body, nl = split_frontmatter(text)
    meta = load_frontmatter(meta)
    meta, changed = add_tag(meta, "alpha", "preserve")
    assert changed is True
    out = full(meta, body, nl)
    assert out.startswith("---\n")
    assert "tags:\n  - alpha\n" in out


def test_add_dedup_and_strip_hash():
    meta, body, nl = fm("tags: [alpha, beta]\n")
    meta, changed = add_tag(meta, "#alpha", "preserve")
    assert changed is False
    meta, changed = add_tag(meta, "gamma", "preserve")
    assert changed is True
    out = full(meta, body, nl)
    assert "tags:" in out and "gamma" in out


def test_add_normalizes_scalar_to_list():
    meta, body, nl = fm("tags: alpha\n")
    meta, changed = add_tag(meta, "beta", "preserve")
    out = full(meta, body, nl)
    # Obsidian-like block list
    assert "tags:\n  - alpha\n  - beta\n" in out


def test_order_alpha_sorts_lists_and_keys_on_add():
    meta, body, nl = fm("aliases: [c, a]\nproperties: 1\ntags: [b, a]\n")
    meta, changed = add_tag(meta, "d", "alpha")
    out = full(meta, body, nl)
    # keys sorted
    assert out.index("aliases:") < out.index("properties:")
    assert out.index("properties:") < out.index("tags:")
    # lists sorted
    assert "aliases:\n  - a\n  - c\n" in out
    assert "tags:\n  - a\n  - b\n  - d\n" in out


# ---------- Remove cases


def test_remove_when_last_tag_deletes_key_and_frontmatter_if_empty():
    meta, body, nl = fm("tags: [alpha]\n")
    meta, changed, empty = remove_tag(meta, "alpha", "preserve")
    assert changed is True
    assert "tags" not in meta
    assert empty is True


def test_remove_when_other_keys_remain_keeps_frontmatter():
    meta, body, nl = fm("aliases: [x]\ntags: [a]\n")
    meta, changed, empty = remove_tag(meta, "a", "preserve")
    assert changed is True
    assert empty is False


def test_remove_nonexistent_tag_no_change():
    meta, body, nl = fm("tags: [a, b]\n")
    meta, changed, empty = remove_tag(meta, "zzz", "preserve")
    assert changed is False
    assert empty is False
