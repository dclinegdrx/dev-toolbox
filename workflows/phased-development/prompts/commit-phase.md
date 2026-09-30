I have reviewed and accepted the implementation for the phase just completed in `{clipboard}` and have staged all implementation work intended for its commit. Finalize that phase as one commit.

Treat this as finalization, not a second implementation pass. Use these instructions as safe defaults, not as a reason to stop unnecessarily. Preserve unrelated user work and use reasonable engineering judgment. Proceed with small, safe deviations when they improve alignment with the repository, and disclose them in your final report. Ask for clarification only when proceeding could cause data loss, an incorrect commit, a material design change, an inaccurate workflow status, or another consequential outcome.

## Finalization workflow

1. Read the plan and identify the first phase not marked `COMPLETE`. Confirm it is the accepted phase and is `IN PROGRESS`.
2. Inspect the current branch, HEAD, and complete worktree state, including staged, unstaged, and untracked changes. Review the relevant staged and unstaged diffs before changing the index.
3. Identify the files and artifacts required by the accepted phase from the plan, implementation report, and my review. Treat the existing staged implementation diff as my proposed commit scope.
4. Confirm that the staged implementation diff contains every required phase file and artifact, and contains no unrelated changes. Preserve unrelated work.
5. If a file or artifact clearly required by the accepted phase is unstaged or untracked, stop without changing the plan status or staging implementation files. Report the exact missing paths and why they belong in the phase so that I can review and stage them before retrying. Do not stage, unstage, or otherwise reconcile implementation files yourself.
6. If the staged scope includes unrelated changes, or the relationship of local changes to the phase cannot be determined safely, stop without changing the plan status and explain what I need to resolve. Do not adjust implementation staging yourself.
7. Use the implementation report and my review as verification evidence. Run only checks that are missing, explicitly required, or directly affected by finalization. Do not repeat broad checks that already passed against unchanged implementation without a reason.
8. Change only the accepted phase in the plan from `IN PROGRESS` to `COMPLETE`, then stage that plan-file change.
9. Review the complete final staged diff. Confirm it contains the accepted staged implementation work and only the corresponding plan-status transition.
10. Create one appropriate commit. Do not push.

## Commit Message Instructions

Refer to the the git-commit skill for standard commit message generation instructions.

## Recovery rule

Do not leave a failed finalization with an uncommitted phase marked `COMPLETE`. If validation, final-diff review, or commit creation fails after the status was changed, restore only that phase to `IN PROGRESS`, stage the repaired plan file, leave implementation staging unchanged, and report what must be resolved before retrying. If the plan was already stranded at `COMPLETE` from an earlier failed attempt and no commit was created, repair only that phase to `IN PROGRESS` before continuing.

Do not edit implementation files; stage or unstage implementation files; push; amend; rebase; reset; clean; restore; switch branches; or create extra commits as part of finalization. You may stage only the plan-file status update or its recovery repair. If the implementation itself needs substantive changes, or if I need to revise staging, leave the phase `IN PROGRESS` and return it for implementation, review, or staging.

When finished, report the commit hash and message, the committed files, verification used, any files intentionally excluded, and any recovery or deviation applied. If stopping because staging is incomplete, report the exact paths I need to review and stage before retrying.

At the end of the response:
- re-iterate the plan doc path this work is related to
- plan steps listed out including their status
