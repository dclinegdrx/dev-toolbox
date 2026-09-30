Please perform a code review of this Fastly infrastructure pull request: {clipboard}

Your goal is to help me, an engineering manager for the Conditions Subscriptions team, quickly understand the purpose of the change, the business context behind it, the Fastly/Terraform/VCL impact, and any issues worth raising with the author before this is applied or merged.

Review this as infrastructure code that can affect production routing, headers, caching, origin selection, tenant behavior, lifecycle environments, and observability. Be practical and risk-focused. Do not nitpick minor style unless it affects correctness, safety, maintainability, or GoodRx Fastly conventions.

## Step 1: Gather context

1. Query GitHub for the PR details, including:
   * title
   * author
   * source branch
   * target branch
   * PR description
   * changed files
   * labels
   * review status
   * PR comments, especially Atlantis output, Code Owner feedback, validation evidence, and requested apply commands
2. Check out the PR branch, or confirm it is already checked out and up to date.
3. Diff the PR branch against:
   * `master`, because `fastly-infrastructure` uses `master` as the default branch
   * if `master` does not exist locally, fetch it first rather than diffing against a stale branch
4. Extract the Jira issue key from the PR title if present, then query Jira for:
   * summary/title
   * description
   * acceptance criteria, if available
   * relevant comments
   * rollout, validation, or rollback requirements
5. Read the repo PR template and compare the PR body against it. Confirm whether the PR includes:
   * proof of testing
   * reviewer validation instructions
   * a Jira ticket in the title
   * client/browser or curl verification where relevant
   * `service_version_comment` update where relevant
   * Atlantis plan/apply workflow notes 
6. Identify the type of Fastly change:
   * redirect or rewrite
   * route/backend/origin selection
   * VCL snippet
   * header mutation
   * cache/pass/TTL behavior
   * dictionary or ACL change
   * tenant onboarding or tenant mapping
   * lifecycle environment behavior
   * logging or observability
   * TLS/domain/cert changes
   * module/provider/version changes
   * rollback or cleanup
7. Identify every affected service and environment:
   * domain folder, such as `www.goodrx.com`, `gold.goodrx.com`, `graph.goodrx.com`, `rxsmartsaver.com`, or another service
   * environment folder, such as `staging`, `prod`, `preprod`, `dev`, or `lifecycle`
   * Terraform workspace or Atlantis project name, if available
   * Fastly service name and domains from `main.tf` or `terraform.tfvars`
8. If the PR touches Conditions Subscriptions routes, auth routes, subscription IDs, follow-up routes, `/treatment`, `/care`, `/account`, `/gold`, or Next Web routing, look for related context in PR comments, Jira, Confluence, Slack, or recent similar PRs before reviewing behavior.
9. Do not invent missing Jira, GitHub, Atlantis, or Slack details. If information is unavailable, say so and explain how that limits confidence.

## Step 2: Review the code

Review the PR with focus on the following Fastly-specific dimensions.

### 1. Atlantis and Terraform safety

Check:
* The branch is current with `master` before any apply.
* The PR has an Atlantis plan for each affected environment.
* Non-production apply was run before production apply where applicable.
* The plan does not show unexpected creates, destroys, replacements, or broad resource churn.
* Any large VCL remove/re-add block is interpreted carefully, ideally by isolating the actual logical diff.
* The PR does not apply from an outdated branch, because internal guidance warns this can unintentionally delete resources. 
* State locks, stale locks, or failed plans are not ignored.
* Provider/module version changes are intentional and compatible with the repo.
* Sensitive values are not introduced in plain text, logs, PR descriptions, comments, or Terraform plans.

Raise concerns for:
* destructive plan output without explanation
* missing plan/apply evidence
* production apply before non-production validation
* broad changes outside the intended service/environment
* stale branch or merge-from-master side effects
* manual Fastly UI changes not reflected in Terraform

### 2. Environment parity and rollout sequence

Check:
* Changes are made in staging first when there is a matching staging environment.
* Matching prod changes are present after staging validation, unless the PR intentionally changes only one environment.
* Staging URLs and prod URLs are not mixed accidentally.
* Prod routes point to prod targets, except for explicitly documented internal/unauthorized-user behavior.
* Any staging/prod difference is intentional and explained.
* `service_version_comment` reflects the change and ticket when relevant.
* The PR does not assume every service has a lifecycle environment, since internal guidance notes not all Fastly services do. 

