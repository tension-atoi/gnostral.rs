# Gnostral Q-010/Q-011 — Public research handoff

Status: **local experimental evidence, not product release or upstream superiority**.
Scope: NVIDIA RTX 3070 8 GiB, Qwen3-30B-A3B Q2_K, CUDA, three paired runs per condition. The research evidence is local and host-specific. This publication supplies selected hashes, code patches, and bounded observations; it does not claim complete external reproducibility.

## Q-010: borrowed CPU expert weights
- Original Strata decoder median (six-check task): 9.51 tok/s.
- Candidate Q2_K/Q3_K copy-free projection median: 20.18 tok/s (2.12x).
- Medians of total-card GPU peaks: 2344 vs 2351 MiB; engine process-tree RSS: 22094 vs 22172 MiB.
- All six matched response pairs were byte-identical, within each paired repetition.
- An **initial candidate run failed** the 128 MiB post-reclaim ambient GPU gate (+196 MiB). A separate fresh repeated session, with unchanged thresholds, passed. Both receipts are retained.
- The unsafe typed borrowed view is not exhaustively audited. These gains do not establish superior performance relative to llama.cpp's CPU-MoE options.

## Q-011: load-time GPU-adaptive mapping
- Three control launches: 22, 21, 21 GPU layers from a 48-layer Qwen3 MoE model.
- Three launches with a separate 2048 MiB CUDA reservation: 13, 12, 13 GPU layers; remaining layers on CPU.
- Median checklist decode: 20.88 tok/s control; 20.15 tok/s under synthetic GPU memory reservation.
- The pressure program reserved GPU bytes but **did not execute sustained competing GPU compute**.
- The CUDA backend's placement changed only **at model load**, not while inference was running. PagedAttention was disabled with mixed CPU/GPU placement.
- Eight negative/unit tests for the read-only post-run placement verifier passed. 37 source artifacts were rehashed by an independent checker.

## Disclosure and limitations
- Rates are workload- and hardware-specific, three launches per condition, not confidence-bounded population estimates.
- Whole-GPU memory measurements include the desktop; RSS includes resident file-backed and potentially shared pages; PSS was not measured.
- Some text generated in Q-011 differed among fresh launches. Structural completeness is not a general semantic correctness metric.
- Path-specific Python harnesses preserve the original host geometry for traceability and are not portable reproductions without adaptation.
- The model GGUF, release binaries, full raw logs, local tokens and private system configuration are **not included** in this publication.
- This public report does not authorize daemon deployment, modeld changes, authentication, privileged GPU control, multi-model scheduling, public APIs or docs-platform authority.

## Source pointers
- patches/strata-residency/*-q010-cpu-expert-borrowed.patch: incremental code changes.
- evidence/runs/q010-hotpath-ssd-ab-audit-20261010.json: paired run audit and resource measurements.
- evidence/runs/q010-hotpath-first-failed-ab-20261010.json: original failed gate.
- evidence/runs/q011-rtx3070-placement-observation-20261010.json: typed placement receipts.
- harness/placement/: read-only collector, tests and known offline-session prerequisites.

No release tag or production qualification is asserted.
