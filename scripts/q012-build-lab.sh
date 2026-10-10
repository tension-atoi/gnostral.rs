#!/usr/bin/env bash
# Q-012: the MoE residency Cargo feature is mandatory; never silently omit it.
set -euo pipefail
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
vendored="$repo/vendor/mistralrs-strata"
runner="${GNU6_LAB_RUN:-$HOME/.local/bin/gnu6-lab-run}"
if [[ ! -f "$vendored/Cargo.toml" ||
      ! -f "$repo/crates/gnostral-expert-residency/Cargo.toml" ]]; then
  echo "Q012_BUILD_REFUSED: vendored runtime / lab-owned residency crate absent" >&2
  exit 72
fi
args=(cargo build --locked --offline --release -p mistralrs-cli
      --features cuda,mistralrs-core/gnostral-expert-residency -j 4)
if [[ "${1:-}" == "--dry-run" ]]; then
  printf 'Q012_FEATURE_RECIPE: '; printf '%q ' "${args[@]}"; printf '\n'
  printf 'CARGO_TARGET_DIR=%s\nMISTRALRS_LAB_FAST_CUDA_BUILD=1\n' "$repo/../target"
  exit 0
fi
if (( $# )); then echo "Q012_BUILD_REFUSED: unknown argument(s)" >&2; exit 64; fi
command -v "$runner" >/dev/null || { echo "Q012_BUILD_REFUSED: safe launcher missing" >&2; exit 72; }
cd -- "$vendored"
export CARGO_TARGET_DIR="$repo/../target"
export MISTRALRS_LAB_FAST_CUDA_BUILD=1
exec "$runner" --exclusive -- "${args[@]}"
