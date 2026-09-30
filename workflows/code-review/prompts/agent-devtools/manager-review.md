Please perform a code review of this pull request: {clipboard}

Your goal is to help me, an engineering manager, quickly understand:
- what user or agent problem this change is solving
- how the skill or tooling behavior changes
- whether the change is safe, discoverable, maintainable, and likely to work in real agent workflows
- any issues that are worth raising with the author

## Step 1: Gather context
1. Query GitHub for the PR details, including:
   - title
   - author
   - source branch
   - target branch
   - PR description
   - changed files

2. Check out the PR branch, or confirm it is already checked out and up to date.

3. Diff the PR branch against:
   - main, or
   - master if main does not exist

4. Classify the PR into one or more change types:
   - skill content change
   - shared references or connectors change
   - CLI / install / catalog behavior change
   - setup / auth / publish / workflow change
   - docs only
   - test only

5. If the PR changes one or more skills, inspect the full skill folder for each affected skill, not just the diff. Review adjacent files such as:
   - SKILL.md
   - references/
   - scripts/
   - assets/
   - CONNECTORS.md or shared reference files, if present

6. If the PR changes shared tooling, inspect the relevant surfaces that could affect skill discovery or execution, such as:
   - CLI behavior
   - manifest or catalog generation
   - install flow
   - GitHub auth / setup flow
   - branch preview or docs generation
   - sandbox or runtime packaging assumptions

7. Extract the Jira issue key from the PR title if present, then query Jira for:
   - summary/title
   - description
   - acceptance criteria, if available
   - relevant comments

8. Use the Jira information, PR description, and changed files to understand the intended user outcome and expected agent behavior.

Do not invent missing Jira or GitHub details. If information is unavailable, say so.

## Step 2: Review the change
Review the PR with focus on:

### A. Skill behavior and contract quality
- Is the skill's purpose clear?
- Are the trigger conditions specific enough that an agent would use it at the right times?
- Are the "use when" and "do not use when" boundaries clear and non-overlapping?
- Are required inputs, outputs, and success criteria explicit?
- Does the skill over-promise what the agent can actually do?

### B. Correctness in real agent workflows
- If an agent followed these instructions literally, would the workflow likely succeed?
- Are there ambiguous steps, missing prerequisites, or hidden assumptions?
- Are file paths, repo paths, command examples, and referenced docs likely to resolve correctly?
- Are relative paths and dependency references consistent with the repo layout?
- If this changes install or discovery behavior, would users still be able to find and use the skill correctly?

### C. Safety and guardrails
- Does the change create risk of unsafe, overly broad, or policy-breaking behavior?
- Does it clearly separate required actions from optional actions?
- Does it avoid encouraging destructive, irreversible, or speculative actions without confirmation?
- Does it avoid hallucination-prone instructions such as assuming missing context, fabricating data, or silently skipping validation?

### D. Maintainability and readability
- Is the skill or tooling easy to understand and update later?
- Are instructions structured clearly enough for both humans and agents?
- Are duplicated instructions or references creating drift risk?
- Are shared files being reused appropriately instead of copied unnecessarily?

### E. Tooling and platform impact
- Could this break CLI behavior, manifest generation, install flow, auth/setup flow, previews, or packaging?
- Does the change preserve backward compatibility for existing skill IDs, paths, or install commands where that matters?
- If the PR changes behavior that affects discovery, install, or packaging, is that impact tested and documented?

### F. Testing and validation
- Is there enough validation for the kind of change being made?
- For skill-only changes, is there evidence of manual validation, examples, or scenario testing?
- For CLI or shared tooling changes, are there unit/integration tests covering the new behavior and obvious regressions?
- Are failure cases and fallback paths tested where relevant?

### G. Consistency with Jira and intended outcome
- Does the implementation match the Jira ticket and acceptance criteria?
- Does the change solve the user problem described, or only part of it?
- Is there hidden scope expansion or untracked behavior change?

