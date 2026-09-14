# Published current-snapshot review evidence

The current user authorized publication of the already reviewed commit
`36b9bbf7dc3f92a647d9e6a341aa7334e0610cbd` to PR #1, followed by a separate commit
containing the review and relevant durable evidence. That reviewed commit was pushed unchanged
first. This publication adds documentation and evidence; it does not modify runtime code, tests,
fixtures, original reports, or historical outputs.

[The review report](../../docs/reviews/pr1/current-snapshot-review.md) is a byte-for-byte copy of the completed
local assessment, including its archival limitation and account of the earlier local-only review.
Its statements that nothing was pushed and that the report was outside the checkout describe that
review session, before this separately authorized publication. Its verified subject remains the
commit above, not the later evidence publication commit. The latter's complete tree necessarily
includes additional files, while every previously reviewed tracked file remains unchanged.

The original `PR1_REPAIR_PARTIAL_OR_BLOCKED` disposition and unresolved historical installation
authorization discrepancy remain unchanged. This publication does not establish missing reviewer
replay or unseen-directive completeness, or authorize merging PR #1.

## Artifact paths and integrity

`publication-manifest.json` maps original review paths to repository paths and records SHA-256 for
every copied file. The report's `evidence/...` references map to this directory. Historical absolute
local paths in logs, commands and scripts remain evidence of the actual run, not directions to create
new local directories. All copied bytes are preserved. Scripts are newly authored current-review
probes, not the missing original reviewer scripts.

Included: normal/optimized plain and audited suite logs, child command records, independent probe
scripts and observations, diagnostic precedence/status checks, all 16 original/current fixture
results and compatibility checks, source/input/output hashes, Git identity and preservation checks,
and one representative result/check/consumer set per mode. The command/observation records retain
both relocation checks; duplicated source trees are omitted.

`TRACKED_SOURCE_SHA256SUMS` covers the 112 files in the reviewed commit. The original/current Git
commits provide the actual tracked source. Large or redundant local artifacts are intentionally not
published: tar archives, extracted original/current snapshots, copied relocation source trees,
synthetic per-case input directories, and Git diffs reproducible from the recorded commits. Archive
hashes and final validation metadata remain historical evidence; their presence does not imply that
the archives are committed here. The earlier local archives were not deleted or rewritten.

For fresh execution, use Codex Cloud with the pinned reviewed source and new temporary output paths.
`run_suites.py`, `current_probes.py` and `precedence_and_reports.py` accept explicit source/output
arguments. `validate_export.py` retains the original hard-coded local paths as an executed historical
script; adapt paths in a new cloud review script rather than overwriting the archived evidence.

Future work follows the repository's [cloud-first workflow](../../AGENTS.md).
