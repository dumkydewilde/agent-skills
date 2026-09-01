#!/usr/bin/env bash
set -euo pipefail

# The Codex/ChatGPT plugin importer ignores symlinks immediately under skills/.
# The Claude plugin symlinks to the canonical source; the Codex plugin needs a
# real copy. Keep that generated copy byte-for-byte aligned with the canonical
# skills while excluding local interpreter artefacts.
#
# Add a plugin by adding its name here. The canonical source is
# skills/<name>/ and the release copy is plugins/codex/<name>/skills/.

PLUGINS=(tools dstack)

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for plugin in "${PLUGINS[@]}"; do
  source_dir="$repo_root/skills/$plugin"
  target_dir="$repo_root/plugins/codex/$plugin/skills"

  if [[ ! -d "$source_dir" ]]; then
    echo "no canonical skills for '$plugin' at $source_dir" >&2
    exit 1
  fi

  if [[ -L "$target_dir" ]]; then
    unlink "$target_dir"
  fi

  mkdir -p "$target_dir"
  rsync -a --delete \
    --exclude '__pycache__/' \
    --exclude '.DS_Store' \
    "$source_dir/" "$target_dir/"

  echo "synced $plugin: $(find "$target_dir" -type f | wc -l | tr -d ' ') files"
done
