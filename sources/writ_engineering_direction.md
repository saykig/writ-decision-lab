# Writ engineering direction: an exact decision-query and checking boundary

**Prepared for Sara · 6 September 2026**  
**Disposition:** Proceed with the local build specified in `RUN_THIS_NEXT_WRIT_ENGINEERING_BUILD_1.md`. The investigation is complete. A bounded computational probe was executed; the proposed production-quality first build was not. No repository writes, merges, publication, deployment, or accepted-record changes were made.

## Judgment in plain language

**Become good at handing a decision calculation to another program without losing which model and question made its answer valid.** Start with small, finite decision problems whose answers can be computed exactly and checked through a second calculation.

The first implementation should accept a complete model and an explicit question, calculate the answer, and let a separate consumer check it against the inputs it actually intended to use. Changing the losses, available actions, observation cost, or model must not silently carry an old answer forward. A zero-probability observation must not become a tie. An unchanged list of recommended actions must not be mistaken for an unchanged information value.

This is more useful than merely filing research reports: it participates in producing and testing results. It is less than a cumulative knowledge system: it does not discover prior research, prove arbitrary theorems, establish real-world assumptions, or decide which claims a community should accept.

**Recommendation: a small Python “Writ Decision Lab” alongside Writ, with a solver, a separately implemented checker, and an exercised consumer interface.** Use existing exact arithmetic rather than inventing it. Do not build a Vela-like acceptance system, a mathematical knowledge graph, or a new canonicalization protocol. Preserve the ability to adopt those systems when the actual operation requires them.

**Confidence:** High that this is technically feasible within the stated finite scope; moderate that it is the best first engineering investment; low, presently, that it will improve research productivity or produce cumulative knowledge. The build is designed to earn evidence for the latter judgment rather than assume it.

## 1. The operation worth owning

The initial users are the author of a bounded mathematical case and a later script that consumes its answer. Their concrete operation is:

> “Here are the exact model and question I intend. Check this earlier answer against them before my program uses it.”

The recurring difficulty is supported by the brief’s counterexamples, not by an observed study of researcher mistakes. They demonstrate that action summaries can be insufficient for a different query. They do **not** establish how often our workflow currently makes this error. That frequency and the cost of prevention remain empirical questions. [B1]

The three levels of the recommendation are:

| Level | Commitment | What remains additional work |
|---|---|---|
| First competence | Exact finite, one-observation decision answers and a fail-closed check-and-consume operation. | Strict decoding, whole-answer validation, mutation tests, and an actual separate consumer. |
| Foundation | A versioned boundary among model, question, computed answer, checking method, and intended use. | A second genuinely different mathematical implementation would be needed to establish generality. |
| North star | Later work could reuse checked results while retaining their assumptions and limitations. | Mathematical transport, source-to-model fidelity, review, correction propagation, retrieval, and real repeated-use evidence. None follows automatically. |

The representation deliberately retains the full labeled finite model. It makes **no compression claim**. Changing a question creates a new calculation, not a request to rescue an old summary. That makes the component compatible with the closure of the observation-compression branch: a stopped hypothesis can still supply an excellent regression case.

The inherited dispositions remain `KL5_STOP_DEGENERATE`, `KL6_STOP_THEORY_ALREADY_SETTLES`, and `KL6_STOP_STANDARD`. KL6 V2 is an analytic closure, not a completed enumeration. No KL5/KL6 continuation, grid enlargement, S04 revival, or KL7 design was undertaken. The larger source proofs were not independently audited here. [B1, §3.2]

## 2. What was investigated and what was actually tested

Repository reads resolved Writ main to `20f0473afa62ed3c6e0433a21b189d1d9d1712d6` and Vela main to `017bca6bfaa29e96d8e1b0819979c732d3320917`. The relevant contracts, selected implementations, and selected tests were read through GitHub. Public specifications were inspected for exact arithmetic, proof validation, mathematical contexts, provenance packaging, and dependency tracking. The source register below distinguishes complete files from selected sections.

