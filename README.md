# Obsidian Tag Manager

A small utility to add or remove a tag across Markdown files in an Obsidian vault (or any folder), without disturbing existing frontmatter structure. It:
- Always uses the `tags` key (never `tag` or a custom property).
- Writes tags as block lists:

  ```yaml
  tags:
    - my_tag
    - another_tag
  ```

- Ignores inline `#tags` in the Markdown body.
- Can operate recursively or just on the specified folder.
- Provides `dry-run` and backup options.
- Can preserve key/list order or sort alphabetically.

## Install & Run

1. Ensure Python (Anaconda recommended) with `ruamel.yaml` available.
2. Edit `config.py` to set your path, tag, mode, and options.
3. Run:

   ```bash
   python main.py
   ```

   Or override via CLI:

   ```bash
   python main.py \
     --path "/path/to/notes" \
     --tag "my_tag" \
     --mode add \
     --recursive true \
     --dry-run true \
     --backup true \
     --order preserve
   ```

## Options

- **path**: Folder with `.md` files.
- **tag**: Tag to add/remove (no leading `#`).
- **mode**: `add` or `remove`.
- **recursive**: Recurse into subfolders.
- **dry-run**: Show diffs only; do not write files.
- **backup**: Create a `.bak` before writing.
- **order**:
  - `preserve`: Keep existing key order and list order (`tags`, `aliases`).
  - `alpha`: Sort top-level keys alphabetically and sort the `tags`/`aliases` lists.

## Tests

Uses `pytest`. From project root:

```bash
pytest -q
```

The test suite:
- Covers parsing/round-trip behavior for frontmatter.
- Verifies add/remove semantics (including deleting entire frontmatter when empty).
- Checks recursive vs non-recursive behavior.
- Generates a grid of initial states to ensure only the `tags` key changes on add.

## Notes

- We rely on `ruamel.yaml` for round-trip YAML editing to preserve formatting and comments as much as possible.
- If you remove the last remaining tag and no other keys exist in frontmatter, we remove the entire frontmatter block.
