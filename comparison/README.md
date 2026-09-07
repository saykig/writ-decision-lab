# Equal-information simpler-workflow comparison

`baseline.py` is a competent ordinary exact-arithmetic script. It receives the same complete
model/query bytes as the candidate, preserves labels, binds raw bytes with SHA-256, freshly
recalculates the whole answer before consumption, and refuses unsupported semantics. It does not
import the candidate package.

`run_sequence.py` applies the packet's same eight changes and failure attempts to both workflows.
It records correctness, refusal status, downstream-use failures, maintained source size, explicit
preparation/repair notes, and measured machine duration. The comparison is same-author,
implementer-run, unblinded, and too small for a productivity or timing claim. Human effort was not
measured and is not estimated.