A local Python 3.13.5 probe compared posterior-based computation with direct enumeration of deterministic observation policies. It checked **12 fixed engineering fixtures and 68 policies in total**, rejected nine malformed rational inputs, rejected two mismatched input bindings, and detected a tampered value even though its input bindings were correct. This was a development probe, not a held-out evaluation or a new mathematical experiment. [P1]

| Probe finding | Result | Evidence and limitation |
|---|---|---|
| Same policy, different information value | The two supplied channels produced EVSI `1/8` and `1/4`. | Recomputed from the supplied definitions; not a general compression theorem. |
| Same old summary, different revised decision | Revised risks were `(1,3/4)` and `(1,3/2)`; actions differed. | Recomputed; the historical KL4C report itself was not re-audited. |
| Impossible versus tied observations | Zero-mass branches had no posterior/action answer; possible ties retained both actions. | Observed on fixed fixtures, not all inputs. |
| Exactness matters | A pair of distinct rational risks became equal as Python floats, while the exact comparison retained the unique minimizer. | One deliberately constructed precision fixture. |
| Binding is not checking | An incorrect EVSI retained correct model/question hashes but failed recomputation. | Demonstrates the separation; the probe is not a complete hostile-input validator. |

The two algorithms share the author, parser, `Fraction`, and mathematical definitions. Calling them “independently implemented algorithms” is accurate; calling this an independent replication, formally verified implementation, or independent evaluator would not be.

**Access limits:** Container Git access failed at DNS resolution, so there was no complete local clone or repository-wide test run. Bun was unavailable. Writ’s and Vela’s tests were inspected, not executed. Lean, MMT, Storm, AiiDA, and provenance exporters were not installed or benchmarked. These limits constrain compatibility and comparative-performance claims, not the completed source-based recommendation.

## 3. Foundations: the useful boundaries, not a product catalogue

### A. Native mathematical computation and verification

**Adopt exact rational arithmetic now.** Python’s standard `fractions.Fraction` provides normalized rational arithmetic; its documentation also warns that constructing a fraction from a float preserves that float’s value, not necessarily the intended decimal. Our input contract should therefore accept canonical rational strings only. This supplies arithmetic, not domain validation, model fidelity, or answer-to-question binding. We own the finite decision semantics and the consumer checks. There is no third-party runtime package to maintain for this first slice. [F1]

**Lean/mathlib is the strongest alternative when a general theorem is the deliverable.** Lean’s validation documentation separates a valid proof from the meaning of its statement and describes axiom inspection and additional checking. Mathlib already represents rational and nonnegative rational objects. These are better foundations than a new proof language. The integration burden is formalizing our intended finite decision semantics, reviewing that formalization, and maintaining a pinned toolchain and proof dependencies. Adopt this route when repeatedly checking a theorem becomes the bottleneck; do not require it before we have a stable operation worth formalizing. No Lean proof was executed here. [F2, F3]

**Storm deserves consideration as a future computation backend, not dismissal.** Its official tutorial supports exact checking for a demonstrated PRISM example. That establishes an existing exact-computation route, not a tested translation of our models. An adapter must preserve the decision-maker’s information: exposing the hidden state to an ordinary fully observed decision process could solve the wrong problem. For this small one-observation slice, two transparent finite algorithms are a lower-burden choice than adding a modeling language, backend, and translation audit. That is an engineering judgment, not a claim Storm lacks the capability. [F4]

**MMT/OMDoc offers a serious alternative for mathematical contexts and translation.** Its module documentation describes theories, declarations, and views preserving typing judgments. This is relevant to jointly scoped assumptions and meaning-preserving reuse, not merely file metadata. GitHub’s release endpoint returned `v27.0.0`, including an `mmt.jar` asset; the setup documentation provides a Java-based installation route. Thus the evidence extends beyond a legacy homepage. However, no decision-model encoding or checking integration was demonstrated here. Building one now would make formal representation the first project, rather than dependable computation and consumption. [F5]