Raise concerns for:
* staging/prod drift
* copied staging URLs into prod
* prod-only change with no staging validation
* missing prod follow-through after staging-only change
* lifecycle expectations for services that do not support lifecycle

### 3. VCL snippet execution order

Check:
* Each changed snippet is attached to the correct VCL subroutine, such as `recv`, `hash`, `fetch`, `miss`, `pass`, `deliver`, `error`, or `log`.
* The priority is correct relative to nearby snippets in the same subroutine.
* Lower-priority snippets that run earlier do not shadow or undo later logic.
* Header, routing, cache, and redirect mutations happen before dependent logic needs them.
* `error` handling and custom status-code flows are intentional.
* If 7xx custom routing codes are used, the flow correctly sets the 7xx status, transfers to error handling, maps to the intended status, and returns. 
* Snippet file names match `script_name` references in Terraform. 

Raise concerns for:
* wrong subroutine
* wrong priority
* broad conditional logic before a more specific route
* missing fall-through/default handling
* response-header changes attempted before response context exists
* cache or pass behavior changed by ordering rather than explicit intent
* snippet registered in Terraform but missing or misnamed on disk

### 4. Routing, redirects, and backend/origin selection

Check:
* Host and path matching is precise.
* Regexes are anchored where needed.
* Query parameter handling is explicit.
* Redirects preserve, remove, or rewrite query parameters intentionally.
* Redirect targets use the right environment.
* Backend/origin selection matches the business goal.
* The change does not capture unrelated traffic.
* The change does not conflict with existing route dictionaries, CWF/Next Web routing dictionaries, or origin selection headers.
* For Next Web migrations, verify whether the intended route should move via a Fastly dictionary, VCL rule, origin swap, or application change. Internal migration notes show several page migrations are handled through Fastly dictionaries such as `content_web_conditions_routing`, `cwf_exclusions`, and related routing dictionaries. 

Raise concerns for:
* overly broad path match
* accidental mobile/desktop mismatch between `www`, `m`, and app-specific domains
* query parameter loss
* redirect loop
* wrong environment target
* route shadowing
* backend/origin mismatch
* conditions subscriptions deeplink behavior not validated end to end

### 5. Headers, identity, auth, tenant, and security behavior

Check:
* Request and response headers are modified in the correct VCL phase.
* Sensitive headers are not exposed to clients.
* Internal-only headers are not trusted from arbitrary clients unless explicitly protected.
* `X-GRX-Internal-User`, `X-GRX-Internal-Req`, `X-GRX-Tenant`, `X-Grx-Origin`, cookies, and auth-related headers are handled intentionally.
* Header changes do not bypass PerimeterX, WAF, tenant gating, auth, or origin ingress expectations.
* Tenant onboarding changes include domains, cert domains, redirects, tenant header mapping, and live-toggle behavior where applicable. 
* Tenant go-live toggles default safely, especially when public traffic should be blocked until launch. 
* Any external-facing route protects against spoofed internal headers or unintended access.

Raise concerns for:
* client-controlled header trusted as internal
* tenant header missing or wrong
* auth or secure-area behavior changed unintentionally
* sensitive response headers leaked
* IP allowlist or ACL behavior weakened
* public traffic enabled prematurely
* security-sensitive bypass without Security/Platform context

### 6. Caching, TTL, purge, and cache-key behavior

Check:
* Cache/pass behavior is intentional.
* TTL changes are appropriate for the content and origin.
* Query params, cookies, `Vary`, and custom cache-key normalization are consistent with the affected application.
* Personalized, auth, account, care, treatment, subscription, payment, or checkout content is not cached incorrectly.
* Cache behavior aligns with backend headers such as `Cache-Control`, `Surrogate-Control`, `Set-Cookie`, or GoodRx-specific Fastly TTL headers.
* Purge or surrogate-key behavior is considered when changing static assets, CWF/Next Web content, or route dictionaries.
* The PR explains how to validate cache behavior after apply.

Raise concerns for:
* caching personalized content
* removing required pass behavior
* cache-key changes that collapse distinct requests
* missing `Vary` for content that differs by header/cookie
* query params unexpectedly stripped or preserved
* no purge/rollback plan for cached bad behavior

### 7. Dictionaries, ACLs, and versionless resources

