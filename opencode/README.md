# OpenCode Phased Development Workflow

A human-reviewed OpenCode V2 workflow for turning an investigated change into
small, independently reviewable commits.

It packages reusable OpenCode workflow definitions only. It does **not**
configure an AI provider, credentials, MCP servers, global permissions, or
terminal preferences.

## What Is Included

```text
opencode/
├── agents/workflow/     # Planner, coordinator, implementers, committer, reviewer
├── commands/workflow/   # /workflow/* slash commands
└── skills/
    └── phase-implementation/
```

The workflow roles are deliberately separated:

- **Planner** creates a phased Markdown plan.
- **Coordinator** selects Luna, Terra, or Sol and delegates exactly one phase.
- **Implementers** make and verify only their assigned phase. They mark it
  `IN PROGRESS`, but never stage or commit.
- **Phase committer** turns an accepted phase from `IN PROGRESS` to `COMPLETE`
  and creates one commit from the already-staged implementation.
- **Integration reviewer** examines the full completed branch without editing.

## Requirements

- [OpenCode V2](https://opencode.ai/v2/docs/)
- A configured model provider. The included agent profiles use these model IDs:
  - `gdrx-litellm/gpt-5.6-luna#high`
  - `gdrx-litellm/gpt-5.6-terra#high`
  - `gdrx-litellm/gpt-5.6-sol#high`
- The `git-commit` skill for `/workflow/commit-phase`. This package does not
  duplicate that skill, because it is maintained separately.

If your OpenCode model catalog uses different IDs, edit the `model:` field in
each file under `opencode/agents/workflow/` before installing.

## Install

Clone this repository, then run the installer:

```bash
git clone git@github.com:dclinegdrx/dev-toolbox.git ~/src/dev-toolbox
cd ~/src/dev-toolbox
./opencode/install.sh
```

The default install uses symlinks:

```text
~/.config/opencode/agents/workflow
~/.config/opencode/commands/workflow
~/.config/opencode/skills/phase-implementation
```

Symlinks are recommended because `git pull` updates the definitions in place.
The installer refuses to overwrite existing paths. For a one-time independent
copy, use:

```bash
./opencode/install.sh --copy
```

## Workflow

Start OpenCode in a ticket worktree and select the model you want to use for
investigation:

```bash
cd ~/worktrees/subscriptions-COND-1234
opencode2
```

Then use the workflow:

```text
Discuss and investigate
/workflow/finalize-plan
/workflow/start-phase docs/plans/<plan>.md 1
Review, verify, and stage the accepted phase changes
/workflow/commit-phase docs/plans/<plan>.md 1
Repeat for later phases
/workflow/integration-review docs/plans/<plan>.md
Push after your final checks
```

### Important Details

- `/workflow/finalize-plan` stays in the current session and preserves its
  selected agent and model.
- `/workflow/start-phase` switches the parent to the coordinator. The
  coordinator chooses an implementation agent and launches it in a background
  child session.
- The implementation child updates its assigned plan phase from `NOT STARTED`
  to `IN PROGRESS` and leaves all changes unstaged.
- After human review, stage the implementation **and the plan file**. The
  committer expects the staged plan transition to `IN PROGRESS`, changes it to
  `COMPLETE`, stages the plan again, and commits the final combined diff.
- `/workflow/integration-review` is read-only. Run any recommended mutable
  checks yourself.
- The workflow never pushes.

## Update or Remove

For symlink installs:

```bash
git -C ~/src/dev-toolbox pull --ff-only
```

To remove a symlink installation:

```bash
rm ~/.config/opencode/agents/workflow
rm ~/.config/opencode/commands/workflow
rm ~/.config/opencode/skills/phase-implementation
```

For copied installs, remove the directories and run the installer again after
pulling the desired revision.

## Maintainer

Maintainer: `@dclinegdrx`  
Last reviewed: 2026-09-08