### B. Scientific state: what Vela owns and what it leaves native

Vela is the strongest inspected foundation for **attributed acceptance, correction, and replay of scientific state**. Its architecture separates native work from scoped verification and authorized decisions. It explicitly describes graph views as ownership separations, not a requirement for a universal graph database. Its current Cargo manifest declares version `0.977.6`, dual Apache-2.0/MIT licensing, a Rust 1.97.1 build requirement, and private implementation crates. A CLI integration is a better initial adoption route than assuming those crates are separately maintained public libraries. [V1, V3]

The inspected `verification_record.rs` is especially instructive. It binds a check to exact subject roots, names the implementation/environment, requires stated limitations, and records shared dependencies. Its outcomes are `pass`, `fail`, `error`, and `inconclusive`—not “accepted.” Its validation checks the record and its signed binding; it does not evaluate the mathematical property written in its scope field. The source tests exercise binding failures and the separation from standing. They were not run here. [V4]

**What transfers:** a check must name its precise subject and limitations; a result, a check, and acceptance are different objects; native tools should remain replaceable.

**What does not transfer by default:** Vela’s signing, repository authority, event replay, and standing are not necessary to calculate and check a finite decision answer. A decision model also needs likelihoods, losses, labels, and query semantics; a claim map alone does not supply these. Rather than reproduce Vela’s state machinery, our component can eventually produce native evidence for it.

Vela’s evidence is task-sensitive. Its internal inheritance comparison reports `73/84` correct answers for Vela, `65/84` for raw Git/source, and `58/84` for a native view, with a failed native session affecting the result. Its separate correction study reports `12/12` exact outcomes for Git/documents and the neutral wrapper, versus `11/12` for Vela, with the registered advantage gates false. These are project-reported internal findings, not independently reproduced results here. The evidence page itself identifies open external-validation gates. It also warns that penalty-adjusted statistics must not be reported as actual durations. [V2]

The lesson is not “small tools always win” or “structure compounds automatically.” It is to choose the operation whose cost structure could justify the layer, and measure that operation with equal information and preparation costs included. Episteme/Atlas was not needed to select this boundary; its exact identity remains unresolved rather than silently replaced with a similarly named project. [B1, §5]

### C. Packaging, provenance, and change

| Foundation | Primitive and actual support | What the application still owns; disposition |
|---|---|---|
| W3C PROV-DM | Entities, activities, agents, derivation, revision, and quotation. Revision is a kind of derivation, not a mathematical verdict. | Supply domain semantics and review judgments. Use these established relation meanings in a later exporter; no new generic provenance ontology. [F6] |
| RO-Crate / Process Run Crate | Package files and context; Process Run Crate describes tools and executions, including manually composed processes. Its specification does not require a complete chain of intervening actions. | Supply executable input contracts and computational correctness. Adopt an exporter when a crate-consuming workflow exists, rather than making JSON-LD a prerequisite for the solver. [F7] |
| Nanopublications | Separate assertion, assertion provenance, publication information, and the connecting head; integrity identifiers are described. | An assertion can be a hypothesis or negative result. Well-formedness is not its mathematical truth. Use for an actual publication/interchange consumer, not as the internal calculation format. [F8] |
| AiiDA | Distinguishes calculations producing data from workflows managing calls and returned data. It separates data provenance from logical workflow provenance. | Domain plugins must still supply the calculation and its scientific interpretation. Its process framework is credible when orchestration and stored execution history are the difficulty; unnecessary for this bounded pure-function path. No deployment-cost benchmark was run. [F9] |
| Snakemake | Rerun triggers can track code, inputs, parameters, modification times, and software environment. | A need to rerun is not disproof of a theorem or withdrawal of a citation. Use an existing build engine when an actual multi-step execution dependency graph warrants it. No custom scheduler now. [F10] |

