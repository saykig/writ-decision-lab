# Certificate transport/revalidation adapter — specification

## Purpose

This adapter transfers one hardened Bellman capability into the Writ Decision Lab test bench: construct and independently check a new sequential decision certificate after an explicitly supplied model or policy change.

It implements only the identity-skeleton transport route. It does not implement continuation conditioning, uniform-comparison bounds, persistent model families, certificate accumulation, family-aware replanning, statistical learning, or Writ applicability/review semantics.

## Mathematical authority

Pinned Bellman integration point:

`aae1b56276b231d16748473f4a54dd4a9ea514cf`

Authoritative mathematical record:

`foundations/BELLMAN_CERTIFICATE_TRANSPORT_AND_REVALIDATION.md`

SHA-256 recorded by Bellman's frozen execution evidence:

`c6d9db76f62783918bbd64b9141095ca0de02f4c2d266db18f42f45e4d8e6253`

Reference source identities:

- `verification/certificate_transport/transport.py` — `a2d04eb8aedaa1d455128abc6ed6ab106c81a82b38d6fb1e9d7752be83f4ee60`
- `verification/sequential_certificates/reference.py` — `99d0f1a3a32334cce826a7a582502122bc25e195f7024ed40f0c45753cbde1df`

The Bellman theorem and its premises remain upstream authority. This repository defines an engineering contract and checker; it does not restate or strengthen the theorem.

## Contract

`certificate-transport-request.v1` binds one exact source subject, complete source policy, checked source lower/upper certificate, exact target subject, complete target policy, complete ordered identity correspondence, and guarantee `expected-additive-total-cost-regret`.

Source and target must preserve the same finite observable-history semantics, expected-additive-total-cost criterion, horizon, loss unit, ordered histories, decision/terminal structure, action labels/menus, outcome labels/menus including zero-probability outcomes, and STOP/continuation structure. Exact rational costs, terminal costs, transition probabilities, subject names, and explicit premise labels may change.

`certificate-transport-evidence.v1` contains exact request/component SHA-256 identities, a target certificate, and nonnegative correction tables `alpha` and `beta`.

The checker does not import the producer. It independently validates the source certificate, evidence/request bindings, ordinary target certificate, exact `L'=L-alpha` and `U'=U+beta` relation, and Bellman's anchored extremal envelope equations at every node.

A target certificate may be mathematically valid but fail the stronger anchored-transport warrant. The check report preserves that distinction explicitly: `target_certificate_status` can remain `checked` while `transport_status` is `rejected`, and the target-certificate bounds remain visible. Overall `status=checked` is reserved for the stronger anchored-transport warrant.

`certificate-transport-check.v1` returns overall `checked`, `rejected`, or `checker_error` together with the two component statuses. A checked transport result is conditional on the exact supplied subjects, policies, source certificate, correspondence, criterion, and bytes. It is not empirical validation, source acceptance, human review, formal proof, or authority to act.

## Bounded profile

- at most 1 MiB per request/evidence object;
- JSON depth at most 64;
- horizon at most 4;
- nodes at most 64;
- actions per node at most 4;
- outcomes per action at most 4;
- model coefficient numerator/denominator bit length at most 256; certificate and correction proof values are exact and have no separate bit cap beyond the object byte limit.

## CLI

```bash
export PYTHONPATH=src
python -m writ_decision_lab.transport solve --request examples/transport/comparator-change-request.json --output /tmp/transport-evidence.json
python -m writ_decision_lab.transport check --request examples/transport/comparator-change-request.json --evidence /tmp/transport-evidence.json --output /tmp/transport-check.json
```

Outputs are creation-only.
