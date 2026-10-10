# WakeKV — reversible KV residency research lead

Date: 2026-10-09
State: PAPER_REVIEW / NOT_LOCALLY_QUALIFIED / NO QUEST OPENED

## External evidence

Source: Utkarsh Ranjan, *WakeKV: Reactive, Reversible KV Residency for Heads That Change Their Minds*, arXiv:2610.02713, submitted 2026-10-02: https://arxiv.org/abs/2610.02713

The paper reports that attention-head reading behavior can change during decode, making a classification fixed at prefill unreliable for some workloads. Its policy moves cooling heads' KV into recoverable host memory and later makes it available again, rather than destructively discarding it. The authors report comparisons with static/evicting alternatives and a FlexiCache/vLLM hardware prototype using Mistral-7B. These are authors' results, **not** RTX 3070, Bonsai or gnostral.rs reproductions.

No WakeKV code was obtained, compiled or executed during this audit. The presence, licensing and reproducibility of a public implementation remain unverified; do not translate that into a claim that code cannot exist.

## Relation to existing quests

- Q-002 supplies semantic-readiness, CONTROL/DESKTOP-PRESSURE, fixed workload, reclaim and driver-health rules.
- Q-003 proves a cross-mechanism *observation* vocabulary; it did not test per-head KV cooling, host recovery or promotion.
- Q-004's xInfer TurboQuant outcome does not qualify WakeKV; these are different engines and cache methods.
- Q-007/Q-008 keep eviction, compression and re-promotion policy inside the engine; modeld may observe physical state and request an envelope, not choose individual KV heads/blocks.
- Q-009 Strata concerns **MoE expert weights**, not KV. They compete for host RAM, VRAM budget and transfer bandwidth if eventually integrated, but no shared scheduler is ratified.

## Unopened candidate experiment

Research question: on a locally runnable, supported attention model, does *reversible* KV offload beat static classification or destructive eviction at matched physical VRAM **without violating quality or decode latency requirements**?
### Proposed measurement — not yet a frozen protocol

- Pin engine code, compatible model, tokenizer, attention/cache layout, exact weights, prompt set and model-specific correctness checks.
- Freeze comparisons before running: no-offload/reference, fixed/static policy, destructive eviction, reactive recoverable policy. Ensure matching effective memory/quality budgets.
- Record head behavior changes, required/available KV coverage, lookup granularity, CPU reservoir bytes, pinned-host footprint, GPU bytes, demotion/promotion bytes, CUDA-event completion and actual PCIe refill stalls.
- Attribute TTFT, TPOT, decode throughput, CPU/GPU contention, driver faults, context success and semantic/quality deltas; preserve every run and warm/cold condition.
- Test a wake event after GPU pressure and an interrupted or failed promotion. A recorded store event is not by itself proof the requested chunk is retrievable or safe for the consuming stream.
- Evaluate expert-weight/KV bandwidth contention with Strata **only if** each independent path becomes qualified; do not assign a combined scheduler authority from this research note.

### Related correctness risk

vLLM issue https://github.com/vllm-project/vllm/issues/59907 (opened 2026-10-04) reports cache metadata visible after same-step priority preemption before KV was computed. This is *upstream issue evidence*, not a reproduced gnostral.rs defect. A future WakeKV harness should test rollback/visibility and never equate scheduled, announced or cached with computed and retrievable.

## Decision

`WATCH / EVALUATE_FEASIBILITY`. No Q-010, implementation, new modeld authority, model download or production dependency is authorized by this note. If a compatible implementation/workload and repeatable protocol become available, propose the bounded experiment and its technical cost explicitly.