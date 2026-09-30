# AI-Assisted Code Review Workflows

Portable prompts for reviewing pull requests from an agentic coding harness
such as OpenCode or Claude Code. Prompts are organized by the reviewed
project's language or domain so teams can share and improve their review rubric
without coupling it to a particular harness.

## Review a pull request

1. Create or open an isolated review worktree with this repository's
   [`wtreview`](../../README.md#git-worktree-development-workflow) command:

   ```bash
   wtreview <repository> <remote-branch>
   ```

2. Start an agentic coding harness in that worktree.
3. Copy the pull request URL and run the appropriate prompt. The prompts use
   Alfred's `{clipboard}` placeholder for that URL.
4. Review the resulting findings and drafts before posting comments or taking
   other action in the pull request.

Prompts direct the agent to produce review analysis and draft comments; they do
not authorize posting comments, approving, merging, or otherwise changing the
pull request.

## Alfred and manual use

For Alfred, store a prompt body in an action and copy the PR URL before running
it. Alfred expands `{clipboard}` to the copied URL. Keep the placeholder in the
stored prompt text.

For manual use, copy the prompt into the harness and replace `{clipboard}` with
the explicit PR URL. Confirm that the URL, repository, and worktree are the
ones you intend to review before starting.

## Available prompts

| Prompt | Use when |
| --- | --- |
| [Go manager review](prompts/go/manager-review.md) | You want a manager-focused PR review that triages existing automated and human review threads before identifying residual risk. |

See [prompt organization](prompts/README.md) before adding prompts for another
language, project, or review role.