Check:
* Dictionary or ACL changes use the right `manage_items` or `manage_entries` behavior.
* PR changes do not overwrite resources that are intentionally managed outside Terraform.
* For dictionaries managed by lambdas or external processes, the PR does not incorrectly move ownership into Terraform.
* Versionless dictionary/ACL resources have backup/restore considerations. Fastly does not store versioned datasets for dictionary items or ACL entries, and GoodRx backs these up to the `fastly-backups` repo through a Codefresh job. 
* If lifecycle environments source dictionary data from production backups or snapshots, validate the lifecycle impact rather than assuming values exist only in this repo. 

Raise concerns for:
* Terraform trying to manage externally managed dictionary values
* accidental dictionary item deletion
* ACL entry drift
* missing restore plan
* lifecycle dictionary assumptions that do not match production-sourced data
* broad dictionary changes without representative URL validation

### 8. Domains, TLS, origins, and upstream connectivity

Check:
* Domains and certificate domains are complete and environment-correct.
* New tenant or subdomain additions include aliases and redirect targets.
* Origin address, override host, SNI hostname, certificate hostname, port, `use_ssl`, and `ssl_check_cert` are consistent.
* Shield, timeout, `max_conn`, health, and load-balancing settings are not changed accidentally.
* Ingress expectations in downstream services still match the headers and origin paths Fastly sends.
* New origin or route changes include validation that the origin responds as expected.

Raise concerns for:
* certificate domain missing wildcard or alias
* wrong `override_host`
* SNI/cert mismatch
* no TLS validation
* sending public traffic to a private or lifecycle origin
* changing origin timeouts without explaining reliability impact

### 9. Observability and logging

Check:
* Fastly logs, Datadog logs, BigQuery logs, S3 logs, Groundcover, or other configured logging are not broken or silently disabled.
* Log format names, table names, bucket paths, service names, and environment tags remain correct.
* The PR considers how reviewers or on-call engineers will detect 4xx/5xx spikes, routing issues, origin errors, or cache regressions.
* For production-impacting changes, validation includes representative logs, metrics, dashboards, or curl output.
* If logging is intentionally changed, cost and visibility tradeoffs are stated.

Raise concerns for:
* logging removed without replacement
* prod/no-prod logging mismatch not explained
* table/bucket/service names wrong
* no observable signal for rollback decision
* high-cardinality or sensitive data added to logs

### 10. Validation evidence and reviewer reproducibility

Check:
* The PR provides concrete verification steps, ideally curl commands that reviewers can copy.
* Validation covers every changed environment.
* Validation covers success, redirect, unauthorized, and negative cases when relevant.
* The author tested after non-production apply.
* For production-impacting changes, the PR states what should be checked immediately after deploy.
* Fastly Fiddle or another VCL-specific validation tool is used when helpful for complex snippets. 
* The PR does not rely only on “looks good locally” for edge behavior.

Raise concerns for:
* missing curl commands
* screenshots without enough detail
* validation before apply but not after apply
* no negative test
* no production post-apply check
* validation that does not exercise the changed route/header/cache behavior

### 11. Rollback and operational readiness

Check:
* The rollback path is explicit.
* The rollback uses a revert PR when appropriate, since Atlantis has no native rollback. 
* The PR identifies whether rollback is a Terraform revert, Fastly service-version activation, dictionary restore, DNS/weighted record change, or coordinated application rollback.
* Any follow-up cleanup needed after rollback is called out.
* For high-risk routing changes, there is a plan for who watches metrics and who can execute rollback.
* The rollback plan is fast enough for the blast radius.

Raise concerns for:
* “revert if needed” with no detail
* rollback depends on unavailable owners
* dictionary/ACL restore not considered
* no post-deploy monitoring window
* unclear rollback for already-applied production changes

## Step 3: Produce the output in this exact structure

### A. Jira / business context

Provide:
* Jira key
* Jira summary
* concise description of the business goal
* acceptance criteria summary, if available
* important context from Jira comments
* related Slack/Confluence/GitHub context, if found
* any mismatch between the Jira ticket and the PR
* any unclear ownership or reviewer alignment issue

### B. PR overview

Provide:
* PR title, author, source branch, target branch
* concise summary of what this PR changes
* affected Fastly services, domains, and environments
* type of change: redirect/routing/VCL/header/cache/dictionary/ACL/tenant/lifecycle/logging/TLS/origin/module
* high-level implementation approach
* main files or modules affected
* Atlantis plan/apply status by environment, if available
* validation evidence provided by the author
* rollback approach, if provided
* overall risk assessment: Low / Medium / High
* merge-readiness assessment: Ready / Ready with minor feedback / Needs changes / Needs clarification

