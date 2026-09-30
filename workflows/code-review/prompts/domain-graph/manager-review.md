Please perform a code review of this pull request: {clipboard}

Your goal is to help me, an engineering manager for the Conditions Subscriptions team, quickly understand the purpose of the change, the business context, the technical impact on the GraphQL platform, and any issues that are worth raising with the author. Domain-graph is a high-traffic, multi-tenant repository used by web (Singularity / next-web), iOS, and Android, and it sits behind `gql-stitch` (which unifies `domain-graph`, `apiv4-graph`, and `graphql-contentful`). The bar for schema design and review is intentionally high, so calibrate your feedback accordingly.

## Context: what domain-graph is and how it's structured

Use this background to ground your review. Do not restate it in your output unless relevant to a finding.

- **Repo**: `GoodRx/domain-graph` ([github.com/GoodRx/domain-graph](https://github.com/GoodRx/domain-graph)). TypeScript, Node 20, pnpm, Apollo Server 4, Awilix for DI.
- **Identity**: Domain Graph is "GraphQL done right" at GoodRx, a Domain Driven Design implementation that models business concepts (not upstream APIs or DB schemas) as a continuous, connected graph. It is the preferred place for new GraphQL development. Owner: APDI (Application Platform Domain Integration).
- **Stitcher topology**: Clients call `gql-stitch`, which proxies to `domain-graph`, `apiv4-graph`, and `graphql-contentful`. Schema changes in domain-graph can break the stitched schema if types collide.
- **Layered code structure** (4 layers, in this order):
  - Schema: `src/Interfaces/HttpApi/GraphQL/Modules/<Domain>/Schema/...`
  - Resolver: `src/Interfaces/HttpApi/GraphQL/Modules/<Domain>/Resolvers/...`
  - Service (app logic): `src/Application/Services/<Domain>/...`
  - API Client (gRPC or REST adapter): `src/Application/ApiClients/<Service>/...`
  - DI registration: `src/Application/DependencyManagement/getContainer.ts` and resolver registration: `src/getResolvers.ts`
  - Generated types live in `src/Interfaces/HttpApi/GraphQL/types.ts`; combined schema in `src/Interfaces/HttpApi/GraphQL/schema.graphql` (regenerated via `pnpm graphql:update`).
- **Key in-repo references for standards** (cite these in feedback when relevant):
  - `docs/mutations.md` — mutation naming, payload, input, userErrors, error mapping conventions.
  - `docs/endorsed-review-comments.md` — pre-written reviewer comments for the most common issues.
  - `docs/logging.md` — structured logging conventions (no string interpolation; structured fields).
  - GraphQL Style Guide (Confluence): nullability, naming, mutations, errors, connections.
  - Pagination guide (list fields): connection/edges/nodes pattern with `connectionFromLimitOffsetApi`, `connectionFromPageTokenApi`, and `connectionFromEdges/NodesArray` helpers.
- **Review process**: PRs flow through team review → Readability reviewers (CODEOWNERS-driven from `codeOwnership.ts`) → GraphQL Champions when the `ready-for-gql-champion-review` label is applied. Schema changes typically require Champion approval.
- **Deployment**: Lifecycle (LC) is configured in `lifecycle.yml` (key services: `domain-graph`, `gql-stitch`, optionally `next-web` and downstream services). Releases are gated on whether real app code changed.

## Step 1: Gather context

1. Query GitHub for PR details:
   - title, author, source branch, target branch, PR description, and the full list of changed files
   - check if the `ready-for-gql-champion-review` label is set, and which CODEOWNERS teams are required
2. Check out the PR branch locally (or confirm it is already checked out and up to date).
3. Diff the PR branch against `main` (fall back to `master` if `main` does not exist).
4. Categorize the changed files into the 4 layers above (Schema / Resolver / Service / ApiClient) plus DI, tests, and `lifecycle.yml`. This map should drive the review structure.
5. Run `pnpm graphql:update` mentally: if the PR touched any `.ts` schema file under `Modules/.../Schema`, confirm `types.ts` and `schema.graphql` were regenerated and committed.
6. Extract the Jira issue key from the PR title (typical formats: `[COND-1234]`, `[APDI-1234]`, `[GOLD-1234]`, etc.) and query Jira for:
   - summary/title
   - description and the linked product/technical requirements doc
   - acceptance criteria
   - relevant comments
7. If the PR description references an upstream service repo (for example `subscriptions`, `telehealth`, `drug-platform`, `pricing-gateway`, `payments`, `accounts-api`, `api-specs`), look at those linked PRs to confirm contract alignment.
8. Use the Jira information to understand the intended business outcome and expected behavior.

## Step 2: Review the code with a domain-graph lens

Apply these review lenses, in roughly this order. Skip any that don't apply.

### A. Schema design (highest scrutiny)

This is the most important lens for domain-graph. Schema is a long-lived public contract used across web, iOS, and Android.

- **Names model the business domain, not the upstream API or DB**. Flag fields named after gRPC methods, proto fields, or DB columns.
- **Mutations**: `verbEntity` (e.g., `createIssue`, `restartCanceledConditionSubscription`) — not `entityVerb` or `productCreate`.
- **Mutation shape** (per `docs/mutations.md`):
  - Single non-null `input: <MutationName>Input!` argument; nullable `<MutationName>Payload` return.
  - `Input`, `Payload`, and `Error` union are 1:1 with the mutation and prefixed with the mutation name. Do not reuse input/payload types across mutations.
  - Payload exposes `userErrors: [<MutationName>Error!]!` (preferred) or `success: Boolean!` (legacy only).
  - Each member of the `userErrors` union must implement the `UserError` interface (`message: String!`, `path: [String!]`).
  - Payload returns the modified entity (created/updated/deleted item, or closest parent with an `id`).
  - `userErrors` are for user-actionable / user-surfaceable problems. Truly internal failures should bubble up as top-level GraphQL errors. Queries should generally not use `userErrors` — model error states with a result `union` instead.
- **Pagination**: list fields must use the connection pattern (`<Parent><Entity>Connection`, `edges`, `nodes`, `pageInfo`). Calls should use the appropriate helper (`connectionFromPageTokenApi`, `connectionFromLimitOffsetApi`, or `connectionFromEdges/NodesArray`) based on the upstream API. Flag raw arrays for non-trivial lists.
- **Nullability**: prefer nullable. Flag `!` on fields that are not strictly always present, especially on new mutation inputs and entity fields. Going from nullable → non-null later is easy; the reverse is a breaking change.
- **No empty strings to mean "absence"**: prefer `null` over `""` on string fields.
- **Schema descriptions**: every new type, field, input, and arg should have a clear description (now important for AI consumers as well).
- **Backward compatibility**: any removal, rename, or `!`-tightening of an existing field is a breaking change. Confirm the field was deprecated for ≥ 7 days using `@deprecated(reason: "...")` and is no longer in use by clients (Apollo schema checks). Mobile rollouts are slow, so even non-breaking schema changes should consider a migration window when older app versions are still in the wild.
- **Stitcher impact**: watch for new top-level types or extensions that might collide with `apiv4-graph` or `graphql-contentful` types and break the stitched schema.
- **Type reuse**: prefer extending or reusing existing domain types (`DrugInstance`, `Viewer`, `MembershipSubscription`, `ConditionSubscription`, `PrescriptionFillOrder`, etc.) over duplicating shape.
- **Domain placement**: confirm the new fields/mutations live in the right `Modules/<Domain>` folder. Cross-cutting changes warrant a comment about ownership.

### B. Resolvers

- **Naming**: `<FieldName>Resolver` or `<ParentType><FieldName>Resolver` (e.g., `PharmacyStorePharmacistsOnStaffResolver`, `RestartCanceledConditionSubscriptionResolver`).
- **Thin pass-throughs**: resolvers should call into a Service method. Business logic in resolvers is a smell — flag it.
- **Chain resolution**: for fields on parent types (e.g., a field on `PharmacyStore` chained via `parent.id`), confirm a corresponding `<Entity>From<Entity>Resolver` exists for chain resolution from arbitrary entry points (see `DrugFromDrugResolver` for the pattern).
- **Registration**: every new resolver must be registered in both `src/Application/DependencyManagement/getContainer.ts` (DI) and `src/getResolvers.ts` (Apollo wiring). Missing either is a runtime failure.
- **Authentication**: confirm authenticated-only fields are correctly gated and that the `viewer` is used appropriately for user-scoped data.

### C. Services and ApiClients

- **Service (`Application/Services`)**: orchestrates one or more API clients, maps upstream domain shapes to the domain types we expose, translates upstream error codes (`grxerrors`) into typed `userErrors`. Each mutation should have its own pure error-mapping helper.
- **ApiClient (`Application/ApiClients`)**: thin gRPC/REST adapter. Should reflect the upstream contract accurately (especially when types come from `api-specs` generated definitions). Avoid leaking upstream types past the Service boundary.
- **DataLoader**: required (per the Reviewer Resource Doc) when an ApiClient method is used to resolve multiple/different fields, the same field in different places, or to chain-resolve an object type. Flag missing DataLoader where batching/dedup would matter.
- **Method naming**: `find*` (may return null) vs `get*` (asserts existence) should be used consistently in services.
- **Error handling**: do not double-log the same error (the ApiClient already logs upstream failures — don't relog at the Service layer). Map known `grxerror` codes to specific `UserError` union members; let unmapped errors bubble to top-level GraphQL errors.
- **DI lifetime**: confirm the new service/api client is registered with the right scope (scoped vs singleton) in `getContainer.ts`. Singletons holding request-scoped state are a real bug.

### D. Logging, observability, and operational impact

- Per `docs/logging.md`, prefer structured fields over interpolated strings: `log.debug('Restarting subscription', { subscriptionId })` not `log.debug(\`Restarting ${subscriptionId}\`)`.
- New code paths that touch upstream services should produce traceable spans. If the change adds a new gRPC call, confirm it inherits `dd-trace` instrumentation.
- Be alert to changes that materially shift call volume to upstream services (especially `pgw-app`, `phm-core`, `subscriptions`, `telehealth`, `drug-platform`). Comment if the PR could meaningfully affect monitor thresholds.

### E. Testing

- **Unit tests**: every new Service method, ApiClient method, and resolver should have a unit test. Look for `*.unit.test.ts` siblings.
- **Integration tests**: new mutations should usually have a matching `*.integration.test.ts` under `Modules/<Domain>/IntegrationTests/`, exercising the resolver end-to-end with mocked services. Cite a peer mutation's integration test as a reference if missing.
- **E2E**: significant client-facing changes may need an e2e test update; flag if appropriate.
- **CI signal**: note any failing checks (`Task:Tests`, `Typecheck`, `Lint`, `Schema Checks`). Schema check failures are usually the most important — they indicate a breaking change for at least one client operation.

### F. Lifecycle and configuration

- If `lifecycle.yml` was modified, confirm any newly added `optional` services are correct and that env vars are wired.
- Feature flags: confirm new behavior is gated appropriately, with cleanup tickets for the flag's eventual removal.

### G. Cross-team and downstream impact

- Identify client teams likely affected (web in `singularity` / `next-web`, iOS, Android, internal Patient Advocate tooling). Consumers of changed/removed fields should be coordinated with.
- If the change touches `viewer.*`, `Drug*`, `PrescriptionFillOrder`, `MembershipSubscription`, `ConditionSubscription`, `PricingOption`, or any pricing/coupon path, raise extra scrutiny — these are heavily shared.
- For changes coordinating with an `api-specs` PR or an upstream service PR (e.g., `subscriptions`, `telehealth`), confirm both are merged in the right order and that the gRPC contract version domain-graph compiles against actually exposes the new method.

Do not nitpick minor style issues unless they affect correctness, maintainability, schema clarity, or team standards in a meaningful way. Do not invent missing Jira/GitHub details — if information is unavailable, say so.

## Step 3: Produce the output in this exact structure

### A. Jira / business context
- Jira key
- Jira summary
- Concise description of the business goal (and which condition / product surface this affects, if relevant)
- Acceptance criteria summary, if available
- Important context from Jira comments or linked PRD/RFC
- Any mismatch between the Jira ticket and the PR

### B. PR overview
- PR title, author, source branch, target branch
- Concise summary of what this PR changes
- High-level explanation of the implementation approach
- Layer map: Schema / Resolver / Service / ApiClient / DI / Tests / Lifecycle — list which layers were touched and the main files in each
- Upstream services or coordinated repos involved (e.g., `api-specs`, `subscriptions`, `telehealth`, `singularity`)
- Schema impact: New / Additive / Deprecation / Breaking, with a one-line justification
- Overall risk assessment: Low / Medium / High
- Merge-readiness: Ready / Ready with minor feedback / Needs changes / Needs clarification
- Required reviewer groups (team, readability group, GraphQL Champions)

### C. High-level review summary
- 3 to 7 bullets summarizing the most important review takeaways
- Call out what looks good (schema modeling, test coverage, layering, etc.)
- Call out the top risks or concerns (breaking change, missing DataLoader, missing integration test, mutation convention deviation, etc.)

### D. Findings, sorted by severity

Only include findings that are actionable and worth commenting on.

For each finding, use this format:

- Severity: Critical / Major / Minor / Nit
- Type: Schema Design / Mutation Convention / Pagination / Nullability / Resolver / Service / ApiClient / DI / DataLoader / Logging / Testing / Backward Compatibility / Stitcher Impact / Cross-team Impact / Bug / Performance / Security / Readability
- Confidence: High / Medium / Low
- File: <path>
- Line: <line number or line range>
- Issue: <one sentence summary>
- Why it matters: <plain-English explanation, grounded in domain-graph standards or downstream impact>
- Recommendation: <specific change or follow-up; cite the relevant doc — `docs/mutations.md`, GraphQL Style Guide, Pagination guide, etc. — when applicable>
- Draft PR comment: <clear, respectful comment I could leave on the PR; mirror the tone of the endorsed review comments in `docs/endorsed-review-comments.md` when one applies>

Severity guidance:
- **Critical**: production bug, security/PII issue, data integrity problem, breaking schema change without deprecation, missing DI registration that will fail at runtime, stitcher schema collision.
- **Major**: mutation convention violation likely to require a follow-up breaking change, missing `userErrors` / wrong payload shape, missing pagination connection, missing DataLoader where it materially matters, missing integration test for a new mutation, double-logging or interpolated logs that will degrade debuggability, business-logic in resolver instead of service.
- **Minor**: nullability that should be reconsidered, missing schema description, naming nit on a resolver/service, test coverage gap on an edge case, deprecated field not annotated with `@deprecated`.
- **Nit**: optional polish only.

### E. Suggested manager narrative

Help me communicate this review effectively to my team member. Provide:
- A short opening summary I could say or write (acknowledging what landed well)
- Which findings are likely blockers vs non-blockers, called out by severity
- Which findings should be framed as direct recommendations
- Which findings should be framed as questions or discussion points (especially anything where intent is ambiguous or coordinated work in `api-specs` / upstream services is in flight)
- A note on review path: whether this PR is likely to need GraphQL Champion approval (any non-trivial schema change usually does) and any other groups to loop in

### F. Schema and contract impact summary (only if the PR touches schema)

A short standalone section for me to skim:
- Net schema delta (added types/fields, deprecated fields, removed fields)
- Breaking-change verdict and reasoning
- Client surfaces likely affected (web / iOS / Android / internal tools)
- Any required follow-up tickets (e.g., field deprecation cleanup, mobile migration window, schema doc updates)

## Style guidance
- Write clearly for a technical engineering manager who understands GraphQL, gRPC, and TypeScript but is not the deepest expert in every domain in the graph.
- Prefer concise, direct explanations over jargon. When invoking a convention, name the doc and link the rule (e.g., "per `docs/mutations.md` §4 the union members must implement `UserError`").
- Be specific and grounded in the actual diff — quote field names, file paths, and line numbers.
- If you are uncertain, say what assumption you are making (e.g., "assuming the upstream `RestartCanceledSubscription` gRPC method already exists in the deployed `subscriptions` service").
- If the PR looks solid, say so clearly rather than forcing extra findings.

/jira