A material version caution: the inspected Process Run Crate page labels itself `0.5`, while its embedded example still contains `0.4` identifiers. No conformance claim or exporter was built from that mixed example. A future exporter must pin a coherent specification and validate against it. The main RO-Crate 1.2 page pointed to 1.3; a direct 1.3 root fetch failed, while its provenance subsection was accessible. This investigation does not label 1.2 “latest.” [F7]

Licensing does not currently select between architectures. Writ’s inspected package is Apache-2.0 and private; Vela offers Apache-2.0 or MIT. Both require respecting their license terms and neither requires publishing our work. The process-profile specification declares Apache-2.0. Other deferred tools’ full dependency-license inventories were not audited; no redistributed bundle or deployment depending on them is proposed. [W3, V3, F7]

## 4. Why this direction wins provisionally

| Serious direction | First competence → foundation → later capability | Strongest case; reason not selected first |
|---|---|---|
| **Exact query/check interface — selected** | Reliable computation and consumption → versioned mathematical interface → reusable checked results. | Directly exercises the problem exposed by the counterexamples. Main risk: more structure than our actual research needs. |
| **Plain Fraction script or notebook plus Git** | Reliable local calculation → readable, versioned code → reuse through ordinary functions and tests. | The strongest simpler alternative. It may be equally safe and cheaper. The selected interface must earn retention through a real consumer, not beat a deliberately careless script. |
| **Vela plus a native calculator** | Reviewed handoff and correction → attributed scientific-state history → inheritable accepted results. | Strongest existing-system alternative for the larger destination. It still needs the native decision calculation. Select this first instead if authority/correction, rather than computational handoff, proves to be our immediate bottleneck. |
| **Lean/mathlib first** | A proved finite evaluator or reusable theorem → formal mathematical library → checked composition of results. | Strongest assurance alternative. Select when the theorem will actually be reused enough to justify statement review and proof maintenance. The current workflow need is not yet shown to require that investment. |
| **Mathematical context/atlas first** | Find and relate formal objects → MMT-style contexts and mappings → discovery and transport. | Valuable when locating and relating existing results is the observed barrier. No inspected evidence establishes that a custom atlas is needed for this initial operation. |

This is **not** a search for an unprecedented algorithm. Exact finite expected-loss minimization is ordinary mathematics and implementation. The difficult integration work is enforcing the meaning of the boundary: labels, impossible events, exact quantities, supported questions, checking scope, and the consumer’s intended inputs must agree.

There are two unresolved propositions, at different levels. First, an engineering hypothesis: explicit checked handoff will reduce repeated repair or duplicated validation enough to cover its preparation and maintenance. Second, a later research question: which weaker representations support which expanded query families or transports? The first is appropriate to evaluate here. The second remains the mathematical programme’s responsibility; Build 1 neither solves it nor authorizes a new experiment.

## 5. Relationship to Writ, component by component

Writ’s current `AGENTS.md` and product definition keep questions and human reasoning outside native records, with NIST as the active proving ground. The README explicitly says complete decision provenance does not yet exist. Those boundaries are assets: source records should not change identity whenever a downstream research question changes. [W1]

| Existing part | Decision for Build 1 | Reason |
|---|---|---|
| Institutional/legal-policy records, schemas, accepted corpora | Preserve unchanged. | No source record needs to become a decision model for this build. |
| Human review and supersession | Preserve unchanged; do not borrow acceptance labels. | A computational check cannot stand in for source review or judgment. |
| `@writ/provenance` | Retain as an existing reusable package; **no mandatory runtime dependency in the Python component**. | Its pure byte-hashing operation is suitable for future cross-language binding. Adding Node solely to hash bytes provides no demonstrated benefit here. |
| Grounding and source resolution | Possible future upstream producer, not used by the synthetic fixtures. | Turning source evidence into a prior, loss, or likelihood requires an explicit, reviewed modeling step. |
| Native DSL, API, UI, repository verifier | No changes. | No new question semantics should leak into the current source-record system. |
| New decision component | Separate local sibling directory, not a new canonical Writ family. | Keeps ownership clear while leaving future packaging, selective refactoring, or integration open. |

