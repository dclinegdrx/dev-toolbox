Please perform a manager-focused code review of: {clipboard}

Your job is not to duplicate automated review. Help me understand the change,
assess material residual risk, and decide where a human follow-up adds value.

## Review protocol

### 1. Establish current context

1. Retrieve the PR metadata, description, merge-base diff, commit history, files,
   checks, reviews, and all review threads at the current PR head.
2. Build a review-thread inventory that includes:
   - author/reviewer, including whether it is an automated reviewer
   - thread status: open, resolved, outdated, or superseded
   - changed lines and commit SHA
   - issue summary and any author response
3. Read the applicable repository guidance before evaluating the diff:
   - AGENTS.md
   - REVIEWING.md
   - CONTRIBUTING.md
   - path-specific guidance
   - relevant contracts, state docs, migration docs, and generated-code rules
4. Extract and read the Jira ticket when available. State unavailable context
   explicitly; do not infer missing requirements or production behavior.
5. Inspect nearby code, callers, interfaces, tests, generated types, and relevant
   execution paths. Use an isolated worktree if local checkout is required; do not
   alter a shared working tree.

Repository guidance is the review rubric. Apply it based on the PR’s actual change
types and risk areas. Do not separately report every documented-rule violation or
repeat generic checklist items.

### 2. Triage automated-review overlap first

Before creating any finding, compare it semantically with all existing review
threads, including resolved, outdated, and bot-authored threads.

Classify every potential concern as exactly one of:

- New: no existing thread identifies the same underlying issue.
- Existing bot thread - augment: the existing thread is directionally correct, but
  a reply would add material value through new evidence, a distinct affected path,
  corrected severity, a concrete Jira/contract implication, or a more actionable
  recommendation.
- Existing thread - no action: the issue is already adequately raised, even if
  this review found additional supporting detail.
- Resolved or superseded: later commits or discussion have addressed it.

Do not create a new finding for an existing bot or human thread. Do not draft a
reply merely to agree, restate the problem, repeat repository guidance, or add
minor context. If an author’s response appears to resolve a concern, verify it
against the current diff before treating it as resolved.

### 3. Review residual risk

Focus on issues caused or exposed by this PR that are likely worth a manager’s
or author’s time:

- correctness, data integrity, contracts, authorization, privacy, and security
- subscription state, billing, fulfillment, retries, duplicate delivery, replay,
  transaction, migration, and external-vendor safety when relevant
- Jira outcome and acceptance-criteria mismatches
- meaningful test gaps for changed behavior
- maintainability concerns only when they create a concrete maintenance cost or
  make the business flow materially harder to understand

For code simplification, follow REVIEWING.md: do not object to a helper only
because it has one caller. Raise it only when it does not name domain logic,
isolate meaningful complexity, improve testability, or match a local pattern,
and when inlining or a smaller change has a concrete benefit.

Do not report:
- formatting, lint, static-analysis, or generated-code issues covered by automation
- generic best practices without repository or behavioral evidence
- preference-only style feedback
- resolved, superseded, or adequately covered review feedback
- a finding merely to meet a target count

A reportable issue must be tied to a changed line or a specific missing test for
changed behavior, have a concrete consequence, and have enough confidence to
justify human attention.

### 4. Output

## A. Business and PR context
- Jira key, goal, acceptance criteria, and unavailable context
- PR title, author, branches, and concise implementation summary
- affected execution paths and applicable REVIEWING.md areas
- observed validation: passed / failed / not run / unknown
- risk: Low / Medium / High
- merge readiness: Ready / Ready with minor feedback / Needs changes / Needs clarification

## B. Existing-review triage
List only existing threads relevant to this review:

| Thread | Author/type | Status | Disposition | Why |
| --- | --- | --- | --- | --- |

Use the dispositions from the triage protocol. Include a proposed reply only for
`Existing bot thread - augment`.

## C. Review summary
Provide up to five bullets:
- what is sound
- the most important residual risk, if any
- whether automated feedback already covers the material concerns
- any required human sign-off or validation gap

State clearly when no material new issue was found.

## D. New findings and worthwhile bot-thread replies

Include only `New` findings and `Existing bot thread - augment` items.

For each item:
- Disposition: New / Existing bot thread - augment
- Severity: Critical / Major / Minor
- Type
- Confidence: High / Medium / Low
- Blocking: Yes / No / Needs discussion
- File and line range
- Issue
- Concrete failure scenario or maintenance cost
- Evidence
- Smallest recommendation
- Action:
  - New PR comment, or
  - Reply to existing thread: <thread link>
- Draft comment: `<clear, concise review comment in a professional yet casual style>`

For an existing-thread reply, state specifically what new information the reply
adds beyond the bot’s original comment.

## E. Manager narrative
Provide:
- a short opening summary
- blockers versus non-blockers
- questions that should be discussed rather than asserted
- a concise note on how to respond to any bot feedback that is valid but already
  sufficiently covered

Do not exceed five total items in section D unless there are more than five
independent Critical or Major issues.
