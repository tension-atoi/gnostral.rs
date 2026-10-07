# Q-004 — xInfer Spike

**State:** CLOSED — NOT_QUALIFIED / RUNTIME_BLOCKED
**Date:** 2026-10-07

Q-004 asked whether xInfer adds a measurable runtime capability on the
reference RTX 3070 that the existing control arm does not already qualify.

The intended primary experiment was same-model baseline KV versus turbo4 KV,
with semantic readiness required before any memory or context comparison.

## Build result

Pinned xInfer revision:

`b88c15334fb607ff52cdc3fd875c3da796dcc020`

A clean CUDA 13.4 build failed before xInfer compilation because the pinned
cudarc revision explicitly rejects toolkit 13.4.

A separate **COMPAT_SHIM** diagnostic lane changed only the text returned by
`nvcc --version` from 13.4 to 13.3 while delegating all real compilation to
`/opt/cuda/bin/nvcc` 13.4.

That lane compiled xInfer 0.14.5 successfully and generated real `sm_86`
kernels. This does **not** convert the clean-build result into PASS.

## Runtime result

Three local GGUF intake attempts failed before a usable KV-cache experiment:

1. **Qwen3.5-9B Q4_K_M** — CUDA OOM during model loading before readiness.
2. **Qwen3-8B Q4_K_M** — CUDA OOM during model loading before readiness.
3. **Phi-4-mini Q4_K_M** — loader stopped with:
   `Merged quantized weight is not supported for GGUF varbuilder at the moment!`

The Phi-4 failure was identical for `auto` and `turbo4`; KV dtype therefore
never became the causal variable.

## Decision

Q-004 closes **NOT_QUALIFIED / RUNTIME_BLOCKED**.

No source patch was made to xInfer. No model was downloaded solely to rescue
the benchmark. No result is presented as evidence for or against TurboQuant
itself because semantic readiness was never reached on a suitable A/B model.

xInfer remains a watched upstream rather than a donor or product candidate.
