# Research method

## Freeze identity

Before a decisive experiment, record engine repository and revision, model artifact identity and checksum, hardware and driver/toolkit versions, relevant build flags, runtime configuration, and desktop/VRAM baseline when GPU pressure matters.

## Separate correctness from performance

A path is not benchmarkable until it is known to execute the intended model semantics. Unsupported engines are reported as unsupported at the observed boundary, not as 0 tok/s.

## Use causal A/B tests

Prefer one changed mechanism at a time. Preserve the pre-change executable or revision when a matched comparison matters.

## Retain negative results

OOMs, driver faults, crashes, semantic mismatches, unsupported formats, and failed builds are evidence. They are not rewritten into success narratives.

## Protect the desktop

Local inference research shares a GPU with a live graphical session. VRAM pressure, process reclaim, driver faults, and desktop responsiveness are part of the protocol.

## Bound generality

One successful model family does not prove cross-family support. One GPU does not establish architecture-wide performance.

## Execution authority

GitHub is not an experimental compute environment for gnostral.rs.

Authoritative qualification runs, benchmarks, CUDA validation, residency
measurements, multimodal probes, and failure characterization run on declared
local hardware before publication.

GitHub Actions may perform only lightweight repository hygiene on pull requests
or manual invocation. A green GitHub workflow is never evidence that an
inference/runtime claim is proven.
