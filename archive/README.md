# Retirement archive

This directory preserves material that is no longer part of the active build or day-to-day
workflow. Nothing was deleted during the September 2026 repository cleanup. Files were moved with
Git so their history remains available.

Historical documents may mention their original paths. Those mentions are retained when they
describe the state that was reviewed or executed; the relocation table below is the current source
of truth.

| Current location | Original location | Original purpose | Retirement reason and status |
| --- | --- | --- | --- |
| `experiments/build1-research-probe/` | `research_probe/` | Isolated fixed-fixture engineering probe supplied with the Build 1 packet | The probe predates the active package and test suite. Its source, fixtures, and results are frozen for provenance; it is not an active test or KL experiment. |
| `instructions/build1/` | `sources/RUN_THIS_NEXT_WRIT_ENGINEERING_BUILD_1.md` | One-time Build 1 execution brief and embedded archival appendix | Build 1 was completed and reviewed. The brief remains useful only as a historical statement of the original assignment. |
| `review-inputs/pr1/` | `sources/pr1-repair/` | Two adversarial reviews and two repair packets for PR #1 | PR #1 and its repairs are closed. Durable outcomes remain in `docs/reviews/pr1/` and `evidence/`. |
| `artifacts/build1-development/` | `outputs/development/` | Preliminary comparison snapshots produced before the final Build 1 ledger | Superseded by the final checked artifacts in `outputs/` and later evidence records. The preliminary bytes remain preserved. |

No tests were retired. The former `tests_build2/` suite was moved into the active `tests/` directory
so one discovery command now exercises the complete project.
