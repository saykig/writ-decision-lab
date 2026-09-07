# Build 2 fixtures

These fixtures use the additive `finite-linear-uncertainty.v1` profile. Build 1's
`finite-one-observation.v1` fixtures are not changed.

- A is Bellman's inconsistent binary triangle.
- B supplies consistent `P(X,Y)` and `P(Y,Z)`. The checked witness is a joint
  extension. Bellman's conditional-independence construction is one compatible
  extension, not an inferred fact about the family or reality.
- C is an identified scalar; D has two certified endpoint models.
- E starts from Bellman's exactly derived posterior family. From prior
  `p in [1/4,2/5]` and likelihoods `P(e|1)=4/5`, `P(e|0)=1/5`, monotonicity of
  `4p/(1+3p)` gives the exact supplied posterior family `[4/7,8/11]`. The
  implementation checks its probability range and its zero-one-loss decision
  separately. It does not claim to have checked the upstream likelihood model.
- F changes only the loss query; the old checked result remains valid for its old
  bytes and is stale for the new bytes.
- G labels the exact fiber and its larger sound outer enclosure separately. Outer
  variation is not projected onto the exact family.
- H exercises controlled missing-certificate and impossible-conditioning paths.

The conditional operation is deliberately deferred in Build 2. E therefore uses
the exact posterior family supplied after Bellman's positive-mass derivation; it is
not an implementation of the linear-fractional transform.
