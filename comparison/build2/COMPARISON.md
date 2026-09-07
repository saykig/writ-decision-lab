# Build 2 comparative judgment

## Judgment

The competent simpler workflow is clearer and answer-equivalent for the tested
scope. This is an engineering judgment, not a scalar score and not a finding
that the structured implementation is mathematically stronger.

| Dimension | Structured Build 2 engine | Equal-assurance direct baseline |
|---|---|---|
| Correctness on A–H | Same checked conclusions | Same checked conclusions |
| Exact checking | Independent `checker.check`; no backend call | Same independent checker |
| Stale refusal | Fresh intended-byte check in separate consumer | Same fresh intended-byte check |
| Failure distinctions | Compatible, incompatible, identified, partially identified, four decision outcomes, unresolved | Identical statuses and reasons |
| Backend use | One adapter entry per operation; finite batch inside | Identical adapter contract |
| Preparation | Reusable engine facade and checked-result boundary | One direct 29-line orchestration module |
| Duplicated safeguards | Decoder, checker, and consumer are reusable modules | Intentionally calls the same safeguards; it does not reimplement or omit them |
| Reuse earned | Backend can be replaced without changing exact checker or consumer; immutable checked artifacts can be retained under old bytes | Adequate for a direct local workflow, but less explicit as a component boundary |

The structured boundary earns only the protection demonstrated here: candidate
search cannot directly authorize display, and checked artifacts remain bound to
original model/query bytes across revision. The baseline reproduces those
protections with less orchestration, so structure is not evidence of better
answers or productivity.

