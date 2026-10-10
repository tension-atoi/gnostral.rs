# Q-013 — EVIDENCE-BOUND-ADMISSION

State: **Q013-A CLOSED — CONTRACT_ONLY / Q013-B FIXTURE PASS / Q013-C REAL-DENSE-PILOT PASS / Q013-D MULTI-ENGINE INTEGRATION PENDING**

Q013-B fixture-scope results: [Q-013B-ISOLATED-FIXTURE](Q-013B-ISOLATED-FIXTURE.md). The subsequent bounded [Q013-C real-dense pilot](Q-013C-REAL-DENSE-PILOT.md) qualifies one actual local CUDA server but does not promote generalized model execution authority.

## Question

Given the three Q-012 sequential functional proofs on the same SHA-pinned
Rust/CUDA executable, what is the smallest safe way to *plan* a capability
selection and represent model lifecycle without extending execution authority
or claiming that a real multi-model supervisor already exists?

Q-013 inherits [EngineProvider v0](../contracts/ENGINE_PROVIDER_V0.md)
and the [Q-008 promotion decision](Q-008-MODELD-PROMOTION-GATE.md).

## Q013-A — implemented / qualified (offline)

1. Pin the exact published Q-012 receipt SHA-256, engine binary SHA-256 and
   per-model weight SHA-256; allow only three operation-specific probes:
   `DenseSentinel`, `EmbeddingTriple1024`, `MoeExpertSentence`.
2. Preserve the distinction between `DeclaredCapability`, published
   `QualifiedCapability` and current runtime truth. No fallback to a
   friendly model name, advertised feature, partial hash or another model.
3. Reject unknown/bad evidence, wrong model/binary, duplicate receipts,
   unqualified profile, extra operation and persistent-serving intent.
4. Return only a `ProbePlan`, for which `execution_authorized() == false`.
   There is no spawning, network, token generation, tool permission or
   capability/grant issuance in this increment.
5. Use the Q-007 lifecycle state machine. Semantic readiness needs a
   matching engine/model/handle receipt plus a separately provided witness;
   unload acknowledgment and host-observed GPU reclaim are distinct gates.
   These typed envelopes model verification; *their constructors do not
   authenticate an external witness or trust its claimed verifier identity*.
6. Keep historical GPU card peaks as observations only, **never** treat
   them as per-process VRAM budgets or fresh available-headroom claims.

## Test/evidence gates

- `cargo test --offline --locked --manifest-path harness/engine-provider-contract/Cargo.toml`:
  seven existing EngineProvider tests plus nine Q-013 tests.
- `python3 -m unittest discover -s harness/experiments -p 'test_q013*.py' -v`:
  six tests with the **actual** public Q-012 receipt and synthetic negative tampering.
- `python3 harness/experiments/q013_evidence_replay.py --output evidence/runs/gnostral-q013-exact-probe-plans-20261010.json`:
  creates immutable, sanitized, probe-only plans. Refuses overwrites.
- No inference workload, CUDA build, GPU allocation or new system service
  is required by Q013-A. Run local tests under `gnu6-lab-run` when available.

## Q013-B to Q013-D — original forward gates, updated October 10

These checks were drafted **before** the bounded Q013-B disposable process and Q013-C real-dense pilot. Q013-B has since passed its CPU fixture scope; Q013-C passed one narrow real engine cycle. The following items remain unmet wherever they imply an authenticated listener, independently established witness trust, generic adapter, or multi-engine authority:

- A concrete adapter must verify the independent semantic predicate against
  a real output and cryptographically bind output digest/receipt to the
  exact engine and artifact identity, not just accept strings/booleans.
- A **fresh** host-sourced memory/VRAM/headroom/driver-health preflight
  must be taken at use time, with a clear expiry and refusal on UNKNOWN.
- A cgroup-protected launcher must be assessed with failure/timeout/cancel
  and reclaim after an *actual* transient subprocess; `gnu6-lab-run`
  alone does not limit NVIDIA VRAM or prevent unrelated workloads.
- Cross-engine generality, concurrency, persistent serving, multi-model
  residency, hot-swap, scheduling and production routing remain **unproven**.
- Only after those gates may the team discuss a narrow, operational adapter.
  Q-008 forbids moving KV, expert/layer placement or kernel authority above
  the inference engine.

## Evidence

- Q-012: `evidence/runs/gnostral-q012-native-three-families-20261010.json`
- Q013-A: `evidence/runs/gnostral-q013-exact-probe-plans-20261010.json`
- Pure model: `harness/engine-provider-contract/src/q013.rs`
- Replayer: `harness/experiments/q013_evidence_replay.py`

**Promotion verdict:** `CONTRACT_ONLY_PASS`. No runtime readiness or
execution authority is promoted by this quest increment.
