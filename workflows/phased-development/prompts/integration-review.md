The implementation plan in `{clipboard}` has completed its implementation phases. Perform a final integration review of the entire change.

This is read-only by default: do not edit files, stage, commit, push, reset, clean, restore, switch branches, or delegate work. Use these instructions as safe defaults, not as a reason to stop unnecessarily. Use reasonable engineering judgment and disclose small, safe deviations. Ask for clarification only when the comparison base or review scope cannot be determined safely enough to provide a meaningful review.

Start by:

1. Reading the complete implementation plan and confirming that every phase is `COMPLETE`. If a phase is incomplete, explain that the planned workflow has not finished and report only any clearly useful preliminary observations.
2. Identifying the current branch and HEAD.
3. Determining the comparison base:
   - Use a base branch or reference named in the plan when it is valid.
   - Otherwise, determine the repository's remote default branch.
   - Calculate the merge base between that reference and HEAD.
   - Ask before proceeding if the correct base cannot be determined unambiguously.
4. Reviewing all changes from the merge base through HEAD, not only the newest commit.
5. Inspecting relevant surrounding code, configuration, interfaces, tests, and verification evidence as needed to understand the complete integration.

Evaluate the completed work as a whole. Look specifically for:

* Requirements from the plan that were missed or only partially implemented.
* Incorrect assumptions that became apparent during implementation.
* Integration problems between phases or behavior that may fail end to end.
* Missing edge cases, error handling, concurrency controls, retries, idempotency, transactions, or data-integrity protections where relevant.
* Insufficient, misleading, or overly narrow test coverage.
* Regressions, backward-compatibility risks, or API, schema, persistence, event, and configuration inconsistencies.
* Observability gaps, including missing logs, metrics, traces, useful error context, or operational documentation where relevant.
* Security, authorization, privacy, or sensitive-data concerns.
* Unnecessary complexity, dead code, temporary scaffolding, unresolved TODOs, incomplete cleanup, or changes outside intended scope.
* Anything that would prevent the branch from being ready for QA or review.

Assess whether the phase-level verification is sufficient when considered together. You may run safe, non-mutating checks when they materially improve confidence and fit the repository workflow. Otherwise, recommend the additional integration, end-to-end, regression, or manual verification that should happen; never imply an unrun check passed.

Report findings in severity order:

## Critical

Issues that should be fixed before the change moves forward. Say `None` if there are no findings.

## Important

Issues likely worth addressing before QA or merge. Say `None` if there are no findings.

## Minor

Lower-risk cleanup or maintainability improvements. Say `None` if there are no findings.

## Verification Recommendations

Additional tests or checks recommended before QA. Say `None` if no additional verification is needed.

For every finding, explain:

* The problem and relevant file, code path, or plan requirement.
* The likely impact.
* A concrete fix or next step.

Finish with one overall assessment:

* `READY FOR QA`
* `READY WITH MINOR FOLLOW-UP`
* `NOT READY`

Explain the assessment concisely. Do not make changes.

At the end of the response, please re-iterate the plan doc path this work is related to.