### C. High-level review summary

Provide:
* 3 to 7 bullets summarizing the most important review takeaways
* what looks good
* top risks or concerns
* whether the PR appears safe to apply to non-production
* whether the PR appears safe to apply to production
* whether approval should wait for Code Owner, Platform, Security, DevOps, or app-team input

### D. Fastly-specific review checklist

Provide a concise checklist with Pass / Concern / Unknown for each relevant category:

| Category | Status | Notes |
| --- | --- | --- |
| Jira / business goal alignment | Pass / Concern / Unknown |  |
| PR template completeness | Pass / Concern / Unknown |  |
| Atlantis plan/apply safety | Pass / Concern / Unknown |  |
| Environment parity | Pass / Concern / Unknown |  |
| VCL subroutine and priority | Pass / Concern / Unknown |  |
| Routing / redirects / backend selection | Pass / Concern / Unknown |  |
| Headers / auth / tenant / security | Pass / Concern / Unknown |  |
| Cache / TTL / cache key | Pass / Concern / Unknown |  |
| Dictionaries / ACLs | Pass / Concern / Unknown |  |
| Domains / TLS / origins | Pass / Concern / Unknown |  |
| Observability / logging | Pass / Concern / Unknown |  |
| Validation evidence | Pass / Concern / Unknown |  |
| Rollback readiness | Pass / Concern / Unknown |  |

Only include categories that are relevant to the PR. If a category is not relevant, omit it rather than filling with noise.

### E. Findings, sorted by severity

Only include findings that are actionable and worth commenting on.

For each finding, use this format:

* Severity: Critical / Major / Minor / Nit
* Type: Bug / Edge Case / Maintainability / Performance / Testing / Readability / Security / Design / Infra Safety / Rollback / Observability
* Confidence: High / Medium / Low
* File: `<path>`
* Line: `<line number or line range>`
* Issue: `<one sentence summary>`
* Why it matters: `<plain-English explanation>`
* Recommendation: `<specific change or follow-up>`
* Draft PR comment: `<clear, respectful comment I could leave on the PR>`

Use severity guidance:
* Critical: likely production outage, security issue, data exposure, cache poisoning, broad traffic misrouting, destructive Terraform change, or breaking behavior
* Major: important correctness, reliability, maintainability, routing, rollout, validation, or rollback concern that should likely be addressed before production apply or merge
* Minor: useful improvement, edge case, missing validation detail, or test gap that may not block merge
* Nit: optional polish only

### F. Apply / merge recommendation

Provide:
* Non-production apply recommendation: Safe / Safe after comments / Do not apply yet / Unknown
* Production apply recommendation: Safe / Safe after comments / Do not apply yet / Unknown
* Merge recommendation: Ready / Ready with minor feedback / Needs changes / Needs clarification
* Required before production apply
* Required before merge
* Suggested but non-blocking follow-ups

### G. Suggested manager narrative

Help me communicate this review effectively to my team member. Provide:
* a short opening summary I could say or write
* which findings are likely blockers vs non-blockers
* which findings should be framed as direct recommendations
* which findings should be framed as questions or discussion points
* whether I should pull in Platform Engineering, DevOps, Security, Code Owners, or another app team

## Style guidance

* Write clearly for a technical manager who understands software engineering and GoodRx systems but may not be the deepest Fastly/VCL expert.
* Prefer concise, direct explanations over jargon.
* Be specific and grounded in the actual diff, PR comments, Jira ticket, and Atlantis output.
* Do not invent missing context. If Jira, Atlantis, or validation evidence is unavailable, say so.
* If the PR looks solid, say so clearly rather than forcing extra findings.
* Do not nitpick formatting unless it affects safety, maintainability, or GoodRx Fastly conventions.
* Prioritize production safety, routing correctness, validation quality, observability, and rollback readiness.
* When uncertain, state the assumption and the consequence if the assumption is wrong.

## Extra instructions for AI coding tools

Before making claims about behavior:
* Read the actual changed files.
* Compare nearby existing Fastly patterns in the same service/environment.
* Compare staging and prod versions when both exist.
* Inspect Atlantis output or PR comments if available.
* Search the repo for similar route, header, dictionary, or snippet names.
* Do not rely on generic Fastly knowledge when GoodRx repo conventions show a specific pattern.
* Do not suggest applying, merging, or approving unless the PR has enough evidence to support that recommendation.

/jira