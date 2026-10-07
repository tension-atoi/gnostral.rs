# Harness

Cross-engine harness code will land here as quests define stable protocols.

The harness should prefer machine-readable output and never infer engine support from a process merely starting successfully.

## Q-002 helpers

`q002_openai_probe.py` performs the frozen one-token semantic probes first.
C1/C4/C8 are skipped automatically if semantic readiness fails, preventing a
fatal model-state error from being mislabeled as a concurrency result.

`q002_reclaim.py` measures SIGTERM→exit and return toward a declared ambient
total-VRAM envelope. It keeps reclaim telemetry separate from engine output.
