# Placement evidence (offline / read-only)

Converts an existing qualified RTX3070 coexistence experiment into an inspectable typed JSON placement receipt. This is not an admission controller, GPU policy engine or live instrumentation.

Usage from repository root:

    python3 harness/placement/evidence.py --session /mnt/hdd/lab/sessions/gnostral-rtx3070-vram-coexist-20261010 --output /tmp/gnostral-placement-new.json
    python3 -m unittest discover -s harness/placement -p test_*.py -v

Optional --model and --binary validate current exact SHA256 again; no output is overwritten.
Log segment topology, native residency counters, release receipts, CUDA reservation witnesses, reply hashes and performance metrics are verified.
Any unexpected discrepancy refuses to emit a PASS receipt. No process is started or controlled.
