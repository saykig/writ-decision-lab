# Build 2 backend investigation

## Direct cloud observations

On 7 September 2026 the cloud image ran CPython 3.12.13 and contained SciPy
1.17.0. `scipy.optimize.linprog(method="highs")` returned floating primal
solutions and feasible-problem marginal fields. An intentionally infeasible
probe returned status 2 but no `certificate` field. The image had no `soplex`,
`highs`, `glpsol`, or `cbc` executable and no importable `highspy`, `pysoplex`,
`swiglpk`, `pulp`, `ortools`, or `sympy` module.

These observations are environment-specific, not claims about every available
release or installation route.

## Candidate comparison

| Candidate | Exact rational ability | Primal/dual/infeasibility evidence | Installation and packaging | License | Fitness here |
|---|---|---|---|---|---|
| SoPlex | Source-reported by its official README: rational input, exact solutions, rational LU, continued-fraction reconstruction | Not directly observed because no executable or binding was installed; a dependable Python-facing certificate path was therefore not established | Source/C++ and standalone routes are documented upstream, but not reproduced in this image | Apache-2.0 in upstream `LICENSE` | Promising future adapter; unavailable for this build's reproducible cloud execution |
| SciPy 1.17 `linprog` using bundled HiGHS | Floating candidate search, not exact rational solving | Directly observed primal vectors and feasible dual marginals; no direct infeasibility certificate field in the probe | Already installed; pinned by `requirements-build2.txt`; SciPy requires Python >=3.11 in this image | BSD-style SciPy distribution; bundled HiGHS upstream is MIT | Selected only as an untrusted candidate generator; exact status comes solely from the independent rational checker |
| Standalone HiGHS / `highspy` | Floating solver; no exact-rational claim used | Not directly observed; `highspy` and executable absent | Upstream documents CMake, binaries, and PyPI, but none was installed here | MIT upstream | No advantage over the bundled candidate search for this bounded run |

Official upstream records inspected:

- SoPlex README and license at `scipopt/soplex`;
- HiGHS README and license at `ERGO-Code/HiGHS`;
- local SciPy package metadata and live `linprog` result keys.

## Decision

**Engineering judgment, high confidence for this bounded build:** use the already
installed SciPy/HiGHS path for candidate search and accept a conclusion only
after exact rational witness/certificate verification. This is reproducible with
the pinned Python dependency and avoids pretending that floating solver status
is a proof.

The judgment would change if a packaged SoPlex (or another exact backend)
provided a stable, reproducible interface for primal optima, dual bounds, and
infeasibility certificates in this environment. Such a backend could replace
candidate search without changing the checker contract.

