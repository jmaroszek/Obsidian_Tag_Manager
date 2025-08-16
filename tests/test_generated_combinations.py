import itertools
import pytest
from fm_yaml import split_frontmatter, load_frontmatter, build_file_text
from tag_ops import add_tag

# Generate combinations of starting states for: frontmatter present?, aliases present?, tags present?, properties present?
# For add-mode, we assert all existing items are unchanged except tags gains 'newtag' appropriately.

def make_yaml(has_aliases, has_tags, has_props):
    parts = []
    if has_aliases:
        parts.append("aliases:\n  - alias_a\n  - alias_b\n")
    if has_tags:
        parts.append("tags:\n  - old\n")
    if has_props:
        parts.append("prop1: 1\nprop2: two\n")
    return "".join(parts)

@pytest.mark.parametrize("has_aliases,has_tags,has_props", list(itertools.product([False, True],[False, True],[False, True])))
def test_add_preserves_everything_else(has_aliases, has_tags, has_props):
    body = "B\n"
    if has_aliases or has_tags or has_props:
        text = "---\n" + make_yaml(has_aliases, has_tags, has_props) + "---\n" + body
    else:
        text = body

    yml, body_out, nl = split_frontmatter(text)
    meta = load_frontmatter(yml)
    meta, changed = add_tag(meta, "newtag", "preserve")
    out = build_file_text(meta, body_out, nl)

    assert out.endswith(body)
    # aliases preserved if they existed
    if has_aliases:
        assert "aliases:" in out and "alias_a" in out and "alias_b" in out
    # properties preserved if existed
    if has_props:
        assert "prop1:" in out and "prop2:" in out
    # tags now contain 'newtag'
    assert "tags:" in out and "newtag" in out
    if has_tags:
        assert "old" in out
