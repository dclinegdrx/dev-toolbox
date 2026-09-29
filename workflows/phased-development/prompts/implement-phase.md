Implement and verify the next incomplete phase in `{clipboard}`.

Treat the implementation plan as the source of truth for the requested outcome, while treating the current repository as the source of truth for implementation details. Use these instructions as safe defaults, not as a reason to stop unnecessarily. Preserve unrelated user work and use reasonable engineering judgment. Proceed with small, safe deviations when they improve alignment with the repository, and disclose them in your final report. Ask for clarification only when proceeding could cause data loss, incorrect scope, a material design change, inaccurate workflow status, or another consequential outcome.

## Phase-status rules

Implementation and human review/commit have separate responsibilities:

* If the next actionable phase is `NOT STARTED`, change only that phase to `IN PROGRESS` before implementation.
* If it is already `IN PROGRESS`, continue it.
* Never mark a phase `COMPLETE` during implementation, even if verification passes.
* A phase becomes `COMPLETE` only after human review and the separate commit/finalization step.

## Before implementation

1. Read the entire plan and confirm the path is valid.
2. Identify the first phase that is not `COMPLETE`.
3. Inspect the current branch, HEAD, and worktree, including staged, unstaged, and untracked changes.
4. Confirm that the selected phase is the active phase. Normally there is only one `IN PROGRESS` phase. If status is stale or duplicated but the safe active phase is obvious, continue and report it. Ask only if the active phase cannot be determined safely.
5. If the selected phase is `NOT STARTED`, update only it to `IN PROGRESS`. Leave it unchanged if it is already `IN PROGRESS`.
6. Inspect the relevant code, tests, and repository guidance. Confirm that the plan's assumptions are still materially sound.

Do not overwrite, discard, stage, or commit unrelated user work. Unrelated local changes do not by themselves block implementation: continue if they can be safely left alone and do not overlap the phase. Pause and ask if existing changes overlap the intended work, make the phase boundary unclear, or could be mistaken for this phase's output.

For minor plan drift—such as moved files, renamed tests, or a better established local pattern—adapt the implementation and document the deviation. Pause before material changes to the plan's architecture, public or cross-service contracts, data model or migration strategy, security boundary, backward compatibility, or phase boundaries.

## Implementation and verification

Implement only the selected phase.

* Follow existing architecture, naming, and conventions; prefer the smallest clean solution that satisfies the phase.
* Add or update tests appropriate to the behavior changed.
* Do not perform unrelated cleanup or casually implement later phases. If a small adjacent change is strictly necessary, keep it narrow and explain it.
* Do not stage, commit, push, reset, clean, restore, switch branches, or mark a phase `COMPLETE`.
* Prefer clear, inspectable commands and repository-provided scripts. Do not hide failures. Combine simple dependent commands only when doing so remains easy to understand and diagnose.

After implementation:

1. Run the verification described in the phase when applicable.
2. Run focused tests and any useful formatting, linting, type checking, builds, or other repository checks appropriate to the changes.
3. If a useful check cannot run because it is unavailable, environment-dependent, too expensive, or otherwise unsuitable, report that limitation rather than claiming success.
4. Review the complete diff for unintended changes, missing cases, unnecessary complexity, and work belonging to another phase. Correct issues that are clearly within this phase.
5. Leave the phase `IN PROGRESS` and do not commit.

When finished, report:

* The implemented phase and its title.
* Starting branch and HEAD.
* Files changed and behavior implemented.
* Tests and verification performed, including results and any checks not run.
* Whether the completion criteria appear satisfied.
* Deviations from the plan and why.
* Assumptions, risks, follow-up concerns, and unrelated work intentionally left untouched.
* Areas that deserve particular human attention during diff review.

Stop after this phase. Do not begin another phase.

At the end of the response:
- re-iterate the plan doc path this work is related to
- plan steps listed out including their status