The provenance package’s contract was checked against its hashing implementation and selected conformance/packed-consumer tests. It already distinguishes raw bytes from canonical JSON and declared-reference checks from grounding. Its canonical JSON profile normalizes Unicode and uses JavaScript number semantics; it must not be repurposed as exact mathematical equivalence or plain RFC 8785/JCS. Its review-artifact checker checks a byte association, not whether a mathematical answer is sound. [W2, W3]

**No migration is selected.** A future move into Writ would require an explicit ADR and visible guarantee changes, not an assertion that questions had always been native objects. Conversely, keeping the first module adjacent is not a permanent separation decision.

## 6. The first build and the exact promise

The build accepts a finite prior and labeled observation channel, plus a question specifying actions, losses, loss units, and the cost of exactly one observation. It returns exact prior risks, all optimal actions, observation probabilities and conditional answers, observed risk, information value, and the choice between acting now and observing once.

A separate checker enumerates all allowed deterministic observation policies and checks every exposed answer field, using direct joint-mass identities for conditional quantities. A separate consumer supplies the intended input bytes and invokes this check before using an answer. The output is a computational result with an explicit checking scope—not a proof certificate in a formal logic and not a review decision.

The promise is conditional and narrow:

> Subject to the documented semantics and the correctness of the checker and its runtime, `checked` means every exposed answer was verified against these exact supplied model/question bytes under the supported finite one-observation profile.

The consumer must distinguish invalid input, unsupported scope, a wrong target binding, and a wrong computed answer. Historical answers can remain correct for their original inputs while being refused for new ones. Labels and complete jointly used inputs remain explicit; they are not separately reusable “premises” merely because each has a hash.

The implementation packet fixes the input shapes, equations, algorithms, module boundaries, error behavior, fixtures, independent-algorithm limits, and execution order. It does not leave the consequential architecture choices to another strategic audit.

## 7. How it earns continuation rather than permanent protection

**Behavior established now:** the local probe supports bounded arithmetic feasibility and identifies failures a hash-only wrapper cannot catch. It does not establish a finished interface.

**Foundation to establish in Build 1:** a real second program consumes checked answers through the public interface, while tampered, mismatched, and unsupported inputs fail without downstream use. Identical frozen runs are reproducible. This can be useful even when a simple script is faster.

**Later benefit hypothesized:** fewer repeated manual checks, fewer misapplied answers, easier handoff, and eventual research accumulation. Test these in a fixed eight-step sequence covering initial calculation, channel change, cost change, loss change, action removal, historical reuse, tampering, and unsupported scope. Give the simpler script the same data, mathematics, tests, and access. Include input preparation, interface maintenance, and repair—not just final query time.

| Decision | Predefined condition |
|---|---|
| Continue as a foundation | All correctness/binding gates pass and the separate consumer actually uses the interface. Keep the claim at this level even if no speed benefit appears. |
| Simplify | The simpler script achieves the same demonstrated consumer protections with less maintained code or duplicated configuration. Retain the arithmetic/tests; merge or remove unnecessary wrappers. |
| Redirect toward Vela | The recurring work is accepted-state correction or attributed handoff, while calculation is already solved. Adopt Vela around the native checker rather than recreate its authority machinery. |
| Redirect toward Lean or a backend | A stable theorem repeatedly needs stronger verification, or an actual supported task exceeds the bounded checker. Change the implementation behind an explicit versioned contract; do not silently widen the old guarantee. |
| Retire the component | It has no willing consumer after the next three suitable research tasks, or maintaining its contract costs more than the demonstrated reuse it provides. Preserve fixtures and findings; this does not retire the programme. |

