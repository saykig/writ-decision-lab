# Certificate transport/revalidation adapter — build report

## Verdict

**TRANSFER QUALIFIED FOR THE BOUNDED IDENTITY-SKELETON PROFILE.**

The Bellman PR #6 capability can be represented as a small language-neutral Decision Lab contract
without weakening its subject, policy, source-certificate, correspondence, or receiver distinctions.
The resulting adapter gives a producer/checker pair suitable for a later Writ integration test.

This is not a claim that Bellman is finished or that every PR #6 theorem has been transferred.
Only the anchored transport/revalidation route is implemented here.

## Why this build was earned

Writ PR #47 established durable revision/replay infrastructure: old checked results remain historical,
changed evidence/model assumptions can make uses stale, and successor calculations can coexist with
prior results. The missing mathematical operation was not another shared-analysis fixture; it was a
way to construct and independently warrant a successor sequential guarantee after a declared model
or policy revision.

Bellman's hardened certificate-transport construction supplies that operation.

## Implementation

Added `writ_decision_lab.transport` as an isolated standard-library package. Existing Build 1 and
Build 2 code paths are unchanged.

The adapter has deliberately separate modules:

- `model.py` — exact subject/policy/certificate/request/evidence decoding and identities;
- `producer.py` — Bellman correction recurrence;
- `checker.py` — ordinary source/target certificate checks plus anchored-envelope receiver;
- `cli.py` / `__main__.py` — creation-only file interface.

The checker never imports `producer.py`.

## Decisive checks

The focused suite covers:

- Bellman's comparator-change counterexample: candidate `a` is unchanged while the optimum moves;
  transport repairs the lower root from `1` to `0` and certifies regret upper `1`;
- unchanged subject/policy returns zero corrections and the original tables exactly;
- the PR5 two-step policy change returns target upper `7/8`, optimum lower `1/4`, and regret upper
  `5/8`;
- a target-valid certificate with false correction/provenance evidence keeps its ordinary target
  warrant and bounds while the stronger transport warrant is rejected;
- tampered request identities are rejected for transport without erasing an independently valid
  target certificate;
- an invalid source certificate supplies no transport warrant;
- action-menu or loss-unit changes are unsupported rather than silently mapped;
- subject names and explicit premise labels may change while the exact structural contract remains;
- certificate/proof values may exceed the 256-bit model-coefficient cap, preserving Bellman's derived-value boundary;
- model coefficients above that 256-bit profile still fail closed;
- noncanonical JSON bytes are rejected;
- the receiver still checks with the producer disabled;
- the CLI is deterministic and refuses output overwrite.

## Executed verification

Environment: CPython 3.13.5, standard library only.

```text
PYTHONPATH=src python -m unittest discover -s tests -v
14 passed, 0 failed

PYTHONPATH=src python -O -m unittest discover -s tests -v
14 passed, 0 failed

PYTHONPATH=src python -m compileall -q src tests
passed
```

Normal and optimized modes produced the same asserted mathematical observations.

## Simpler-workflow comparison

Bellman's own frozen Python reference remains the simpler research workflow and mathematical source.
This Decision Lab adapter is justified only where a caller needs:

- a versioned language-neutral JSON boundary;
- canonical exact byte identities;
- explicit source/target/request binding;
- creation-only producer/checker CLI behavior;
- a receiver path that can be called independently of the producer;
- a stable handoff surface for Writ.

For one-off mathematics, Bellman's reference remains simpler and should be preferred.

## What this does not earn

- no general sequential planning engine;
- no structural mapper between different trees or information structures;
- no certificate accumulation or policy-selection semantics;
- no continuation/conditional query interface;
- no statistical coverage or empirical model checking;
- no authenticated review or authority to act;
- no Writ integration in this PR;
- no claim of formal verification or all-input correctness.

## Next gate

After human review/merge of this Decision Lab adapter, Writ should pin the exact adapter commit and
exercise one complete revision story:

1. preserve a checked old sequential certificate;
2. declare a target model or policy revision;
3. mark the old use stale without rewriting its historical validity;
4. call the pinned transport producer;
5. independently check the transported target certificate;
6. preserve old and successor guarantees together;
7. hand the record to a fresh recipient that performs checker-only replay.

That Writ integration should reuse PR #47's existing revision/applicability machinery rather than
invent another parallel lifecycle.
