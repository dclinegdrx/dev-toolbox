---
name: Phase Implementation
description: Implement and verify one explicitly assigned phase from an implementation plan.
---

# Phase Implementation

Implement and verify exactly the explicitly assigned phase.

Treat the referenced implementation plan as the source of truth for the
requested outcome and the repository as the source of truth for implementation
details. Use these rules as safe defaults, not as a reason to stop
unnecessarily.

## Status rules

- If the assigned phase is `NOT STARTED`, change it to `IN PROGRESS` before implementation.
- If it is already `IN PROGRESS`, continue it.
- Never mark a phase `COMPLETE`.
- Only the separate human review and commit workflow may mark it `COMPLETE`.

## Before implementation

1. Read the entire plan and confirm the path is valid.
2. Confirm the assigned phase exists and is the first phase not marked
   `COMPLETE`.
3. Inspect the current branch, HEAD, and complete worktree state, including
   staged, unstaged, and untracked changes.
4. Confirm the assigned phase is the active phase. Normally only one phase is
   `IN PROGRESS`; if stale or duplicated status has an obvious safe active
   phase, continue and report it. Otherwise, ask for clarification.
5. If the assigned phase is `NOT STARTED`, change only it to `IN PROGRESS`.
   Leave it unchanged if it is already `IN PROGRESS`.
6. Inspect relevant code, tests, and repository guidance. Confirm the plan's
   assumptions are still materially sound.

Preserve unrelated user work. Non-overlapping staged, unstaged, or untracked
changes do not by themselves require a stop; leave them untouched and continue
when their relationship to this phase is clear. Ask for clarification when
existing changes overlap the phase, make its boundary unclear, or could be
mistaken for its output.

Handle minor repository drift, such as moved files, renamed tests, or a better
established local pattern, when it improves alignment; disclose it in the
report. Ask before materially changing architecture, public or cross-service
contracts, data models or migrations, security boundaries, backward
compatibility, or phase boundaries.

## Implementation requirements

- Implement only the assigned phase.
- Add or update appropriate tests.
- Follow existing architecture, naming, and conventions.
- Prefer the smallest clean implementation.
- Do not perform unrelated cleanup.
- Do not implement later phases.
- Do not stage, commit, push, reset, clean, restore, switch branches, or mark
  a phase `COMPLETE`.

## Verification

1. Run the verification specified by the phase.
2. Run appropriate focused tests, formatting, linting, or builds.
3. Review the complete diff.
4. Correct unintended changes and missing cases.
5. Leave the phase `IN PROGRESS`.

## Final report

Report:

- Phase implemented
- Starting branch and HEAD
- Files changed
- Behavior implemented
- Tests and verification actually performed, including results and unrun checks
- Whether the completion criteria appear satisfied
- Deviations from the plan
- Assumptions, risks, follow-up concerns, and intentionally untouched work
- Areas requiring particular human review

Finish by reiterating the plan path and listing every plan phase with its
current status.

Stop after this phase.
