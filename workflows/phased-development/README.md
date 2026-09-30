# Phased Development Workflow

This workflow turns an agreed outcome into small, reviewable changes. It has
two implementations with the same lifecycle: portable Markdown prompts for any
agent launcher, and an installable OpenCode package.

## Lifecycle

1. **Plan** — investigate the repository and write a dated implementation plan
   under `docs/plans/`.
2. **Implement one phase** — select the next incomplete phase, make only its
   changes, and verify them.
3. **Review, stage, and finalize** — a human reviews and stages the accepted
   implementation. Finalization changes that phase's status and creates one
   commit; it does not push.
4. **Repeat and review the branch** — repeat for each phase, then perform a
   read-only integration review of the full branch.

Plans use only these authoritative phase statuses:

- `NOT STARTED` — no implementation has begun.
- `IN PROGRESS` — implementation is underway or awaiting human review and
  finalization.
- `COMPLETE` — human review accepted the phase and its finalization commit was
  created.

Only one phase should be active at a time. Implementers never mark a phase
`COMPLETE`, stage, commit, or push. A human accepts and stages the work before
the separate finalization step. The workflow never pushes automatically, and
the final integration review covers the full branch rather than only its latest
commit.

## Implementations

| Implementation | Use it when | Start here |
| --- | --- | --- |
| Portable prompts | You want launcher-neutral Markdown prompts for Alfred, another launcher, or manual copy/paste. | [Portable prompts](prompts/README.md) |
| OpenCode package | You use OpenCode V2 and want installed slash commands, agents, and a skill. | [OpenCode package](opencode/README.md) |

The portable prompts are self-contained. The OpenCode package uses its own
agents, commands, skill, and installation mechanics. Both implementations are
available under this workflow directory.

## Parity and intentional differences

Both implementations use the lifecycle and safety boundaries above. The plan
defines the intended outcome; the repository defines the implementation
details. They preserve unrelated local work, allow and report minor repository
drift, and require clarification for material architecture, contract,
migration, security, compatibility, or phase-boundary changes.

| Lifecycle stage | Portable prompt | OpenCode command | OpenCode agent or skill |
| --- | --- | --- | --- |
| Plan | [Finalize plan](prompts/finalize-plan.md) | `/workflow/finalize-plan` | Current-session command; [`planner.md`](opencode/agents/workflow/planner.md) is optional when directly selected |
| Implement a phase | [Implement phase](prompts/implement-phase.md) | `/workflow/start-phase <plan> <phase>` | `coordinator.md` routes to an implementer; [phase-implementation skill](opencode/skills/phase-implementation/SKILL.md) |
| Review, stage, and finalize | [Commit phase](prompts/commit-phase.md) | `/workflow/commit-phase <plan> <phase>` | `phase-committer.md` and the external `git-commit` skill |
| Full-branch review | [Integration review](prompts/integration-review.md) | `/workflow/integration-review <plan>` | `integration-reviewer.md` |

The portable implementation selects the next incomplete phase itself. OpenCode
commands instead require an explicit phase number, validate that it is next,
and use a coordinator to route work to a child session and model. The
`/workflow/finalize-plan` command stays in the active session and retains its
selected agent and model; `planner.md` remains an optional directly selected
agent.

OpenCode's integration reviewer is read-only by permission. It reviews
available evidence and recommends mutable checks rather than running them; it
must never report an unrun check as passing. The implementations intentionally
share guarantees rather than identical wording or mechanics.
