import os
import sys
from types import SimpleNamespace

import pytest

# Ensure project root is importable in all environments
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture
def sample_bodies():
    return {
        "simple": "This is a body.\n\n#not-a-frontmatter-tag\n",
        "empty": "",
        "with_inline": "Intro text.\n\n#inlineTag and more text.\n",
    }


@pytest.fixture
def make_tmp_md(tmp_path):
    def _make(content: str, name="note.md"):
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p

    return _make


@pytest.fixture
def options(tmp_path):
    # defaults used by integration tests; can override per-test
    return SimpleNamespace(
        path=str(tmp_path),
        tag="newtag",
        mode="add",
        recursive=True,
        dry_run=False,
        backup=False,
        order="preserve",
        include_glob="*.md",
    )
