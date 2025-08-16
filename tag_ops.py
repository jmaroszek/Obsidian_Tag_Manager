from __future__ import annotations

from typing import Tuple

from ruamel.yaml.comments import CommentedMap, CommentedSeq


def _ensure_list(value):
    if value is None:
        return CommentedSeq()
    if isinstance(value, CommentedSeq):
        return value
    # scalars -> list
    seq = CommentedSeq()
    if isinstance(value, (list, tuple, set)):
        for v in value:
            seq.append(v)
    else:
        seq.append(value)
    return seq


def normalize_tags(meta: CommentedMap) -> bool:
    """
    Ensure 'tags' is a CommentedSeq of bare strings (no leading '#'),
    deduplicated in original order. Return True if anything changed.
    """
    changed = False
    if "tags" in meta:
        original = meta["tags"]
        seq = _ensure_list(original)

        cleaned = []
        seen = set()
        for t in list(seq):
            if t is None:
                continue
            s = str(t)
            if s.startswith("#"):
                s = s[1:]
            if s not in seen:
                cleaned.append(s)
                seen.add(s)

        # Detect changes: scalar->list, content change, or length change
        if not isinstance(original, CommentedSeq):
            changed = True
        else:
            if len(original) != len(cleaned) or any(
                str(a) != b for a, b in zip(original, cleaned)
            ):
                changed = True

        meta["tags"] = CommentedSeq(cleaned)
    return changed


def normalize_aliases(meta: CommentedMap):
    if "aliases" in meta:
        meta["aliases"] = _ensure_list(meta["aliases"])


def sort_everything(meta: CommentedMap, order: str):
    """If order == 'alpha':
        - sort the 'tags' and 'aliases' lists
        - sort the top-level keys alphabetically
    Otherwise, preserve order.
    """
    if order == "alpha":
        # sort lists
        for key in ("tags", "aliases"):
            if key in meta and isinstance(meta[key], (list, CommentedSeq)):
                # Compare case-insensitively but keep stable lowercase-first
                lst = list(meta[key])
                lst = sorted(lst, key=lambda x: str(x).lower())
                meta[key] = CommentedSeq(lst)

        # sort mapping keys
        keys = sorted(list(meta.keys()), key=lambda x: str(x).lower())
        if list(meta.keys()) != keys:
            new_map = CommentedMap()
            for k in keys:
                new_map[k] = meta[k]
            # Copy comments if any: ruamel comments are attached to keys; this simplistic
            # approach may drop complex comment positions.
            meta.clear()
            meta.update(new_map)


def add_tag(meta: CommentedMap, tag: str, order: str) -> Tuple[CommentedMap, bool]:
    normalize_aliases(meta)
    norm_changed = normalize_tags(meta)

    if "tags" not in meta:
        meta["tags"] = CommentedSeq()
        norm_changed = True  # we created the key

    tag = tag.lstrip("#")
    tags = meta["tags"]

    added = False
    if not any(str(t) == tag for t in tags):
        tags.append(tag)
        added = True

    sort_everything(meta, order)
    changed = norm_changed or added
    return meta, changed


def remove_tag(
    meta: CommentedMap, tag: str, order: str
) -> Tuple[CommentedMap, bool, bool]:
    """Remove tag from meta['tags'] if present.
    Returns (meta, changed, frontmatter_empty_after).
    """
    normalize_aliases(meta)
    normalize_tags(meta)

    changed = False
    tag = tag.lstrip("#")

    if "tags" in meta:
        seq = [t for t in meta["tags"] if str(t) != tag]
        if len(seq) != len(meta["tags"]):
            changed = True
        if seq:
            meta["tags"] = CommentedSeq(seq)
        else:
            # remove 'tags' key entirely
            del meta["tags"]

    sort_everything(meta, order)
    # Determine if FM is empty
    empty = len(meta.keys()) == 0
    return meta, changed, empty
