# QUESTLOG

The quest log is the public execution order for gnostral.rs. A quest is not a generic TODO: it has a bounded question, evidence requirements, and a closure gate.

| ID | Quest | State | Purpose |
|---|---|---|---|
| Q-001 | FG03-TRUTH-01 | CLOSED | Reconcile the unsupported 40 tok/s claim with retained evidence. |
| Q-002 | RUNTIME-BASELINE-01 | CLOSED | Freeze a complete mistral.rs+Bonsai runtime lifecycle baseline. |
| Q-003 | ELASTIC-LEDGER-02 | CLOSED | Put mistral.rs, Pulsar and CUDA VMM under one residency protocol. |
| Q-004 | XINFER-SPIKE-01 | CLOSED | Evaluate scheduler/KV compression capabilities on RTX 3070. |
| Q-005 | ZLLM-PLACEMENT-01 | CLOSED | Evaluate automatic CPU↔CUDA placement under changing desktop pressure. |
| Q-006 | UNILLM-DONOR-01 | **ACTIVE** | Evaluate model/runtime abstractions as donor architecture. |
| Q-007 | ENGINE-PROVIDER-01 | BLOCKED | Define an engine-neutral lifecycle/capability contract after Q-002–Q-006. |
| Q-008 | MODELD-PROMOTION-GATE | BLOCKED | Decide whether any residency authority deserves production promotion. |

A quest closes only when its protocol was frozen before the decisive run, evidence is retained, negative observations remain visible, non-claims are explicit, and upstream / patched-upstream / lab-owned behavior are separated.
