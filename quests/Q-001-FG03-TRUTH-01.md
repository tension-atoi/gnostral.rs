# Q-001 — FG03-TRUTH-01

State: CLOSED

## Question

Does retained local evidence justify publishing the claim that FG-03 achieved the 40 tok/s product gate?

## Evidence reviewed

The local source history contains a commit titled as if the 40 tok/s product gate had been achieved.

The retained FG-03 implementation-authority document instead records:
- qualified FG-02 baseline: 35.2 tok/s / 28.44 ms/token;
- FG-03B and FG-03C as future bounded implementations;
- FG-03D as not authorized at that point;
- explicit stop language saying those changes had not been implemented.

The FG-03 contract names lab03-fg03-qualification.md as the final closure artifact. That artifact is not present in the retained local worktree reviewed for this public baseline.

## Decision

REJECTED: gnostral.rs must not claim a proven 40 tok/s FG-03 gate.

PROVEN: the bounded public baseline remains FG-02 at 35.2 tok/s until a complete retained qualification packet establishes a newer result.

## Non-claim

This does not prove no unpublished or subsequently lost run ever exceeded 40 tok/s. It proves only that retained evidence is insufficient to publish that number as qualified.

## Post-closure review — 2026-10-09

**Disposition: CLOSED / NO CHANGE TO QUALIFIED BASELINE.** The local Q-009 Strata absorption design and the WakeKV paper are not Bonsai FG-03 performance evidence. Do not reissue the rejected 40 tok/s claim or mix speed estimates from other engines/models with the qualified FG-02 result. Any new Bonsai throughput claim requires an independently frozen, retained and complete protocol.