Do not nitpick wording unless it materially affects agent behavior, safety, discoverability, correctness, or long-term maintainability.

## Step 3: Produce the output in this exact structure

### A. Jira / business context
Provide:
- Jira key
- Jira summary
- concise description of the user or business goal
- acceptance criteria summary, if available
- important context from Jira comments
- any mismatch between the Jira ticket and the PR

### B. PR overview
Provide:
- PR title, author, source branch, target branch
- concise summary of what this PR changes
- change classification:
  - skill content
  - shared references
  - CLI / catalog / install
  - setup / auth / workflow
  - docs / tests
- high-level explanation of the implementation approach
- main files, skill folders, or modules affected
- overall risk assessment: Low / Medium / High
- merge-readiness assessment: Ready / Ready with minor feedback / Needs changes / Needs clarification

### C. High-level review summary
Provide:
- 3 to 7 bullets summarizing the most important review takeaways
- call out what looks good
- call out the top risks or concerns
- explicitly say whether the main risk is:
  - incorrect agent behavior
  - poor discoverability / installability
  - weak safety boundaries
  - maintainability drift
  - insufficient validation
  - or no major concern

### D. Findings, sorted by severity
Only include findings that are actionable and worth commenting on.

For each finding, use this format:

- Severity: Critical / Major / Minor / Nit
- Type: Behavior Contract / Bug / Edge Case / Safety / Discoverability / Tooling / Testing / Maintainability / Readability / Design / Docs
- Confidence: High / Medium / Low
- File: &lt;path&gt;
- Line: &lt;line number or line range&gt;
- Issue: &lt;one sentence summary&gt;
- Why it matters: &lt;plain-English explanation, including likely agent or user impact&gt;
- Recommendation: &lt;specific change or follow-up&gt;
- Draft PR comment: &lt;clear, respectful comment I could leave on the PR&gt;

Use Severity guidance:
- Critical: likely unsafe behavior, broken install/discovery path, major tooling break, or agent behavior that is likely wrong in production use
- Major: important correctness, safety, maintainability, or validation concern that should likely be addressed before merge
- Minor: useful improvement, missing edge case, or validation gap that may not need to block merge
- Nit: optional polish only

### E. Suggested manager narrative
Help me communicate this review effectively to my team member. Provide:
- a short opening summary I could say or write
- which findings are likely blockers vs non-blockers
- which findings should be framed as direct recommendations
- which findings should be framed as questions or discussion points

### F. Agent-skill-specific reviewer notes
Add a short section with:
- "What would happen if an agent followed this literally?"
- "What is the most likely failure mode?"
- "Is the skill/tooling change easy to discover and adopt?"
- "What validation would give me the most confidence before merge?"

## Review heuristics specific to this repo

When the PR is mostly skill content:
- Treat the skill as a behavior spec, not just documentation
- Review whether the instructions are concrete, bounded, and executable
- Look for missing prerequisites, vague trigger logic, conflicting instructions, and path/reference drift
- Check whether examples, references, and companion files are still aligned

When the PR touches shared tooling:
- Review for downstream impact on skill discovery, installation, auth, previews, packaging, and existing workflows
- Pay extra attention to manifest handling, GitHub auth assumptions, local-vs-remote resolution, and backward compatibility
- Expect tests for meaningful behavior changes

When the PR touches both skill content and tooling:
- Review both the human-facing authoring quality and the runtime/distribution implications
- Call out whether the user-visible skill behavior and the packaging/discovery layer are still aligned

## Style guidance
- Write clearly for a technical manager who understands software engineering but is not the deepest expert in every code path.
- Prefer concise, direct explanations over jargon.
- Be specific and grounded in the actual diff.
- If you are uncertain, say what assumption you are making.
- If the PR looks solid, say so clearly rather than forcing extra findings.
- For skill-content PRs, optimize for behavior clarity over prose preferences.
- For tooling PRs, optimize for regression detection over stylistic commentary.

/jira