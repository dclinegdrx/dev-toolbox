# Organize the Phased Development Workflow

## Overview

Reorganize the repository around a single phased agentic-development workflow with two sibling implementations: portable Markdown prompts that work with Alfred's `{clipboard}` expansion or manual copy/paste, and the existing installable OpenCode package. The shared workflow documentation will define the lifecycle and invariants, while each implementation will retain the mechanics appropriate to its environment.

The intended final layout is:

```text
workflows/
└── phased-development/
    ├── README.md
    ├── prompts/
    │   ├── README.md
    │   ├── finalize-plan.md
    │   ├── implement-phase.md
    │   ├── commit-phase.md
    │   └── integration-review.md
    └── opencode/
        ├── README.md
        ├── install.sh
        ├── agents/workflow/
        ├── commands/workflow/
        └── skills/phase-implementation/
```

The worktree commands under `bin/` and standalone skills under `skills/` remain independent and are not otherwise reorganized.

**Intended comparison base:** `origin/main`

## Assumptions and Constraints

- The four untracked files under `tmp/` are the current source copies of the portable prompts. Preserve their content during the initial move so later behavior changes remain reviewable.
- `prompts/` is intentionally implementation-neutral. Alfred is a supported launcher, not the only way to use the prompts.
- `{clipboard}` remains the Alfred placeholder for the plan path; manual users replace it with an explicit path.
- Existing OpenCode slash-command names, installed destinations under `~/.config/opencode`, model routing, and the external `git-commit` skill dependency remain compatible unless a documented shared invariant requires an update.
- `/workflow/finalize-plan` continues to preserve the active session's selected agent and model. Keep `planner.md` as an optional direct agent rather than silently changing that command's behavior, and document the distinction.
- OpenCode may enforce shared behavior through multiple agents, commands, skills, and permissions; the portable prompts remain self-contained. Do not introduce generation or templating solely to make their source text identical.
- No runtime service, schema, data migration, or deployment rollout is involved.

## Risks and Rollout Considerations

- Relocating `opencode/` changes repository paths. Existing symlink installations will point at removed paths after pulling the change and must be removed and reinstalled from the new installer location. Document this migration prominently before the move is considered complete.
- The installer currently refuses to overwrite destinations. Migration instructions must remove only the three known workflow symlinks or directories after the user verifies them; the installer must retain its non-overwrite safety.
- Repository-relative links in `README.md`, `skills/README.md`, OpenCode documentation, and installer messages can become stale during the move.
- The prompt snippets contain newer safety and recovery guidance than parts of the OpenCode implementation. Reconcile universal workflow rules deliberately while retaining intentional differences such as explicit OpenCode phase numbers, model routing, and stricter read-only permissions.
- Prompt or agent edits can weaken staging, commit, or destructive-operation boundaries. Review those changes as workflow behavior, not merely prose.
- The workflow handles repository contents and may encounter sensitive code, but this reorganization introduces no telemetry, credential storage, or external data transfer. Documentation must continue to avoid embedding secrets or personal clipboard contents.
- There are no meaningful performance, retry, idempotency, or observability changes beyond preserving commit-finalization recovery and safe repeatability of installation tests.

## Phase 1: Establish the shared workflow and portable-prompt implementation

**Status: COMPLETE**

### Goal

Make the common phased workflow and its portable prompt implementation discoverable and usable from a stable, tracked location without changing the existing OpenCode package.

### Implementation

- Create `workflows/phased-development/README.md` as the canonical description of the process:
  - planning, one-phase implementation, human review and staging, phase finalization and commit, repetition, and full-branch integration review;
  - the three authoritative statuses: `NOT STARTED`, `IN PROGRESS`, and `COMPLETE`;
  - one active phase at a time, human acceptance before completion, no automatic push, and full-branch final review;
  - a short comparison of when to use portable prompts versus OpenCode;
  - links to both implementations.
- Create `workflows/phased-development/prompts/README.md` with the four-step usage sequence, Alfred setup guidance, manual copy/paste instructions, `{clipboard}` substitution behavior, and the human staging boundary between implementation and commit finalization.
- Move the four untracked prompt copies from `tmp/` into `workflows/phased-development/prompts/`, dropping the redundant `prompt-` filename prefix. Preserve prompt bodies in this phase except for path-independent corrections required by the move.
- Update the root `README.md` to introduce the phased development workflow as a shareable tool family and link to its shared README and both implementations. Keep worktree installation and behavior documentation intact.
- Do not relocate or behaviorally rewrite the existing `opencode/` package in this phase. Links from the shared README should accurately reflect its current location so the repository remains navigable after this commit.

