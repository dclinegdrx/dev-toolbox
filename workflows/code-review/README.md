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

## Example review outline

The [Go manager review](prompts/go/manager-review.md) produces a concise report
that separates business context, existing feedback, material residual risk, and
the conversation a manager may need to have. This illustrative example uses
placeholders rather than a real pull request:

### A. Business and PR context

- **Jira:** `TEAM-123` — add idempotency to a fulfillment retry path.
- **PR:** `[TEAM-123] fix: avoid duplicate delivery requests` by `@author`.
- **Observed validation:** unit tests passed; no end-to-end replay test found.
- **Risk:** Medium. The affected path can issue an external request more than
  once after a timeout.

### B. Existing-review triage

| Thread | Author/type | Status | Disposition | Why |
| --- | --- | --- | --- | --- |
| Retry counter is not reset | Automated reviewer | Open | Existing thread - no action | It already identifies the same failure path and recommends the needed test. |

### C. Review summary

- The retry state is now persisted before the external call, which addresses
  the main duplicate-delivery risk.
- Existing automated feedback covers the missing counter-reset test.
- One minor new finding remains: the changed retry path has no test for a
  process restart between persistence and replay.
- A human should confirm replay behavior with the external vendor before
  approval.

### D. New findings and worthwhile replies

**New — Minor — Test coverage — High confidence — Non-blocking**

- **File:** `internal/fulfillment/retry.go:142`
- **Issue:** The new persisted retry state is not exercised across a process
  restart.
- **Failure scenario:** A worker can persist the retry marker, restart before
  completing the request, and replay with a stale in-memory counter.
- **Evidence:** The added tests cover a timeout in one process but do not
  recreate the handler or reload the persisted state.
- **Smallest recommendation:** Add a focused restart-and-replay test.
- **Action:** New PR comment.
- **Draft comment:** `Could we add a restart-and-replay case here? The current
  tests cover a timeout, but not whether a freshly initialized worker reloads
  the persisted retry state before issuing the request again.`

### E. Manager narrative

> The implementation addresses the primary retry-safety concern. Before
> approval, I would ask for confirmation that a timed-out request can be replayed
> safely by the vendor, that the existing counter-reset test is added, and that
> the retry state survives a worker restart. I do not see a blocker, but the
> restart case is a worthwhile regression test before this path changes again.

## Available prompts

| Prompt | Use when |
| --- | --- |
| [Go manager review](prompts/go/manager-review.md) | You want a manager-focused PR review that triages existing automated and human review threads before identifying residual risk. |
| [Agent DevTools manager review](prompts/agent-devtools/manager-review.md) | You are reviewing agent skills, shared tooling, CLI/catalog behavior, or install and discovery flows. |
| [API specs manager review](prompts/api-specs/manager-review.md) | You are reviewing API contracts, schema evolution, compatibility, and consumer impact. |
| [Domain Graph manager review](prompts/domain-graph/manager-review.md) | You are reviewing GoodRx Domain Graph schema, resolver, service, API-client, or GraphQL platform changes. |
| [Fastly infrastructure manager review](prompts/fastly-infrastructure/manager-review.md) | You are reviewing Fastly, Terraform, VCL, routing, caching, or production rollout changes. |
| [Observability manager review](prompts/observability/manager-review.md) | You are reviewing GoodRx observability monitors, dashboards, routing, or Groundcover migration work. |
| [Retool manager review](prompts/retool-src-ctrl/manager-review.md) | You are reviewing Retool UI, query wiring, generated metadata, resource, or operational-workflow changes. |
| [Singularity manager review](prompts/singularity/manager-review.md) | You are reviewing Singularity frontend, analytics, state-machine, GraphQL, or Lifecycle-preview changes. |
| [Follow-up review](prompts/shared/follow-up-review.md) | An author has updated a PR in response to prior review feedback. |

See [prompt organization](prompts/README.md) before adding prompts for another
language, project, or review role.
