# Evidence model

gnostral.rs uses explicit claim classes.

| Class | Meaning |
|---|---|
| PROVEN | Reproduced under a retained protocol with evidence sufficient for the stated bounded claim. |
| OBSERVED | Directly seen in a bounded run, but not necessarily reproduced or generalized. |
| SUPPORTED | Strongly supported by source inspection and/or multiple observations, without full proof. |
| INFERRED | Reasoned consequence not yet directly demonstrated. |
| VENDOR_CLAIM | Claimed by an upstream/vendor source but not reproduced by this lab. |
| UNKNOWN | Deliberately unresolved. |
| REJECTED | Tested and not retained, disproven, or failed the declared gate. |

## Evidence hierarchy

Preferred order:

1. retained machine-readable run artifact;
2. retained raw log/telemetry sufficient to reconstruct a result;
3. source-level mechanism inspection;
4. upstream official documentation;
5. upstream benchmark claim;
6. secondary commentary.

Claims must stay within the narrowest level the evidence supports.
