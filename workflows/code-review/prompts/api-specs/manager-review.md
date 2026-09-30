Please perform a code review of this pull request: {clipboard}.

Your goal is to help me, an engineering manager, quickly understand the purpose of the change, the business context behind it, the impact on API consumers, and any issues worth raising with the author.

## Step 1: Gather context

1.  Query GitHub for the PR details, including:
    *   title
    *   author
    *   source branch
    *   target branch
    *   PR description
    *   changed files
2.  Check out the PR branch, or confirm it is already checked out and up to date.
3.  Diff the PR branch against:
    *   main, or
    *   master if main does not exist
4.  Extract the Jira issue key from the PR title if present, then query Jira for:
    *   summary/title
    *   description
    *   acceptance criteria, if available
    *   relevant comments
5.  Use the Jira information to understand:
    *   what product capability or workflow is being enabled or changed
    *   which clients or services depend on this API (web, mobile, backend services, partners)
    *   expected request/response behavior after the change

If Jira data is unavailable, infer intent from the PR description and spec changes.

## Step 2: Review the API specification changes

Review the PR with a contract-first API lens. Focus on:

### Correctness and clarity

*   accuracy of request/response schemas
*   required vs optional fields
*   data types and constraints (enums, formats, validation rules)
*   consistency between documentation and schema definitions
*   clarity of field names and descriptions

### Backward compatibility

*   breaking changes (removed fields, renamed fields, type changes, required field additions)
*   behavior changes that could impact existing clients
*   versioning strategy (new version vs in-place change)
*   deprecation strategy for fields or endpoints
*   safe evolution patterns (additive changes vs destructive)

### API design quality

*   consistency with existing API patterns in the repo
*   naming conventions (fields, endpoints, RPCs, GraphQL types)
*   resource modeling and hierarchy (REST)
*   RPC method semantics (gRPC)
*   schema design and type reuse (GraphQL and shared models)
*   pagination, filtering, and sorting patterns where applicable

### Consumer experience

*   ease of use for clients
*   predictability and consistency across APIs
*   error handling structure and clarity
*   presence of helpful descriptions and examples
*   avoidance of ambiguous or overloaded fields

### Validation and constraints

*   appropriate validation rules (min/max, formats, enums)
*   nullability and default values
*   handling of partial or invalid input

### Error handling and status modeling

*   standardization of error responses (REST, GraphQL errors, gRPC status codes)
*   meaningful error codes and messages
*   mapping between business errors and transport-level errors

### Documentation quality

*   completeness of descriptions for endpoints, fields, and types
*   examples for requests and responses
*   clarity of edge cases and special behaviors
*   consistency between spec and any inline documentation

### Consistency across protocols

*   alignment between REST, gRPC, and GraphQL equivalents if applicable
*   consistent naming and field semantics across different API styles
*   shared models reused where appropriate

### Security and access considerations

*   exposure of sensitive fields
*   authentication/authorization expectations (if defined in spec)
*   proper marking of internal vs public APIs

### Testing and validation

*   presence of schema validation (linting, CI checks, codegen compatibility)
*   risk of breaking downstream code generation
*   missing test cases or validation scenarios (if applicable to repo setup)

Do not nitpick formatting unless it impacts readability, consistency, or long-term maintainability.

Do not invent missing Jira or GitHub details. If information is unavailable, say so.

## Step 3: Produce the output in this exact structure

### A. Jira / business context

Provide:

*   Jira key
*   Jira summary
*   concise description of the business or product goal
*   acceptance criteria summary, if available
*   important context from Jira comments
*   any mismatch between the Jira ticket and the PR

### B. PR overview

Provide:

*   PR title, author, source branch, target branch
*   concise summary of what this PR changes (endpoints, schemas, types, RPCs, etc.)
*   high-level explanation of the design approach
*   main APIs, services, or domains affected
*   overall risk assessment: Low / Medium / High
*   merge-readiness assessment: Ready / Ready with minor feedback / Needs changes / Needs clarification

### C. High-level review summary

Provide:

*   3 to 7 bullets summarizing the most important takeaways
*   what looks well-designed (clear contracts, consistent patterns, safe evolution, etc.)
*   top risks (breaking changes, unclear semantics, poor validation, etc.)

### D. Findings, sorted by severity

Only include findings that are actionable and worth commenting on.

For each finding, use this format:

*   Severity: Critical / Major / Minor / Nit
*   Type: Breaking Change / Design / Consistency / Validation / Documentation / Consumer Experience / Security / Testing / Readability
*   Confidence: High / Medium / Low
*   File: <path>
*   Line: <line number or line range>
*   Issue: <one sentence summary>
*   Why it matters: <plain-English explanation, focused on API consumers and system impact>
*   Recommendation: <specific change or follow-up>
*   Draft PR comment: <clear, respectful comment I could leave on the PR>

Use Severity guidance:

*   Critical: breaking change without versioning, incorrect schema, or likely to break clients
*   Major: significant design flaw, ambiguity, or inconsistency that should be addressed before merge
*   Minor: improvement to clarity, validation, or consistency that may not block merge
*   Nit: optional polish only

### E. Suggested manager narrative

Help me communicate this review effectively to my team member. Provide:

*   a short opening summary I could say or write
*   which findings are likely blockers vs non-blockers
*   which findings should be framed as direct recommendations
*   which findings should be framed as questions or discussion points

## Style guidance

*   Write clearly for a technical manager who understands APIs and system design, but is not deep in every schema detail
*   Prefer concise, direct explanations over jargon
*   Be specific and grounded in the actual diff

/jira