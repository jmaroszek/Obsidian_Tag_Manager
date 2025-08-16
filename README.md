# Obsidian Tag Manager
A small utility to add or remove a tag across Markdown files in an Obsidian vault without disturbing existing frontmatter structure. It:

- Ignores inline `#tags` in the Markdown body.
- Can operate recursively or just on the specified folder.
- Provides `dry-run` and backup options.
- Can preserve key/list order or sort alphabetically.

## Install & Run

2. Edit `config.py` to set your path, tag, mode, and options.
3. Run:

   ```bash
   python main.py
   ```

   Or via CLI:

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

