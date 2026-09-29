---
description: Review the completed implementation against its base branch.
agent: workflow/integration-reviewer
subagent: true
---

Perform a final integration review using the implementation plan at `$1`.

Determine the comparison base before reviewing:

1. Identify the current branch and HEAD.
2. Check whether the plan identifies a base branch.
3. Otherwise, determine the remote default branch using Git.
4. Calculate the merge base between that branch and HEAD.
5. If the base cannot be determined unambiguously, stop and ask me.

Review all changes between the merge base and HEAD, not only the latest commit.

Do not modify files. Follow your integration-review instructions and report
findings by severity.