### Verification

- Run `git status --short` and confirm the four original `tmp/` files are represented only by their intended tracked destinations, with no unrelated user files removed.
- Compare each destination prompt with its original source or review the rename-aware diff to confirm the bodies were preserved.
- Follow the root README to the shared workflow README, the prompt README, each prompt, and the still-root-level OpenCode README; confirm every relative link resolves.
- Manually inspect one prompt with `{clipboard}` substitution and with an explicit plan path to ensure both documented usage modes are understandable.
- Run `bash tests/wtcleanup-test.sh` to confirm the unrelated worktree tooling remains unaffected.

### Completion Criteria

- The portable prompts are tracked under `workflows/phased-development/prompts/` and no longer depend on `tmp/`.
- A new reader can discover the shared process from the root README and choose either implementation.
- The shared documentation clearly separates workflow invariants from implementation mechanics.
- Existing OpenCode installation paths and behavior are unchanged in this phase.
- The existing worktree test passes.

## Phase 2: Relocate the OpenCode implementation without changing its installed interface

**Status: COMPLETE**

### Goal

Place the OpenCode package beside the portable prompts while preserving its slash commands, installed configuration layout, safety checks, and independent installation behavior.

### Implementation

- Move the complete `opencode/` tree to `workflows/phased-development/opencode/` without mixing semantic prompt changes into the relocation diff.
- Update the relocated `install.sh` to resolve sources from its package directory rather than assuming a root-level `opencode/` path. Preserve both symlink and `--copy` modes, XDG configuration support, refusal to overwrite existing destinations, and the three installed destinations:
  - `agents/workflow`
  - `commands/workflow`
  - `skills/phase-implementation`
- Update `workflows/phased-development/opencode/README.md`, the shared workflow README, root `README.md`, and `skills/README.md` for the final paths and responsibilities.
- Add explicit migration instructions for existing symlink installations: verify and remove the old three workflow destinations, then run `./workflows/phased-development/opencode/install.sh`. Explain that a pull containing the relocation can temporarily leave old symlinks broken until reinstall.
- Add `tests/opencode-install-test.sh`, following the existing Bash test style, that uses temporary `XDG_CONFIG_HOME` directories to verify:
  - default installation creates the expected symlinks to the relocated sources;
  - `--copy` creates independent directories and files;
  - existing destinations are not overwritten and produce a nonzero exit;
  - no real user configuration is read or modified.
- Update installer usage and output to show the new repository-relative invocation while reporting the effective configuration destination accurately.

### Verification

- Run `bash -n workflows/phased-development/opencode/install.sh tests/opencode-install-test.sh`.
- Run `bash tests/opencode-install-test.sh`.
- Run `bash tests/wtcleanup-test.sh`.
- Search tracked Markdown and shell files for stale repository-relative references to `./opencode/install.sh`, `opencode/README.md`, `../opencode/skills/`, and `$repo_root/opencode`.
- Inspect the rename-aware Git diff to confirm agents, commands, and the skill moved without unintended semantic changes.
- From the root README, follow all links into the shared workflow, prompts, relocated OpenCode package, and standalone skills.

### Completion Criteria

- Both implementations are siblings under `workflows/phased-development/`.
- Fresh symlink and copy installations use the relocated package and preserve the existing `~/.config/opencode` interface.
- Existing users have clear, safe migration instructions for broken old-path symlinks.
- Installer tests cover both install modes and overwrite refusal without touching real configuration.
- No stale documented root-level OpenCode paths remain, and all existing tests pass.

## Phase 3: Align shared workflow guarantees and document intentional differences

**Status: COMPLETE**

### Goal

Resolve accidental behavioral drift between the portable prompts and OpenCode while making implementation-specific differences explicit and preserving safety boundaries.

### Implementation

