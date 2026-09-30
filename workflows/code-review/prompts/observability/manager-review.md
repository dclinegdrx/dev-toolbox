Please perform a code review of this pull request in GoodRx/observability: {clipboard}

Your goal is to help me, an engineering manager who codes part time, quickly understand:
* what this change is trying to do
* whether the Groundcover implementation matches the intended operational outcome
* what routing, alerting, dashboard, or migration risks are worth discussing
* which questions I should ask the author before approving

Use Glean Document Reader for the PR URL and any Jira / Confluence / GitHub URLs referenced in the PR.

Favor evidence-based questions over prescriptive rewrites. I am not looking for style nitpicks or “this must be done exactly this way” feedback unless something appears clearly risky or incorrect.

## Step 1: Gather context

1. Query GitHub for the PR details, including:
   * title
   * author
   * source branch
   * target branch
   * PR description
   * changed files
   * labels
   * linked issues, if present

2. Review the diff against:
   * main, or
   * the default branch if main does not exist

3. Determine what area of the observability repo this PR touches. Call that out explicitly:
   * terraform/monitors/<team>/
   * terraform/dashboards/
   * terraform/platform/
   * routing/
   * catalog/
   * apps/self-service
   * apps/incident-router-config
   * scripts/groundcover
   * other

4. Extract the Jira issue key from the PR title or description if present, then query Jira for:
   * summary/title
   * description
   * acceptance criteria, if available
   * relevant comments
   * any validation or rollout expectations

5. Use internal context to understand:
   * whether this is a migration PR, a validation/remediation PR, a routing PR, a dashboard PR, or a net-new Groundcover capability
   * what service, team, environment, or alert path is affected
   * whether this appears to change operational semantics, routing semantics, or only metadata / plumbing

If Jira data is unavailable, rely on the PR description, code changes, and repo context to infer intent.

## Step 2: Review the change with a Groundcover / observability lens

Review the PR with special attention to the Groundcover model used in GoodRx/observability.

### A. Repo contract and identity

Focus on:
* whether the change is being made in the correct part of the repo
* whether monitor identity looks stable, especially labels.iac_key
* whether title changes might accidentally imply a new monitor identity or create duplicate-title risk
* whether labels.service, labels.team, labels.env, and severity are present and plausible
* whether the PR preserves the idea that monitor definitions provide metadata, not direct Slack/PagerDuty destinations

Questions to consider:
* Is this changing the intended monitor, or accidentally creating a new one?
* Is any routing-relevant metadata changing without explanation?
* If a monitor moved teams, does the PR reflect a real ownership change or just a file move?

### B. Groundcover selector correctness

Focus on:
* whether the query is selecting the intended population in Groundcover
* whether the selector looks workload-centric, or whether it seems to be carrying over Datadog tag assumptions
* label key drift, such as workload vs workload_name vs kube_app_name
* workload names with environment suffixes
* case sensitivity in trace resource or gRPC method names
* whether the query likely returns real data for the intended service / env / cluster / resource

Questions to consider:
* What evidence shows this selector returns the right series in Groundcover?
* Is this selecting the real workload, or an old Datadog-style service label?
* Could this silently return zero series, the wrong workload population, or an overly broad population?

### C. Query math and threshold semantics

Focus on:
* counters that may need rate(...) or increase(...)
* histogram_quantile usage, bucket labels, and range selectors
* unit mismatches, especially milliseconds vs seconds
* impossible or suspicious threshold translations
* double-counting or sticky formulas caused by combining PromQL range functions with Groundcover rollups
* whether numerator and denominator both make sense for ratio-style monitors

Questions to consider:
* Does this formula measure a current symptom, or a cumulative counter value?
* If the query is translated from Datadog, is the semantic equivalent actually preserved?
* Does the threshold appear to be in the right unit?
* If this alert fired, would the value be interpretable by an on-call engineer?

### D. NoData, absence, and low-traffic behavior

Focus on:
* whether noDataState behavior matches the actual symptom
* whether “no traffic” or “no events” conditions evaluate to numeric zero rather than collapsing into NoData
* whether low-volume signals are being measured by event count vs series count
* whether missing telemetry is intentionally a page, or more likely a selector bug

Questions to consider:
* What happens when the system is healthy but quiet?
* What happens when the telemetry path breaks?
* Is this alert likely to go NoData for reasons unrelated to the symptom we care about?

### E. Routing, ownership, and operational response

Focus on:
* whether the labels support the intended routing outcome
* whether the PR changes service/team/env/severity in ways that might reroute alerts
* whether this needs catalog or routing changes in addition to monitor changes
* whether route-related changes are explained clearly enough for reviewers to assess blast radius
* whether the alert message, header, or description gives enough context for investigation

