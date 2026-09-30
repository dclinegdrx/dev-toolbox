---
description: Mark an accepted phase complete and commit the staged changes.
agent: workflow/phase-committer
subagent: true
---

I have reviewed and accepted the implementation for Phase $2 in `$1` and have
staged all implementation work intended for its commit. Finalize that phase as
one commit.

Load and follow the `git-commit` skill.

Treat this as finalization, not a second implementation pass. If an earlier
failed attempt stranded Phase $2 at `COMPLETE` without creating its commit,
repair only that phase to `IN PROGRESS` before normal validation. Then confirm
Phase $2 is the first incomplete phase and is `IN PROGRESS`. Inspect the
complete worktree and staged and unstaged diffs, then treat the staged
implementation diff as the human's proposed commit scope.

Before changing the plan status, stop if any required implementation artifact
is unstaged or untracked, the staged scope includes unrelated work, or its
relationship to Phase $2 is unclear. Do not stage, unstage, or edit
implementation files. Do not proceed unless `$1` is under `docs/plans/`.

Use existing implementation evidence and run only missing or directly affected
checks. Change only Phase $2 from `IN PROGRESS` to `COMPLETE`, stage only that
plan-file update, review the complete final staged diff, and create one commit.
Do not push.

If validation, final staged-diff review, or commit creation fails after the
status update, repair only Phase $2 to `IN PROGRESS`, stage that repair, leave
implementation staging unchanged, and report what must be resolved.

Report the plan path and phase statuses, commit hash and message, committed
files, verification actually used, any intentionally excluded files, and any
recovery or deviation.
