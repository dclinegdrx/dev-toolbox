---
description: Finalize the current discussion into a phased implementation plan.
subagent: false
---

Finalize the implementation plan based on everything we have discussed so far.

Stay in this session with the currently selected agent and model. Do not switch
agents or models.

Before writing it, do one final pass against the repository and make sure the plan reflects the actual codebase, existing architecture, conventions, tests, and constraints. Resolve any remaining ambiguity you can from the code rather than guessing.

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

Status: NOT STARTED

Use only these status values throughout the plan:

* NOT STARTED
* IN PROGRESS
* COMPLETE

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
* Important assumptions or constraints.
* Risks or areas that deserve particular attention during implementation.
* Any final integration or end-to-end verification that should happen after all phases are complete.

The plan should contain enough context that a capable implementation agent with no knowledge of our current conversation can execute it successfully.

The phase status is the authoritative record of implementation progress. Future implementation agents should use it to determine which phase should be worked on next.

Do not implement the changes yet.

Write the completed plan as a Markdown file under `docs/plans/`.

Choose a concise, descriptive filename based on the work. If `docs/plans/` does not exist, create it.

After writing the file, tell me the path and give me a short summary of the phases you created.
