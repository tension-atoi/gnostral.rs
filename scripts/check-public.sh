#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

fail=0

if git grep -nE '(gho_|ghp_|github_pat_|AKIA[0-9A-Z]{16})' -- ':!scripts/check-public.sh'; then
  echo "ERROR: possible secret-like token found" >&2
  fail=1
fi

if find . -type f \( -name '*.gguf' -o -name '*.safetensors' -o -name '*.nsys-rep' -o -name '*.pid' \) -print -quit | grep -q .; then
  echo "ERROR: forbidden public artifact type found" >&2
  fail=1
fi

if ! grep -q '35.2 tok/s' README.md; then
  echo "ERROR: qualified public baseline missing" >&2
  fail=1
fi

exit "$fail"
