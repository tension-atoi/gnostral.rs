# Contributing

gnostral.rs welcomes rigorous, reproducible contributions. The repository is a research lab first; novelty without evidence is not enough.

## Contribution classes

### Engine intake
Propose a runtime, inference engine, scheduler, kernel substrate, or serving project worth evaluating.

Required: canonical repository, license, exact revision or release, the capability not already represented, and the quest it informs.

### Reproduction
Reproduce, falsify, or narrow an existing result.

Required: hardware/software manifest, exact protocol, model/artifact identity, retained result, and claim classification.

### Donor analysis
Analyze an upstream mechanism without proposing adoption. Examples include KV-cache compression, paged allocation, expert residency, continuous batching, hot load/unload, scheduler preemption, or multimodal encoder caching.

### Implementation experiment
Code changes require a predeclared gate, rollback mechanism, correctness oracle, and a statement of which upstream code is modified.

## Claim vocabulary

Use PROVEN, OBSERVED, SUPPORTED, INFERRED, VENDOR_CLAIM, UNKNOWN, REJECTED.

Do not convert VENDOR_CLAIM into PROVEN without reproduction.

## Provenance and licensing

Every vendored, copied, adapted, translated, or derived artifact must identify its source project, canonical URL, exact revision, upstream license, modification status, and applicable patches. Never remove an upstream copyright or license notice.

## DCO sign-off

All commits must include a Developer Certificate of Origin style sign-off:

    Signed-off-by: Your Name <you@example.com>

Use git commit -s. By signing off, you certify that you have the right to submit the contribution under the applicable license and that third-party material is properly identified.

## Pull requests

A research PR should answer:
1. What exact question is being tested?
2. What changed?
3. What evidence supports the result?
4. What could falsify the conclusion?
5. What remains unknown?
6. Does this alter any public claim or compatibility ledger?
