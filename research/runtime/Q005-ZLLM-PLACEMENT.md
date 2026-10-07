# Q-005 — zLLM Placement

**State:** CLOSED — BLOCKED_MODEL_INVENTORY
**Date:** 2026-10-07

Q-005 asked whether zLLM's CUDA runtime changes CPU↔CUDA placement safely and
reproducibly as physical VRAM availability changes on the reference RTX 3070.

The primary mechanism is specific to Qwen3.6/3.8. The pinned Fedora CUDA
client leaves `cuda_gpu_layers=None`, delegating the split to the runtime.

## Pinned upstream

- zLLM 0.8.11
- revision `9a9d1ef0b55b09e1c41589ff83c407d3549f2b67`
- Apache-2.0

## Clean CUDA build

Unlike Q-004 xInfer, zLLM built directly against the local CUDA 13.4 toolkit.
No compatibility shim or source patch was required.

- `zllm-fedora-cuda` SHA-256:
  `942a3a8dd773dc3f77ef50f80c891c9aef5891cd9d5e930c888d04ed18b48d3e`
- `zllm-rt-cuda` SHA-256:
  `25297110daf99f71901ae4b56cb4db0799394a80f86f60354329ba59fc9d5cc8`

## CUDA_INTAKE — Gemma4 E4B

Gemma4 is not the placement model. It was used only to qualify the pinned CUDA
runtime on hardware already present in the lab.

The zero-config Fedora client loaded all 42 Gemma4 layers and reported a
4.97 GiB model footprint. Its console frontend then rejected single-request
generation for Gemma4, so that frontend was not treated as the semantic
oracle.

The official `zllm-rt-cuda` standalone HTTP surface was then configured
without source modification. The config passed zLLM's own
`--check-config` validation.

On CONTROL:

- model registration: **2231 ms**;
- semantic probe `2+3=5`: **PASS**;
- semantic request latency: **516 ms**;
- ambient total VRAM: **1229 MiB**;
- peak total VRAM: **4352 MiB**;
- RSS at model-ready: **732 MiB**;
- SIGTERM → ambient VRAM: **168 ms**;
- NVIDIA Xid/MMU fault: **none observed**.

The first standalone harness revision also exposed a useful readiness
distinction: the HTTP server returned 200 while `/v1/models` was still empty.
Q-005 therefore used **model-registered-ready**, not socket/HTTP readiness, as
its semantic gate.

## AUTO_PLACEMENT — blocked

No compatible Qwen3.6/3.8 placement artifact is currently present locally.

The pinned CUDA hybrid path accepts GPU-resident Q4_K/Q5_K/Q6_K/Q8_0/F16/BF16/F32
weights. The smaller IQ3/Q3 options are not valid substitutes for this CUDA
placement rail.

A suitable Qwen3.6 27B Q4_K_M artifact is approximately 16.8–19 GB. At intake,
the workbench had only about 36 GB free. Downloading the artifact solely to
complete this quest would consume nearly half of the remaining storage margin.

The model was therefore **not downloaded**.

## Verdict

Q-005 closes **BLOCKED_MODEL_INVENTORY**.

Qualified:
- clean Rust/CUDA build on toolkit 13.4;
- official standalone HTTP Gemma4 semantic readiness;
- bounded physical VRAM reclaim;
- no observed driver-health fault.

Not qualified:
- Qwen3.6/3.8 adaptive CPU↔CUDA placement;
- causal response to changing ambient VRAM;
- placement quality relative to another engine;
- production adoption.

zLLM remains a credible future placement challenger. Reopen this quest when a
compatible Qwen3.6/3.8 artifact is already available or the lab's storage
budget is deliberately expanded.