- Add a parity table to `workflows/phased-development/README.md` mapping each lifecycle stage to its portable prompt, OpenCode command, and relevant OpenCode agent or skill.
- Treat the following as shared guarantees and align the OpenCode definitions where they currently lag behind the portable prompts:
  - plans use dated `docs/plans/YYYY-MM-DD-<name>.md` filenames;
  - the plan is the outcome source of truth and the repository is the implementation-detail source of truth;
  - unrelated local work is preserved, and non-overlapping changes do not force an unnecessary stop;
  - minor repository drift may be handled and disclosed, while material architecture, contract, migration, security, compatibility, or phase-boundary changes require clarification;
  - implementation never stages, commits, pushes, or marks a phase `COMPLETE`;
  - commit finalization changes only the accepted phase, commits only human-staged implementation, and repairs a newly stranded `COMPLETE` status back to `IN PROGRESS` if finalization fails;
  - reports identify the plan path, phase statuses, verification actually performed, deviations, and intentionally untouched work;
  - integration review covers the full branch and never claims unrun verification passed.
- Apply each rule in the appropriate OpenCode layer rather than duplicating all text everywhere: planning rules in `finalize-plan.md` and optional `planner.md`, phase rules in the `phase-implementation` skill, finalization rules in the command and committer agent, and review rules in the integration-review command and agent.
- Preserve and document intentional differences:
  - portable implementation selects the next incomplete phase, while OpenCode commands require an explicit phase number and validate it;
  - OpenCode uses coordinator model routing and child sessions;
  - OpenCode's integration reviewer remains constrained by its read-only permissions and recommends mutable checks rather than running them;
  - `/workflow/finalize-plan` stays in the current session, while `planner.md` remains an optional directly selected agent.
- Review the resulting definitions for contradictory instructions, especially around dirty worktrees, staging authority, plan status transitions, recovery, and test execution. Prefer one authoritative statement per OpenCode layer and links or concise references in documentation over unnecessary repetition.
- Update implementation READMEs to describe the reconciled behavior and intentional differences without presenting either implementation as a byte-for-byte equivalent of the other.

### Verification

- Review all four portable prompts and all OpenCode commands, workflow agents, and the phase-implementation skill against the parity table.
- Search for conflicting rules such as unconditional rejection of all unstaged work, permission to stage implementation files during finalization, implementation marking phases `COMPLETE`, or integration review modifying files.
- Walk through these scenarios using the text and permission definitions:
  - a clean new phase;
  - unrelated non-overlapping local work;
  - overlapping local work requiring clarification;
  - missing required staged files at finalization;
  - a commit failure after the plan status changed;
  - a completed plan receiving a full-branch read-only review.
- Run `bash tests/opencode-install-test.sh` and `bash tests/wtcleanup-test.sh`.
- Run `git diff --check` and inspect the full branch diff against `origin/main` for accidental scope expansion.

### Completion Criteria

- The shared README accurately maps both implementations and defines their common guarantees.
- Universal workflow rules are consistent across prompts and OpenCode layers.
- Intentional differences are documented and supported by OpenCode permissions and invocation patterns.
- Finalization recovery cannot intentionally leave an uncommitted phase marked `COMPLETE`.
- No implementation gains permission to push, discard unrelated work, or bypass human staging and review.
- All repository tests pass and the complete diff contains only the workflow organization, documentation, installer validation, and deliberate behavior alignment.

## Final Integration Verification

After all phases are complete:

1. Confirm every phase in this plan is `COMPLETE` and review `git diff --check origin/main...HEAD` plus the complete commit history for phase boundaries.
2. Run `bash tests/wtcleanup-test.sh` and `bash tests/opencode-install-test.sh` from the repository root.
3. Run Bash syntax checks for the worktree scripts, relocated installer, and test scripts.
4. Test both OpenCode install modes in disposable configuration roots and verify overwrite refusal.
5. Navigate from the root README through both workflow implementations and standalone skills, checking every changed relative link.
6. Manually simulate the documented lifecycle once with the portable prompts and once with the OpenCode command mapping, paying particular attention to plan status, human staging, failed-finalization recovery, and final comparison-base selection.
7. Verify `git status --short` contains no generated installation artifacts or unexpected changes.

## Rollback

The repository changes can be reverted by phase because no external data is migrated. If the OpenCode relocation must be rolled back, restore the root-level package and its documentation paths, then reinstall the three OpenCode workflow destinations so their symlink targets match the restored layout. Never remove broader OpenCode configuration directories as part of rollback.
