Please perform a code review of this pull request: {clipboard}.

Your goal is to help me, an engineering manager, quickly understand the purpose of the change, the business context behind it, the user or operational impact, and any issues that are worth raising with the author.

This prompt is tuned for Retool PRs in the `GoodRx/retool-src-ctrl` repo, where changes often span app layout files, query wiring, JS helpers, Retool-generated metadata, gRPC/REST resources, and UI behavior.

## Step 1: Gather context
1. Query GitHub for the PR details, including:
   - title
   - author
   - source branch
   - target branch
   - PR description
   - changed files
   - review comments and unresolved discussion, if available
2. Check out the PR branch, or confirm it is already checked out and up to date.
3. Diff the PR branch against:
   - main, or
   - master if main does not exist
4. Extract the Jira issue key from the PR title or PR description if present, then query Jira for:
   - summary/title
   - description
   - acceptance criteria, if available
   - relevant comments
5. Use the Jira information to understand the intended business outcome, expected user workflow, and any operational constraints.
6. Inspect the changed Retool assets and classify the change into one or more buckets:
   - UI/layout only
   - query wiring / event flow
   - JS transformer / helper logic
   - data fetching / API contract changes
   - resource or auth configuration
   - generated Retool churn / schema migration
7. If the PR includes a Retool preview URL, note it. Use it as context if available, but do not invent observations you cannot verify from the diff or PR text.

## Step 2: Review the code
Review the PR with focus on:

### A. Behavior and correctness
- does the UI do what the Jira ticket intends
- are button states, visibility conditions, and destructive actions correct
- does the change behave correctly for the currently selected row, record, or modal state
- are Retool queries triggered at the right time and from the right event source
- could the implementation use stale state, previous selections, or incomplete async state

### B. Retool-specific workflow risks
- duplicate query triggers
- missing trigger paths
- race conditions between table selection, query success handlers, and downstream derived state
- queries depending on `selectedRow`, temporary state, or derived values that may not yet be ready
- modals, drawers, tabs, or details panels showing stale data after actions complete
- success/failure toasters not matching actual backend outcomes
- missing refreshes or partial refreshes after mutations
- destructive actions that are visually exposed but not safely gated

### C. Data and API integrity
- request payload correctness
- null/undefined handling
- assumptions about field presence or shape
- proto / REST request correctness
- resource version mismatches
- whether the PR hardcodes business rules that should come from backend APIs instead
- whether frontend logic is compensating for missing server fields in a fragile way

### D. UX and operational safety
- dangerous actions clearly signposted
- confirmation flows appropriate for cancel / delete / edit actions
- disabled states and eligibility logic correct
- wording, labels, and warnings clear enough for internal operators
- error states actionable for the human using the tool
- loading states prevent stale or misleading UI

### E. Maintainability
- is the logic understandable in a Retool context
- are JS queries / transformers readable and scoped
- is business logic placed in the least fragile location
- is repeated logic duplicated across widgets or queries
- are file changes easy to reason about despite Retool-generated noise
- should generated churn be separated from behavioral changes

### F. Testing and verification
- does the PR include a credible test plan
- were meaningful flows actually validated, versus only checking wiring in the editor
- are edge cases called out
- are there important manual tests missing for stateful or destructive flows
- for config/resource PRs, is there enough evidence the change is safe across environments

Do not nitpick minor style issues unless they affect correctness, maintainability, reviewability, or team standards in a meaningful way.

Do not invent missing Jira, GitHub, or Retool details. If information is unavailable, say so.

## Step 3: Produce the output in this exact structure

### A. Jira / business context
Provide:
- Jira key
- Jira summary
- concise description of the business goal
- acceptance criteria summary, if available
- important context from Jira comments
- any mismatch between the Jira ticket and the PR

### B. PR overview
Provide:
- PR title, author, source branch, target branch
- concise summary of what this PR changes
- high-level explanation of the implementation approach
- main apps, modules, queries, or resources affected
- whether this is primarily:
  - UI/layout
  - query wiring
  - JS logic
  - resource/config
  - mixed
- overall risk assessment: Low / Medium / High
- merge-readiness assessment: Ready / Ready with minor feedback / Needs changes / Needs clarification

### C. High-level review summary
Provide:
- 3 to 7 bullets summarizing the most important review takeaways
- call out what looks good
- call out the top risks or concerns
- explicitly note whether the diff contains meaningful logic changes, generated Retool churn, or both

### D. Findings, sorted by severity
Only include findings that are actionable and worth commenting on.

For each finding, use this format:

- Severity: Critical / Major / Minor / Nit
- Type: Bug / Edge Case / Maintainability / Performance / Testing / Readability / Security / Design / UX / Data Flow / Retool Wiring / Config
- Confidence: High / Medium / Low
- File: &lt;path&gt;
- Line: &lt;line number or line range&gt;
- Issue: &lt;one sentence summary&gt;
- Why it matters: &lt;plain-English explanation&gt;
- Recommendation: &lt;specific change or follow-up&gt;
- Draft PR comment: &lt;clear, respectful comment I could leave on the PR&gt;

Use Severity guidance:
- Critical: likely production bug, dangerous destructive behavior, security issue, wrong record mutation, broken operational workflow, or environment/config issue that could cause outages or bad writes
- Major: important correctness, reliability, UX safety, data-flow, or maintainability concern that should likely be addressed before merge
- Minor: useful improvement, edge case, test gap, or review concern that may not need to block merge
- Nit: optional polish only

### E. Retool-specific checklist
Provide a short checklist with Pass / Concern / Not applicable for each:
- selection state correctness
- query trigger timing
- duplicate query execution risk
- stale data / refresh behavior after mutation
- null / undefined handling
- destructive action gating
- success and failure notifications
- preview / manual verification coverage
- generated diff separated from meaningful logic
- resource / environment safety

### F. Suggested manager narrative
Help me communicate this review effectively to my team member. Provide:
- a short opening summary I could say or write
- which findings are likely blockers vs non-blockers
- which findings should be framed as direct recommendations
- which findings should be framed as questions or discussion points

## Extra review heuristics for Retool PRs
Apply these heuristics when relevant:

1. Be suspicious of logic that depends on `selectedRow`, modal state, or derived temp state during async transitions.
2. Prefer backend-provided truth over duplicated frontend eligibility logic when available.
3. Watch for duplicate triggers, especially when one query is fired both from a search flow and a component event.
4. Confirm that success handlers refresh the right widgets and clear any transient form state.
5. Treat destructive actions as high-risk even if the code diff is small.
6. If a PR mixes generated Retool changes with behavioral edits, separate the two in your explanation and findings.
7. For resource/config PRs, look for environment assumptions, token expiry assumptions, auth caching behavior, and cross-env safety.
8. For layout-only PRs, review whether the visual change could still affect usability, discoverability, or operator mistakes.
9. Call out when the author’s test plan is too shallow for a stateful UI change.
10. If the PR looks solid, say so clearly rather than forcing extra findings.

## Style guidance
- Write clearly for a technical manager who understands software engineering but is not the deepest expert in every Retool implementation detail.
- Prefer concise, direct explanations over jargon.
- Be specific and grounded in the actual diff.
- Pay special attention to data flow, query wiring, state synchronization, and operational safety.
- If you are uncertain, say what assumption you are making.
- If generated Retool noise makes the diff harder to review, say that explicitly.
- If the PR looks solid, say so clearly rather than forcing extra findings.

/jira