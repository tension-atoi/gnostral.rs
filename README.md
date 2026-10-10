# gnostral.rs

Rust-first local inference research lab.

gnostral.rs is a public, reproducible research repository for local AI inference and serving on constrained hardware. It studies Rust-native and Rust-first runtimes, quantization, multimodal workloads, memory residency, KV-cache behavior, concurrency, model lifecycle, and engine-neutral orchestration.

This repository does not claim to own, replace, or author the upstream inference engines studied here. Upstream projects retain their own copyright, licenses, names, and provenance.

## Reference host

The initial public research baseline comes from an NVIDIA RTX 3070 with 8 GiB VRAM and 32 GiB system RAM. Results are evidence for that bounded environment unless a report explicitly establishes broader generality.

## Research principles

- Real artifacts before synthetic claims.
- Negative results are retained.
- Vendor claims are never silently promoted to reproduced facts.
- Engine-specific mechanisms remain engine-specific until generality is shown.
- A commit message is not evidence.
- Performance claims require a retained protocol and measurement artifact.
- Upstream support and local patched support are always distinguished.
- Tool execution authority is outside the inference engine.

See QUESTLOG.md and docs/EVIDENCE_MODEL.md.

## Initial tracks

1. Bonsai / Rust CUDA — ternary and ultra-low-bit execution on mistral.rs plus Candle-derived kernels.
2. Elastic memory — RAM↔VRAM behavior, oversubscribed models, CUDA VMM, residency, reclaim, and desktop pressure.
3. Runtime challengers — xInfer, zLLM, UniLLM, Pulsar, candle-vLLM and other credible Rust-first runtimes.
4. Engine-neutral orchestration — lifecycle and capability contracts above individual runtimes.

## Public baseline

The current qualified Bonsai product baseline is 35.2 tok/s, 28.44 ms/token, on the bounded FG-02 protocol.

A historical local commit title stated that a 40 tok/s FG-03 product gate had been achieved. The retained FG-03 evidence does not support publishing that number: the required final qualification artifact is absent and the implementation-authority document says the relevant follow-on seams had not been implemented. Public gnostral.rs therefore does not claim 40 tok/s.

See quests/Q-001-FG03-TRUTH-01.md.

## Q-012 — three native inference families (2026-10-10)

On the bounded RTX 3070 reference host, **one exact Rust/CUDA executable** passed sequential, independently started functional probes for dense text, Qwen3 embeddings and quantized MoE. The initial MoE attempt timed out because the optional `gnostral-expert-residency` Cargo feature was absent; the corrected build passed independent auditing. No claim of concurrent hosting, optimized performance or production stability is made.

- [Full French/English report](research/runtime/GNOSTRAL-Q012-NATIVE-CAPABILITIES-20261010.md)
- [Sanitized public qualification receipt](evidence/runs/gnostral-q012-native-three-families-20261010.json)
- [Fail-closed build feature gate](harness/experiments/q012_feature_gate.py) and [bounded build recipe](scripts/q012-build-lab.sh)

The MIT-licensed [lab-owned expert-residency crate](crates/gnostral-expert-residency/) is included (10 local crate tests pass). The reproduction recipe additionally requires locally prepared third-party vendored sources and a `gnu6-lab-run` systemd launch guard; it intentionally does not distribute raw model weights, private embedding vectors or upstream vendor subtrees.

## Q-013 — evidence-bound admission (contract only)

Q-013-A extends the dependency-free EngineProvider v0 reference model with **probe-only** selection and lifecycle gates tied to the exact Q-012 public receipt. It produces three informational plans; none grants execution rights, authorizes arbitrary prompts or claims fresh host memory headroom. An isolated disposable subprocess fixture is now qualified under Q-013B; real model-runtime integration and GPU reclaim qualification remain pending.

- [Q-013 quest and qualification boundaries](quests/Q-013-EVIDENCE-BOUND-ADMISSION.md)
- [Machine-readable exact probe plans](evidence/runs/gnostral-q013-exact-probe-plans-20261010.json)
- [Reference Rust contract](harness/engine-provider-contract/src/q013.rs) and [offline evidence replay](harness/experiments/q013_evidence_replay.py)

## Q-013B — isolated process fixture (bounded qualification)

A new [Rust subprocess harness](harness/q013b-local-adapter/) executes a **single SHA-pinned, CPU-only disposable test binary** after verifying the user's real systemd cgroup bounds. It enforces fixed arguments, private executable snapshots, strict output predicates, timeout/cancellation with process-group kill, and observed CPU cgroup resource return. Outside the protected lab scope, the boundary probe rejects execution with exit 73. The real inference adapter is **not** qualified.

- [Fixture qualification and remaining engine gates](quests/Q-013B-ISOLATED-FIXTURE.md)
- [Sanitized subprocess evidence](evidence/runs/gnostral-q013b-fixture-process-20261010.json)
- [Fail-closed evidence audit](harness/experiments/q013b_fixture_audit.py)

## Q-013C — real Rust/CUDA dense pilot (single server)

The first real inference adapter pilot is qualified **only** for one exact SHA-pinned Qwen2.5-Coder-1.5B server under the guarded lab scope. It verifies the local CUDA executable and model weights, performs a bounded semantic request, reaps the owned process and independently rehashes the inputs before accepting the exact GNOSTRAL output. The GPU card returned to +8 MiB of its initial ambient memory. This is **not** persistent serving, hot swap, or multi-model qualification.

- [Q-013C qualification and precise limits](quests/Q-013C-REAL-DENSE-PILOT.md)
- [Public real-dense audit receipt](evidence/runs/gnostral-q013c-real-dense-single-server-20261010.json)
- [Pinned real-model pilot](harness/experiments/q013c_real_dense.py), [independent auditor](harness/experiments/q013c_independent_audit.py), and [negative gates](harness/experiments/test_q013c_independent_audit.py)

## Upstream research intake — 2026-10-10

The [Rust Inference Watch and experiment gates](research/runtime/RUST-INFERENCE-WATCH-20261010.md) verify upstream Burn Remote v5 / Flex FP8+FP4, Ferrum opt-in SLO scheduling and CubeCL CUDA multi-GPU ordering by exact commit. They are **research candidates only**; none has been integrated or qualified locally. Proposed investigation order: Burn loopback quantized transfer → Ferrum client-side SLO measurements → CubeCL physical multi-GPU conditional gate.

## License

Original gnostral.rs material is MIT licensed. Vendored, adapted, or derived third-party material is not relicensed by this repository. Its original license and provenance must be preserved.

See THIRD_PARTY.md and docs/VENDORING_POLICY.md.

## Contributing

Reproductions, negative results, engine intakes, donor analyses, and bounded implementation experiments are welcome. Contributions require provenance and a DCO-style Signed-off-by trailer.

See CONTRIBUTING.md.
