---
description: Mark an accepted phase complete and commit the staged changes.
agent: workflow/phase-committer
subagent: true
---

I have reviewed, verified, and staged the implementation for Phase $2 in `$1`.

Load and follow the `git-commit` skill.

1. Confirm Phase $2 is currently `IN PROGRESS`.
2. Review the staged diff, including any staged change to `$1`.
3. A staged plan-file change is expected when it changes only the assigned
   phase from `NOT STARTED` to `IN PROGRESS`. Confirm that it contains no
   other plan edits or phase-status changes.
4. Confirm the remaining staged files contain only the accepted Phase $2
   implementation.
5. Update only the assigned phase in `$1` from `IN PROGRESS` to `COMPLETE`.
6. Stage `$1` again so the final plan diff records `NOT STARTED` to
   `COMPLETE` for only the assigned phase.
7. Review the complete final staged diff.
8. Create an appropriate commit.
9. Do not push.

Stop if `$1` is not under `docs/plans/`; the staged plan change is not the
expected transition for the assigned phase; the staged diff contains unrelated
work; or the implementation does not match the phase.

Report the commit hash and message.
