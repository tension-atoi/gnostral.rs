# Runtime benchmark protocol

The next cross-engine protocol should measure more than token throughput.

Required dimensions:
- cold process start;
- model load to readiness;
- warm request latency;
- TTFT and TPOT;
- prefill/decode throughput;
- process RSS;
- model VRAM after load;
- peak VRAM;
- reclaim after stop;
- context growth;
- KV-cache residency/compression;
- C1/C4/C8 concurrency;
- preemption behavior;
- two-model residency;
- unload/reload;
- crash/restart;
- desktop pressure and driver health.

Guardrails:
- record baseline graphical VRAM;
- reject NVIDIA Xid/MMU faults as success;
- distinguish sampled nvidia-smi telemetry from allocator traces;
- keep cold, warm-host-cache, and warm-VRAM-cache states separate;
- never compare different quantizations/topologies as if they were identical.

## Desktop profiles

Cross-engine qualification uses two distinct lanes.

CONTROL keeps the live graphical session but rejects opportunistic GPU compute
clients. It is the primary comparison lane.

DESKTOP-PRESSURE intentionally retains ordinary workstation GPU clients and
records their exact identities plus ambient VRAM before each run. Results in
this lane are robustness evidence and are never substituted for CONTROL.

A pressure-lane result must retain the ambient VRAM envelope alongside the
runtime result.