Questions to consider:
* If this monitor fires, who will actually receive it?
* Is that routing outcome intentional and obvious from the PR?
* Does the investigation path seem clear, or would responders need tribal knowledge?

### F. Migration and parity risk

If the PR appears to be part of the Datadog -> Groundcover migration or validation effort, focus on:
* whether this is a safe repair, an unsupported monitor, or a forced translation
* whether the author included validation evidence
* whether the PR explains if Groundcover was over-alerting, under-alerting, or mismatching Datadog
* whether this should be fixed, re-authored, deferred, or discussed with the owning service team
* whether a dashboard / monitor gap is being documented rather than hidden

Questions to consider:
* What evidence proves this is the right fix?
* Is this an actual repair, or just a best guess translation?
* If the signal cannot be proven in Groundcover, should this be a follow-up instead of a silent merge?

### G. Dashboards and visualization, if applicable

Focus on:
* whether the dashboard seems operationally useful
* whether key signals are easy to spot quickly
* whether missing metrics, unsupported widgets, or odd conversions are acknowledged
* whether the layout helps an on-call engineer move from symptom to investigation
* whether the dashboard appears too broad, too dense, or too hard to interpret

Questions to consider:
* Would this help someone triage a real incident quickly?
* Are the most important signals surfaced first?
* Is the PR transparent about any missing metrics or degraded parity?

### H. Testing and validation

Focus on:
* whether the PR shows how the author validated the change
* query screenshots, previews, before/after results, parity notes, route checks, or dashboard validation
* whether there is enough evidence to merge confidently
* whether a staged rollout, follow-up validation, or owner signoff is implied but missing

Questions to consider:
* What proof would make me comfortable approving this?
* Is the validation strong enough for the operational risk of the change?
* If validation is thin, what is the smallest clarifying question worth asking?

Do not nitpick formatting unless it affects readability, identity, or long-term maintainability.

Do not invent missing Jira, GitHub, routing, or Groundcover details. If something is unavailable, say so.

## Step 3: Produce the output in this exact structure

### A. Jira / business context

Provide:
* Jira key
* Jira summary
* concise description of the operational or business goal
* acceptance criteria summary, if available
* important context from Jira comments
* any mismatch between the Jira ticket and the PR

### B. PR overview

Provide:
* PR title, author, source branch, target branch
* concise summary of what this PR changes
* which part of GoodRx/observability it touches
* high-level explanation of the implementation approach
* main services, teams, routes, dashboards, or monitors affected
* overall risk assessment: Low / Medium / High
* merge-readiness assessment: Ready / Ready with minor feedback / Needs changes / Needs clarification

### C. High-level review summary

Provide:
* 3 to 7 bullets with the most important takeaways
* what looks solid
* top risks or open questions
* where the reviewer should ask for evidence vs where the reviewer can likely trust the implementation

### D. Findings, sorted by severity

Only include findings that are actionable and worth commenting on.

For each finding, use this format:

* Severity: Critical / Major / Minor / Nit
* Type: Bug / Query Semantics / Routing / Ownership / Coverage Gap / Noise / Maintainability / Testing / Readability / Security / Design
* Confidence: High / Medium / Low
* File: <path>
* Line: <line number or range if available>
* Issue: <one sentence summary>
* Why it matters: <plain-English explanation tied to Groundcover behavior, alerting, routing, or incident response>
* Suggested angle: <how I should frame this with the author, preferably as a question or request for evidence>
* Draft PR comment: <clear, respectful comment I could leave on the PR>

Severity guidance:
* Critical: likely broken monitor/routing behavior, likely missed incidents, likely false paging, or accidental destructive identity/routing change
* Major: important semantic risk, unproven migration fix, suspicious selector/math, or meaningful operational ambiguity before merge
* Minor: useful improvement, validation gap, or maintainability concern that may not block merge
* Nit: optional polish only

### E. Suggested manager narrative

Help me communicate this review effectively. Provide:
* a short opening summary I could say or write
* which findings are likely blockers vs non-blockers
* which findings should be framed as direct recommendations
* which findings should be framed as questions or discussion points

## Style guidance

* Write clearly for a technical manager who understands systems and observability, but is not deep in every Groundcover or PromQL detail
* Prefer concise, direct explanations over jargon
* Be specific and grounded in the actual diff
* If you are uncertain, state assumptions explicitly
* If the PR looks solid, say so clearly rather than forcing extra findings
* Prefer comments like “Can you help me understand why this selector uses X instead of Y?” over “This must use Y”
* Prefer “What evidence did you use to validate this threshold / query / routing change?” over prescriptive rewrites when multiple solutions may be valid

/jira