---
name: Phase Implementation
description: Implement and verify one explicitly assigned phase from an implementation plan.
---

# Phase Implementation

Implement and verify exactly the phase identified in the assignment.

Treat the referenced implementation plan as the source of truth.

## Status rules

- If the assigned phase is `NOT STARTED`, change it to `IN PROGRESS` before implementation.
- If it is already `IN PROGRESS`, continue it.
- Never mark a phase `COMPLETE`.
- Only the separate human review and commit workflow may mark it `COMPLETE`.

## Before implementation

1. Read the entire plan.
2. Confirm the assigned phase exists.
3. Confirm it is the first phase that is not `COMPLETE`.
4. Confirm no different phase is currently `IN PROGRESS`.
5. Inspect the relevant code and tests.
6. Inspect the current branch, HEAD, worktree status, and staged changes.
7. Confirm that the plan's assumptions still match the codebase.

Stop and report the problem if:

- The assigned phase is not the next actionable phase.
- The worktree contains unexpected staged or unstaged changes.
- An earlier phase is incomplete.
- The plan materially conflicts with the codebase.
- A significant design decision is required that the plan did not resolve.

## Implementation requirements

- Implement only the assigned phase.
- Add or update appropriate tests.
- Follow existing architecture, naming, and conventions.
- Prefer the smallest clean implementation.
- Do not perform unrelated cleanup.
- Do not implement later phases.
- Do not commit, push, or stage implementation changes.

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
- Tests and verification, including results
- Whether the completion criteria appear satisfied
- Deviations from the plan
- Assumptions, risks, or follow-up concerns
- Areas requiring particular human review

Stop after this phase.