A comparison is uninformative about speed when both workflows finish trivially and timing noise dominates; it can still establish correctness. A same-author simulated successor is not an independent user study. The packet requires that distinction in reporting.

## 8. Confidence and what could change this recommendation

| Proposition | Basis and confidence | Main limitation / evidence that would change the judgment |
|---|---|---|
| Writ’s mechanical provenance is not a mathematical validator. | **High; directly inspected contract and relevant source.** | A future explicitly versioned semantic extension would require a fresh judgment. |
| Vela offers a relevant scientific-state boundary. | **High about documented/source-level design; untested locally.** | A real native-calculator integration would establish usability; a failed one could change the adoption route. |
| The finite exact operation is implementable. | **High within the tested cases; derived formulas and executed probe.** | Full hostile-input and whole-output testing remain necessary. |
| This is the right first engineering investment. | **Moderate; recommended judgment.** | Equal-input baseline evidence or real workflow observation may favor a simpler script, Vela, or Lean first. |
| This architecture generalizes across mathematical branches. | **Low-to-moderate; hypothesis only.** | A genuinely different second mathematical consumer/backend must demonstrate it without forcing misleading semantics. |
| This produces cumulative decision knowledge or external adoption. | **Not established.** | Repeated, independently usable results and real correction/reuse must be observed. |

The durable lesson from Vela is to choose a narrow technical responsibility worth being dependable at. Here that responsibility is not “store science” but **“check this answer for this question before another program builds on it.”** It is a credible foundation, not a demonstrated destination.

## Source and execution register

References below identify what was inspected, not a claim that every linked repository or specification was audited. Web documentation was accessed on 6 September 2026. Moving documentation versions are reported as displayed, not as installation pins.

**[B1] Governing user brief.** `RUN_THIS_NEXT_WRIT_ENGINEERING_FOUNDATIONS_AND_FIRST_BUILD.md`, prepared 6 September 2026; read in full. Especially §§3.2–3.3, 5, 8–10. The historical mathematical statuses are inherited from this source.

**[W1] Writ governing/current material.** Commit `20f0473afa62ed3c6e0433a21b189d1d9d1712d6`; full `AGENTS.md`, `README.md`, and `docs/current/product-definition.md`.  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/AGENTS.md`  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/README.md`  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/docs/current/product-definition.md`

**[W2] Writ provenance contract and hashing.** Same commit; full `packages/provenance/README.md` and `src/hash.ts`; hash source blob `ec39fef8fdd1b5e14231c05cd94b8e8603c65bc5`.  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/packages/provenance/README.md`  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/packages/provenance/src/hash.ts`

**[W3] Writ distribution and relevant tests.** Same commit; full package manifest, `test/profile-conformance.test.ts`, and `test/packed-consumer.mjs`. Read, not run.  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/packages/provenance/package.json`  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/packages/provenance/test/profile-conformance.test.ts`  
`https://github.com/saykig/Writ/blob/20f0473afa62ed3c6e0433a21b189d1d9d1712d6/packages/provenance/test/packed-consumer.mjs`

**[V1] Vela architecture.** Commit `017bca6bfaa29e96d8e1b0819979c732d3320917`; `docs/ARCHITECTURE.md` lines 1–190 inspected. Current README also read through the public repository view.  
`https://github.com/vela-science/vela/blob/017bca6bfaa29e96d8e1b0819979c732d3320917/docs/ARCHITECTURE.md`

**[V2] Vela evidence.** Same commit; full `docs/EVIDENCE.md`, blob `4656e460b1d104090388e57c0e3b2fabf7b3f841`. Its demonstrated-CLI paragraph names `v0.977.5`; do not relabel that qualification as a local test of `0.977.6`.  
`https://github.com/vela-science/vela/blob/017bca6bfaa29e96d8e1b0819979c732d3320917/docs/EVIDENCE.md`

**[V3] Vela manifest.** Same commit; full `Cargo.toml`.  
`https://github.com/vela-science/vela/blob/017bca6bfaa29e96d8e1b0819979c732d3320917/Cargo.toml`

