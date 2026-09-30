---
description: Finalize the current discussion into a phased implementation plan.
mode: primary
model: gdrx-litellm/gpt-5.6-sol#high
steps: 50
permissions:
  - action: subagent
    resource: "*"
    effect: deny
  - action: edit
    resource: "*"
    effect: deny
  - action: edit
    resource: "docs/plans/*"
    effect: allow
  - action: shell
    resource: "*"
    effect: deny
  - action: shell
    resource: "git status *"
    effect: allow
  - action: shell
    resource: "git diff *"
    effect: allow
  - action: shell
    resource: "git log *"
    effect: allow
  - action: shell
    resource: "git show *"
    effect: allow
  - action: shell
    resource: "git branch *"
    effect: allow
  - action: shell
    resource: "git rev-parse *"
    effect: allow
---

Finalize the implementation plan based on everything we have discussed so far.

Treat the plan as the source of truth for the intended outcome and the
repository as the source of truth for implementation details. Preserve
unrelated local work. Resolve ordinary ambiguity from the code rather than
guessing, disclose minor repository drift, and ask before a material
architecture, contract, migration, security, compatibility, or phase-boundary
change. Do not implement, stage, commit, or push in this step.

Before writing it, do one final pass against the repository and make sure the
plan reflects the actual codebase, existing architecture, conventions, tests,
deployment or operational constraints, and existing work.

Structure the work into clear implementation phases.

Each phase should:

* Represent a coherent, reviewable commit.
* Leave the repository in a valid state when complete.
* Build naturally on the previous phases.
* Be independently verifiable where practical.
* Include the implementation work required for that phase.
* Include appropriate tests as part of the implementation work, unless there is a specific reason testing should be a separate phase.
* Include explicit verification steps and completion criteria.
* Avoid pulling in work that belongs to later phases.
* Prefer vertical slices of working behavior over phases organized only by architectural layer or file type.

Every phase must include an explicit status field. When the plan is first created, set every phase to:

**Status: NOT STARTED**

Use only these status values throughout the plan:

* `NOT STARTED`
* `IN PROGRESS`
* `COMPLETE`

For each phase, use this structure:

## Phase N: <descriptive outcome>

**Status: NOT STARTED**

### Goal

Describe what should be true when this phase is complete.

### Implementation

Describe the concrete changes required, including relevant files, components, interfaces, tests, migrations, configuration, or other work where known.

### Verification

Describe the exact tests, commands, checks, or manual verification that should be performed.

### Completion Criteria

List the observable conditions that indicate the phase is complete and ready to commit.

Also include:

* A short overview of the intended solution and architecture.
* Important assumptions and constraints.
* Risks, failure modes, and areas that deserve particular attention during implementation.
* Relevant observability, security, privacy, performance, retry, idempotency,
  data-integrity, or backward-compatibility concerns.
* Rollout, migration, or rollback considerations when applicable.
* Any final integration, end-to-end, regression, or manual verification that
  should happen after all phases are complete.
* The intended base branch or comparison reference when it is known.

The plan should contain enough context that a capable implementation agent with no knowledge of our current conversation can execute it successfully.

The phase status is the authoritative record of implementation progress. Future implementation agents should use it to determine which phase should be worked on next.

Do not implement the changes yet.

Write the completed plan as a concise Markdown file under `docs/plans/`. If
that directory does not exist, create it. Choose a descriptive filename that
begins with the current date in ISO 8601 format (`YYYY-MM-DD`), followed by a
short kebab-case description:

`docs/plans/YYYY-MM-DD-<descriptive-plan-name>.md`

After writing the file, report the path, phase summary and statuses, important
assumptions or risks, and any small safe deviations.
