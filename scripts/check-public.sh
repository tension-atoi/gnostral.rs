#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

fail=0

if git grep -nE '(gho_|ghp_|github_pat_|AKIA[0-9A-Z]{16})' -- ':!scripts/check-public.sh'; then
  echo "ERROR: possible secret-like token found" >&2
  fail=1
fi

# Inspect the Git index, not local untracked vendored dependencies or model fixtures.
# CI checks exactly the files being published; a forced git add is still detected.
indexed_files="$(git ls-files --cached)" || { echo "ERROR: cannot inspect Git index" >&2; exit 1; }
if grep -E '\.(gguf|safetensors|nsys-rep|pid)$' <<<"$indexed_files"; then
  echo "ERROR: forbidden public artifact type staged or tracked" >&2
  fail=1
fi

if ! grep -q '35.2 tok/s' README.md; then
  echo "ERROR: qualified public baseline missing" >&2
  fail=1
fi

exit "$fail"