**[V4] Vela verification implementation and embedded tests.** Same commit; `crates/vela-protocol/src/objects/verification_record.rs` read through its end in two ranges, blob `fc2dc8b6e4e2814d95ccdb16a6a28c5db8c64b6e`. Tests not run.  
`https://github.com/vela-science/vela/blob/017bca6bfaa29e96d8e1b0819979c732d3320917/crates/vela-protocol/src/objects/verification_record.rs`

**[F1] Python rational arithmetic.** Python 3.13 documentation, page displaying 3.13.15; constructor and exactness sections inspected. Local probe runtime was 3.13.5.  
`https://docs.python.org/3.13/library/fractions.html`  
The built-in-types integer/string conversion limit was also inspected to set conservative Build 1 numeric bounds.  
`https://docs.python.org/3.13/library/stdtypes.html#integer-string-conversion-length-limitation`

**[F2] Lean proof validation.** Current reference, displayed 4.34.0-rc2; proof/statement distinction, axiom checks, external-checker and compiler-trust sections inspected. No local proof build.  
`https://lean-lang.org/doc/reference/latest/ValidatingProofs/`

**[F3] Mathlib rational representation.** Generated API for `Mathlib.Data.NNRat.Defs`; representation-level inspection only. No pinned compiled library integration.  
`https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/NNRat/Defs.html`

**[F4] Storm.** Official engine documentation and running tutorial, especially the PRISM die example and exact-mode discussion. The tutorial includes historical command-output versions; they are not a current installed-version claim.  
`https://www.stormchecker.org/documentation/background/engines.html`  
`https://www.stormchecker.org/documentation/usage/running-storm.html`

**[F5] MMT.** Modules and setup documentation; live GitHub latest-release metadata returned `v27.0.0`, published 7 September 2025, with `mmt.jar`. Availability of an artifact was observed, not its execution.  
`https://uniformal.github.io/doc/language/modules`  
`https://uniformal.github.io/doc/setup/`  
`https://github.com/UniFormal/MMT/releases/tag/v27.0.0`

**[F6] W3C PROV-DM.** W3C Recommendation, 30 April 2013; overview of components and derivation/revision/quotation definitions inspected.  
`https://www.w3.org/TR/prov-dm/`

**[F7] RO-Crate and Process Run Crate.** RO-Crate 1.2 landing page, accessible 1.3 provenance section, and Process Run Crate overview/requirements/multiple-process sections. Process page header `0.5`; embedded example version mismatch noted above.  
`https://www.researchobject.org/ro-crate/specification/1.2/`  
`https://www.researchobject.org/ro-crate/specification/1.3/provenance.html`  
`https://www.researchobject.org/workflow-run-crate/profiles/process_run_crate/`

**[F8] Nanopublication Guidelines.** Working draft; basic elements, well-formedness criteria, example, and integrity-key sections inspected.  
`https://nanopub.net/guidelines/working_draft/`

**[F9] AiiDA.** Concepts page, displayed documentation 2.9.2; full conceptual page read.  
`https://aiida.readthedocs.io/projects/aiida-core/en/stable/topics/provenance/concepts.html`

**[F10] Snakemake.** CLI reference, displayed documentation 9.26.1; rerun-trigger option inspected, not the entire CLI reference.  
`https://snakemake.readthedocs.io/en/stable/executing/cli.html`

**[P1] Executed local probe.** Standard-library Python, 12 fixed fixtures; no model grid. Full reproduction source is embedded in the build packet’s Appendix A. Command: `python spike.py`. Expected stdout and hashes are retained there. Source SHA-256: `bf8ede7d901cafb20dda96f3c3824cfe48e446a8308cdaad361a25a9673977d8`; result-file SHA-256 under Python 3.13.5: `4775493a22c3dd98773582ae4ea566543e1a052d73d8e8525f9dd3d3b2badd2b`.
