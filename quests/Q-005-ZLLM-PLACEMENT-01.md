# Q-005 — ZLLM-PLACEMENT-01

State: CLOSED — BLOCKED_MODEL_INVENTORY

## Question

Does zLLM's CUDA runtime make safe and reproducible placement decisions when
physical VRAM availability changes on the reference RTX 3070?

The primary mechanism under test is zLLM's Qwen3.6/3.8 CPU+CUDA hybrid
layering. The CUDA client intentionally leaves `cuda_gpu_layers=None`, so the
runtime derives the split from available VRAM.

## Pinned upstream

- repository: `https://github.com/zllm-lab/zllm`
- revision: `9a9d1ef0b55b09e1c41589ff83c407d3549f2b67`
- release at pin: `0.8.11`
- license: Apache-2.0

The pin is an intake identity, not a moving-latest claim.

## Rails

### CUDA_INTAKE

Local Gemma4 E4B Q4_K_M is used only to answer:

- does the pinned CUDA client build on this host;
- can a supported local CUDA model reach semantic-ready;
- are reclaim and driver health bounded?

Passing this rail does **not** prove automatic CPU+CUDA placement.

### AUTO_PLACEMENT

Only a Qwen3.6/3.8 artifact compatible with the pinned runtime may qualify this
rail.

Required comparison:

1. CONTROL desktop profile;
2. DESKTOP-PRESSURE profile with a measured higher ambient VRAM floor.

The same model artifact and binary must be used in both lanes.
## Required observations

For each AUTO_PLACEMENT lane:

- exact binary/model identities;
- ambient physical VRAM before process start;
- selected CPU/CUDA layer split;
- load-to-ready or terminal load failure;
- semantic-ready result;
- process RSS and peak physical VRAM;
- request latency / bounded throughput;
- reclaim to ambient;
- Xid/MMU-fault window.

## Causal gate

Q-005 can claim adaptive placement only if a change in measured ambient VRAM
causes a reproducible change in selected placement while preserving semantic
correctness.

A single successful auto-fit at one VRAM level is insufficient.

## Guardrails

- no source patch before the pinned upstream build/runtime result is recorded;
- no model is silently substituted for the placement rail;
- Gemma4 success cannot be promoted into a Qwen3.6/3.8 placement claim;
- vendor benchmark numbers remain VENDOR_CLAIM;
- any Xid/MMU fault fails the lane;
- throughput is secondary to placement correctness and reclaim.

## Exit states

- `QUALIFIED`: adaptive placement is causally reproduced.
- `NOT_QUALIFIED`: a supported artifact runs but adaptation is not proven.
- `BLOCKED_MODEL_INVENTORY`: CUDA intake is viable but no compatible local
  placement artifact is available.
- `RUNTIME_BLOCKED`: the pinned CUDA path cannot reach semantic readiness.

## Post-closure review — 2026-10-09

**Disposition: CLOSED / BLOCKED_MODEL_INVENTORY.** Strata expert cache admission, WakeKV KV demotion and zLLM layer-level adaptive CPU/CUDA placement are distinct interventions. Neither new lead satisfies Q-005's required same-model causal CONTROL versus DESKTOP-PRESSURE placement experiment. No Qwen3.6/3.8 artifact download or reinterpretation of Gemma4's CUDA-intake result is authorized by this review.
