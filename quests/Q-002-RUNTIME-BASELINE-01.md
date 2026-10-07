# Q-002 — RUNTIME-BASELINE-01

State: PROPOSED

Freeze a complete mistral.rs + Bonsai lifecycle and concurrency baseline before adding more runtime complexity.

Required evidence: cold start, load-to-ready, warm request, TTFT/TPOT, C1/C4/C8, VRAM/RSS, context growth, reclaim, restart, and failure behavior under a live desktop.

Exit gate: one machine-readable qualification packet with a frozen protocol and explicit non-claims.
