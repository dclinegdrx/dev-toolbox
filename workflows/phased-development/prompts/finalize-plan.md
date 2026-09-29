Finalize the implementation plan based on everything we have discussed so far.

Use these instructions as safe defaults, not as a reason to stop unnecessarily. Preserve unrelated user work and use reasonable engineering judgment. Proceed with small, safe deviations when they improve alignment with the repository, and disclose them in your final report. Ask for clarification only when proceeding could cause data loss, an incorrect commit, a material design change, an inaccurate workflow status, or another consequential outcome.

Before writing the plan, make a final pass through the repository. Make sure the plan reflects the actual architecture, conventions, tests, deployment or operational constraints, and existing work. Resolve ordinary ambiguity from the code rather than guessing. Do not implement, stage, commit, or push changes in this step.

Structure the work into clear implementation phases. Each phase should:

* Represent a coherent, reviewable change that can normally be committed on its own.
* Leave the repository in a valid state when complete.
* Build naturally on prior phases and avoid taking work from later phases.
* Prefer vertical slices of working behavior over phases organized only by architectural layer or file type.
* Include the implementation work, appropriate tests, and explicit verification for that phase. Keep tests with the behavior they validate unless there is a clear reason not to.
* Include observable completion criteria.
* Identify dependencies, rollout considerations, migrations, compatibility concerns, or operational follow-up when relevant.

Every phase must include a status. Set every new phase to:

**Status: NOT STARTED**

Use only these status values throughout the plan:

* `NOT STARTED`
* `IN PROGRESS`
* `COMPLETE`

Use this structure for each phase:

```markdown
## Phase N: <descriptive outcome>

**Status: NOT STARTED**

### Goal

Describe the behavior or outcome that should be true when this phase is complete.

### Implementation

Describe the concrete changes required, including relevant files, components, interfaces, tests, migrations, configuration, or other work where known.

### Verification

Describe the tests, repository commands, checks, or manual verification that should be performed. Prefer existing repository scripts and conventions. Make the steps independently understandable; do not hide expected failures or rely on opaque command sequences.

### Completion Criteria

List the observable conditions that show the phase is ready for human review and commit.
```

Also include:

* A short overview of the intended solution and architecture.
* Important assumptions and constraints.
* Risks, failure modes, and areas needing particular attention during implementation.
* Relevant observability, security, privacy, performance, retry, idempotency, data-integrity, or backward-compatibility concerns.
* Rollout, migration, or rollback considerations when applicable.
* Final integration, end-to-end, regression, or manual verification to perform after all phases are complete.
* The intended base branch or comparison reference when it is known.

The plan must contain enough context for a capable agent with no knowledge of this conversation to implement it safely. The phase status is the authoritative record of workflow progress: later implementation steps use it to identify the next actionable phase.

Write the plan as a concise Markdown file under `docs/plans/`. If that directory does not exist, create it. Choose a descriptive filename that begins with the current date in ISO 8601 format (`YYYY-MM-DD`), followed by a short kebab-case description. Use the date on which the plan is generated. The filename must follow this pattern:

`docs/plans/YYYY-MM-DD-<descriptive-plan-name>.md`

For example:

`docs/plans/2026-09-16-some-plan-filename.md`

After writing it, report the path, a short phase summary, important assumptions or risks, and any small safe deviations made while reconciling the plan with the repository.
