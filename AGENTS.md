# Engineering workflow

Do not create branches unless the user instructs you to. Commit and push completed work regularly.
Do not merge a pull request unless the user explicitly authorizes it.

Cloud-first is the default for this project. Start from the current GitHub repository and relevant
PR or branch. Prefer Codex Cloud for implementation, repairs, reviews, tests, and evidence generation.
Commit completed work to the appropriate branch, push it, and open a PR if none exists or update the
existing PR. Return the exact commit SHA and PR link.

Keep durable engineering evidence in the repository when appropriate. Preserve historical evidence,
source identities, and disclosed limitations; distinguish later assessments from earlier results.

Avoid creating local clones, sibling repositories, review directories, tar archives, duplicated source
trees, generated evidence bundles, or other persistent files on the user's Mac unless the task genuinely
requires local-machine access. Keep temporary files in the cloud task environment and do not copy them
to the Mac by default. If correct execution requires local-machine access, stop and explain exactly
why before creating substantial local files. Local work is the exception.
