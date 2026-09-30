# Portable Phased-Development Prompts

These Markdown prompts implement the phased-development workflow without
requiring OpenCode. Use them from Alfred, another prompt launcher, or a manual
chat session.

## Usage sequence

1. Use [Finalize plan](finalize-plan.md) after investigation to create a dated
   plan under `docs/plans/`.
2. For each incomplete phase, use [Implement phase](implement-phase.md) with
   the plan path. It updates a `NOT STARTED` phase to `IN PROGRESS`, implements
   only that phase, and leaves its changes unstaged.
3. Review and verify the implementation yourself. If you accept it, stage only
   the work intended for that phase. Then use [Commit phase](commit-phase.md)
   with the plan path to finalize the accepted phase as one commit. This human
   review-and-staging boundary is deliberate: the finalization prompt must not
   decide or change implementation staging.
4. Once every plan phase is `COMPLETE`, use [Integration review](integration-review.md)
   with the plan path for a read-only full-branch review.

## Alfred setup

Create an Alfred workflow action for each prompt and paste in the prompt body.
For the three prompts that need a plan, copy the plan's repository-relative
path before invoking the action. Alfred expands `{clipboard}` to that copied
path. The finalize-plan prompt does not use a plan path because it creates one.

Keep `{clipboard}` unchanged in the stored prompt text; it is Alfred's
placeholder, not a path literal. Confirm that the copied value is the intended
plan path before running an action, especially before commit finalization.

## Manual copy/paste

Copy a prompt into your agent chat. For prompts containing `{clipboard}`,
replace that literal text with an explicit plan path, for example
`docs/plans/2026-09-28-example.md`. Do not rely on clipboard expansion when
your launcher does not support it.

See the [shared workflow README](../README.md) for lifecycle rules and a
comparison with the OpenCode implementation. These self-contained prompts
select the next incomplete phase; OpenCode instead requires an explicit phase
number and uses coordinator model routing and child sessions. The
implementations share workflow guarantees, not byte-for-byte prompt text.
