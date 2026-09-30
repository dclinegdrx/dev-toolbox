Please perform a code review of this pull request: {clipboard}

Your goal is to help me, an engineering manager, quickly understand the purpose of the change, the business context behind it, the technical impact, and any issues worth raising with the author.

## Step 1: Gather context

1. Query GitHub for the PR details, including:
   - title
   - author
   - source branch
   - target branch
   - PR description
   - changed files
2. **Check for branch stacking.** Singularity PRs are often stacked. If the description notes that this branch is based on another feature branch (not `main`), note which commits/files belong solely to this PR vs. the parent branches. Focus your review only on the work scoped to this ticket.
3. Diff the PR branch against:
   - `main`, or
   - `master` if `main` does not exist
   - If the PR is stacked, diff against the parent branch instead of `main` to isolate only this PR's changes.
4. Check the PR description for a **Lifecycle environment link** (e.g., `ui-oss.lifecycle.lfc.goodrx.com/environments/...`). Note whether a preview environment is deployed and available for manual verification.
5. Extract the Jira issue key from the PR title if present, then query Jira for:
   - summary/title
   - description
   - acceptance criteria, if available
   - relevant comments
6. Use the Jira information to understand the intended business outcome and expected behavior.

---

## Step 2: Understand the frontend context

Before reviewing the code, orient yourself to where this change lives in the monorepo:

- **Package location:** Is this in `apps/` (a deployable app like `next-web`) or `packages/` (a shared library)? Identify the package name (e.g., `@goodrx/pages.accounts.conditions-subscription`).
- **Domain:** Which domain does this touch — `account`, `drug`, `editorial`, `marketing`, `platform`, or `pricing`?
- **Layer:** Is this a UI component (`packages/components/`), a page/feature (`packages/pages/`), a shared utility (`packages/utils/`), or CMS content model (`packages/cms/`)?
- **Analytics:** Does the PR add or modify Segment analytics events (`page`, `navigationSelected`, etc.)? If so, check whether a tracking plan link is provided.
- **Feature flags:** Does the PR gate new behavior behind an Optimizely experiment flag? Note the flag name and whether the PR is safe to ship without the flag being enabled.
- **State machines:** Does the change touch an XState-style actor or state machine (e.g., `*StateMachine.ts`, `*Actor.ts`)? These require extra scrutiny on state transitions and side-effect ordering.

---

## Step 3: Review the code

Review the PR with focus on:

### React & TypeScript
- Correctness of component logic and potential rendering bugs
- Hook usage (correct dependency arrays, stale closure risks, unnecessary re-renders)
- TypeScript type safety — especially ensure GraphQL operations use generated types from `pnpm codegen` rather than hand-rolled types
- Zod schema correctness if runtime validation is involved
- No `console.log` in production code (use `@goodrx/utils.logger` instead)
- DRY principles and single-responsibility components

### Naming & Structure Conventions
- **PascalCase** for components, interfaces, type aliases, and file names
- **camelCase** for variables and functions
- **kebab-case** for folder names (except inside `src/`, where PascalCase applies)
- Package naming follows `@goodrx/{type}.{domain}.{component-name}` pattern
- New packages should be scaffolded with `pnpm create:package`, not created manually
- `CODEOWNERS` updated for any new packages

### Styling
- Tailwind classes are consistent with project conventions (v3 or v4, depending on the package)
- Complex or context-aware styling uses `cva` in a `.styles.ts` file rather than inline class strings
- No arbitrary Tailwind hacks that could break responsive layouts or parent-context assumptions

### Data Fetching & GraphQL
- Apollo Client queries and mutations use generated types
- Proper loading, error, and empty states are handled in UI
- No overfetching — query fields match what the component actually uses

### Analytics (Segment)
- `page` event fires on component mount with correct `screenName` and `category`
- `navigationSelected` (or equivalent interaction events) fire with correct metadata
- Shared analytics constants are used where multiple events share fields (spread pattern)
- A tracking plan reference (spreadsheet link or row numbers) is provided in the PR description
- Tests assert that analytics fire with the correct shape — not just that they fire

