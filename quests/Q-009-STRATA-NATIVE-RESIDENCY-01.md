# Q-009 — STRATA-NATIVE-RESIDENCY-01

**Historical review dated 2026-10-09 — not the latest system qualification.**

State *as of that review*: ACTIVE_IN_ISOLATED_WORKTREE — TASKS_1_TO_3_EVIDENCED / TASK_4_WIP / INFERENCE_UNQUALIFIED

**2026-10-10 addendum:** separate Q010 and Q011 workstreams subsequently produced qualified local MoE CPU fast-path A/B and load-time placement observations; Q012 produced a 3/3 native-family functional pass. See [Q010/Q011 public handoff](../research/runtime/GNOSTRAL-Q010-Q011-PUBLIC-HANDOFF-20261010.md) and [Q012 report](../research/runtime/GNOSTRAL-Q012-NATIVE-CAPABILITIES-20261010.md). Those do **not** automatically close every original Q009 residency requirement or establish a production release.
Review date: 2026-10-09
Authorization: operator approved the native absorption design on 2026-10-08; this document does not expand that approval to any new host, daemon, persistence or control authority.

## Question

Can Strata's expert-residency mechanisms be adapted *inside* the pinned mistral.rs/Candle Rust engine, preserving exact model/routing semantics, and then qualified on the bounded RTX 3070 8 GiB / 32 GiB host?

This is not an authorization to deploy Strata as a parallel serving product or to let modeld place individual experts.

## Source and current evidence

- Donor: Niko1221/Strata at `fb58e0dbc8399662c0e47c76578c6e878b14f6cf`, MIT; notices and source provenance retained in the existing ignored local snapshot.
- Local 2026-10-08 approved design: `research/runtime/STRATA-ABSORPTION-PROPOSAL.md` (uncommitted at this review).
- Local six-task design: `docs/superpowers/plans/2026-10-08-strata-native-residency.md` (uncommitted at this review).
- The initial donor intake alone was not Strata runtime, GPU or model qualification.
- **Current execution lives in ignored isolated Git worktree** `vendor/gnostral-strata-worktree/`, branch `feat/strata-native-residency`, based on the source baseline. Do not infer project state from root `main` alone.
- Commits `e844960` (ranked admission), `101b015` (transactional leases/uploads) and `3fd1c03` (quantization preservation/CUDA 13.4) exist in that worktree. Its `research/runtime/STRATA-RESIDENCY-01.md` reports CUDA extraction parity: 5 tests passed, max absolute error 0.0002579689 and max relative error 0.00006157579.
- The worktree has **uncommitted Task 4 changes** inside paired mistral.rs/Candle sources and untracked Task 4 fixture/compile receipts (including successful fixture exits). These do not establish a complete model request, full runtime CLI A/B, or a speed gain.
- The root `main` still lacks the native crate and patches because that implementation is isolated. This is **active but not integrated into main or inference-qualified**.

## Execution sequence already described by the approved plan

1. Checked, profile-ranked admission within a global byte budget; deterministic RED→GREEN tests.
2. Transactional upload/generation tickets, leases and route partitioning with failure/rollback tests.
3. Exact quantized expert extraction; matched isolated Candle baseline/candidate source trees.
4. Opt-in native Qwen3 MoE CPU/GPU execution; numerical and routing parity before any speed claim.
5. Engine-origin residency observation and safe unload/reclaim with outstanding work.
6. Frozen A/B model/binary/prompt/quantization protocol; at least three measured repetitions per lane and explicit negative evidence.

No task is considered complete merely because an implementation checklist exists.

## Required claims and stop conditions

- Engine owns expert slots, materialization, routing and CUDA lifetime; modeld may receive qualified observations and resource-envelope intent only (Q-008).
- Publish slots only after verified transfer completion; retain active-consumer leases; failed or stale transfers never materialize a usable slot.
- Do not change expert count, top-k, route weights, quantization or activation to manufacture speed.
- No GPU inference qualification without exact available supported model, frozen hashes, semantic and numerical parity, measured memory reserves, reclaim and driver-health receipts.
- Strata's published speeds and LocalAnalysis estimates are not local results.
- Stop only the affected implementation slice if source geometry, layout, model inventory or authority contradicts the plan; preserve negative evidence.

## Outcome vocabulary

`ACTIVE_IN_ISOLATED_WORKTREE` (now, Task 4 unfinished); `CORRECTNESS_ONLY` (deterministic/extraction tests, no complete inference); `BLOCKED_INFERENCE_QUALIFICATION` (no valid model/GPU gate); `QUALIFIED_WITH_LIMITS` (measured bounded parity and A/B); `NOT_QUALIFIED` (failed semantic, numerical or physical gate).

Grouped-prefill and transfer-overlap adaptations remain **conditional follow-on work**, not automatically proven by completing admission/bookkeeping.