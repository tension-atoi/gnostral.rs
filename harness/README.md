# Harness

Cross-engine harness code will land here as quests define stable protocols.

The harness should prefer machine-readable output and never infer engine support from a process merely starting successfully.

## Q-002 helpers

`q002_openai_probe.py` performs the frozen one-token semantic probes first.
C1/C4/C8 are skipped automatically if semantic readiness fails, preventing a
fatal model-state error from being mislabeled as a concurrency result.

`q002_reclaim.py` measures SIGTERM→exit and return toward a declared ambient
total-VRAM envelope. It keeps reclaim telemetry separate from engine output.

## EngineProvider v0 reference contract

`engine-provider-contract/` is a dependency-free executable model of the
Q-007 provider boundary.

It tests that heterogeneous runtimes can be represented without promoting
engine-internal layer placement, KV paging, or token batching into supervisor
authority.

Run locally:

```bash
cd harness/engine-provider-contract
cargo test
```

GitHub Actions is not the qualification authority for this contract.
