---
description: Select an implementation model and delegate one plan phase.
agent: workflow/coordinator
subagent: false
---

Coordinate implementation of Phase $2 from the plan at `$1`.

Do not implement it yourself.

Read the complete plan, validate that Phase $2 is the next actionable phase,
apply your model-routing policy, and select exactly one configured phase
implementer.

Tell me:

- Selected implementation agent and model
- Why it was selected
- Any concern discovered before delegation

Then launch the selected agent in a fresh background child session with this
assignment:

"Implement and verify Phase $2, <title from the plan>, from `$1`.

Read the entire plan before changing anything. Confirm that this is the next
actionable phase. Load and follow the `phase-implementation` skill.

Starting branch: <current branch>. Starting HEAD: <current HEAD>.

Do not commit, push, stage changes, mark the phase COMPLETE, or start another
phase. Stop with the worktree ready for human review."