### State Machines
- State transitions are exhaustive — no reachable state is unhandled
- Side effects (actors, services) are invoked in the correct states, not duplicated
- IDs used for deterministic lookups (e.g., drug IDs) take precedence over text-based pattern matching, which can fail on generic or incomplete labels

### Testing
- Unit tests (`.spec.ts` / `.spec.tsx`) are colocated with the implementation
- `test.each` used for parameterized cases; happy path and error scenarios are separated
- GraphQL mocks use `mockQueries` / `mockMutations` from `@goodrx/config.jest/helpers`
- Analytics events are verified with dedicated `describe('analytics')` blocks
- Playwright E2E tests updated if user-visible flows changed; E2E failures in the CI run are assessed for relatedness to this PR
- Codecov report is reviewed — look for meaningful drops in coverage on modified files

### Accessibility & UX
- Interactive elements are keyboard-accessible and have appropriate ARIA attributes
- Loading, empty, error, and success UI states are all present for meaningful screens
- Responsive behavior is covered (mobile and desktop, where applicable)

### Performance & Bundle
- No large or unnecessary dependencies introduced
- Lazy loading / code splitting is used appropriately for heavy components
- No unnecessary renders introduced (memo, useMemo, useCallback used where justified — not cargo-culted)

### Security & Data Integrity
- No PII or sensitive data exposed in analytics payloads or client-side logs
- No unsafe use of `dangerouslySetInnerHTML`
- Health/telehealth data handled in compliance with applicable standards

Do not nitpick minor style issues unless they affect correctness, maintainability, or team standards in a meaningful way.

Do not invent missing Jira or GitHub details. If information is unavailable, say so.

---

## Step 4: Produce the output in this exact structure

### A. Jira / business context
Provide:
- Jira key
- Jira summary
- Concise description of the business goal
- Acceptance criteria summary, if available
- Important context from Jira comments
- Any mismatch between the Jira ticket and the PR

### B. PR overview
Provide:
- PR title, author, source branch, target branch
- Whether the branch is stacked — and which files/commits are scoped to this ticket only
- Lifecycle preview environment URL, if available
- Concise summary of what this PR changes
- High-level explanation of the implementation approach
- Main files, packages, or domains affected
- Overall risk assessment: **Low / Medium / High**
- Merge-readiness assessment: **Ready / Ready with minor feedback / Needs changes / Needs clarification**

### C. High-level review summary
Provide:
- 3–7 bullets summarizing the most important review takeaways
- Call out what looks good
- Call out the top risks or concerns

### D. Findings, sorted by severity

Only include findings that are actionable and worth commenting on.

For each finding, use this format:

- **Severity:** Critical / Major / Minor / Nit
- **Type:** Bug / Edge Case / Accessibility / Analytics / Styling / Performance / Testing / TypeScript / Design / Security / Maintainability
- **Confidence:** High / Medium / Low
- **File:** `<path>`
- **Line:** `<line number or range>`
- **Issue:** One sentence summary
- **Why it matters:** Plain-English explanation
- **Recommendation:** Specific change or follow-up
- **Draft PR comment:** Clear, respectful comment I could leave on the PR

Use severity guidance:
- **Critical:** Likely production bug, broken user flow, data integrity issue, security concern, or PII exposure
- **Major:** Important correctness, reliability, analytics accuracy, or accessibility issue that should likely be addressed before merge
- **Minor:** Useful improvement, missing test coverage, or edge case that may not need to block merge
- **Nit:** Optional polish only

### E. Suggested manager narrative

Help me communicate this review effectively to my team member. Provide:
- A short opening summary I could say or write
- Which findings are likely blockers vs. non-blockers
- Which findings should be framed as direct recommendations
- Which findings should be framed as questions or discussion points

## Style guidance
- Write clearly for a technical manager who understands software engineering but is not the deepest expert in every component and flow.
- Prefer concise, direct explanations over jargon.
- Be specific and grounded in the actual diff.
- For stacked PRs, be explicit about which layer of the stack a finding belongs to.
- If the PR looks solid, say so clearly rather than forcing extra findings.
- If you are uncertain, state your assumption.

## Skills

/jira
/singularity-review-env for preparing the current git worktree for building and running tests