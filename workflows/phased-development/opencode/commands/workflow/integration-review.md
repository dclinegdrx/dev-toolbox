---
description: Review the completed implementation against its base branch.
agent: workflow/integration-reviewer
subagent: true
---

Perform a final integration review using the implementation plan at `$1`.

This is read-only: do not edit files, stage, commit, push, reset, clean,
restore, switch branches, or delegate work. First read the entire plan and
confirm every phase is `COMPLETE`. If one is incomplete, explain that the
workflow has not finished and report only clearly useful preliminary
observations.

Determine the comparison base before reviewing:

1. Identify the current branch and HEAD.
2. Check whether the plan identifies a base branch.
3. Otherwise, determine the remote default branch using Git.
4. Calculate the merge base between that branch and HEAD.
5. If the base cannot be determined unambiguously, stop and ask me.

Review all changes between the merge base and HEAD, not only the latest commit.
Treat the plan as the outcome source of truth and the repository as the
implementation-detail source of truth. Inspect relevant code, configuration,
tests, and available verification evidence.

Follow your integration-review instructions and report findings by severity.
State the plan path, phase statuses, checks actually run, recommended mutable
checks, and any review limitations or deviations; never claim an unrun check
passed.
