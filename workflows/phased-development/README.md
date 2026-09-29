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
| OpenCode package | You use OpenCode V2 and want installed slash commands, agents, and a skill. | [OpenCode package](../../opencode/README.md) |

The portable prompts are self-contained. The OpenCode package uses its own
agents, commands, skill, and installation mechanics. The package remains at
the repository root during this phase; it will be colocated with these prompts
in a later change.
