from __future__ import annotations

import re
from io import StringIO
from typing import Optional, Tuple

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

YAML_START = re.compile(r"^---\s*(?:\r?\n)", re.M)

_FM_RE = re.compile(
    r"^\ufeff?---[ \t]*\r?\n"  # opening fence, allow optional BOM and trailing spaces
    r"(.*?)"  # YAML payload (non-greedy)
    r"\r?\n---[ \t]*\r?\n",  # closing fence
    re.DOTALL,
)


def _yaml_loader() -> YAML:
    yaml = YAML(typ="rt")  # round-trip
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=2, offset=2)
    return yaml


def split_frontmatter(text: str) -> Tuple[Optional[str], str, str]:
    """
    Return (yaml_text, body, newline).
    If no frontmatter is present, yaml_text is None and body is the original text.
    newline is '\n' or '\r\n' reflecting the original style (best effort).
    """
    nl = "\r\n" if "\r\n" in text else "\n"
    m = _FM_RE.match(text)
    if not m:
        return None, text, nl
    yaml_text = m.group(1)
    body = text[m.end() :]
    return yaml_text, body, nl


def load_frontmatter(yaml_text: Optional[str]):
    yaml = _yaml_loader()
    if yaml_text is None:
        data = CommentedMap()
    else:
        data = yaml.load(yaml_text)  # may be None if empty
        if data is None:
            data = CommentedMap()
    if not isinstance(data, CommentedMap):
        # Force mapping
        m = CommentedMap()
        m.update(data)
        data = m
    return data


def dump_frontmatter(data) -> str:
    yaml = _yaml_loader()
    buf = StringIO()
    yaml.dump(data, buf)
    out = buf.getvalue()
    # ruamel may add a trailing '...\n'; remove it if present for Obsidian friendliness
    out = out.strip()
    if out.endswith("..."):
        out = out[:-3].rstrip()
    return out + "\n"


def build_file_text(meta_map, body: str, nl: str) -> str:
    yaml_str = dump_frontmatter(meta_map)
    return f"---{nl}{yaml_str}---{nl}{body}"
