# dev-toolbox

Development workflow tools and agent configuration.

This repository contains two independent pieces. Adopt either one without
installing the other:

- **Git worktree development workflow** — shell commands for creating feature
  and review worktrees, opening matching tmux windows, and reporting on stale
  review worktrees. Start with [Git worktree development workflow](#git-worktree-development-workflow).
- **OpenCode configuration** — reusable OpenCode V2 agents, slash commands, and
  a phase-implementation skill. Start with [OpenCode configuration](#opencode-configuration)
  and then read [`opencode/README.md`](opencode/README.md).

Installing the worktree commands does not install the OpenCode configuration,
and installing the OpenCode configuration does not install the worktree
commands.

## Git worktree development workflow

The worktree workflow consists of three shell commands:

- `wtdev`: create or reuse a worktree for feature work, open a tmux window for
  it, and optionally launch an agent command.
- `wtreview`: create or reuse an isolated review worktree from a remote branch,
  open a tmux window for it, and optionally launch an agent command.
- `wtcleanup`: identify local review worktrees whose Jira tickets are Done,
  without changing them.

The core worktree commands do not depend on OpenCode. `wtcleanup` can optionally
enrich its report with the most recent OpenCode session for each worktree, but
it still works without OpenCode; unavailable session history is shown as `-`.

### Which command should I use?

Use `wtdev` when you are doing your own development work.

Good `wtdev` use cases:

- starting work on a new local branch
- reopening an existing local branch in its own worktree
- pulling down an existing remote branch that you plan to work on directly
- creating a feature branch from a custom base such as `origin/develop`

Use `wtreview` when you want a review checkout of an existing remote branch.

Good `wtreview` use cases:

- reviewing someone else's PR branch
- checking out an existing remote branch without using the same local branch name
- keeping review worktrees clearly named with a `review-...` prefix

Neither command pushes branches to `origin`. They only fetch from `origin`, create or reuse local branches and worktrees, and open the matching tmux window.

For new `wtdev` branches, the local branch is intentionally left without an upstream. You decide when and where to push it.

### Requirements

- `bash`
- `git`
- `tmux`

`wtcleanup` also requires an authenticated `acli` and `jq`. OpenCode is only
needed if you want `wtcleanup` to include session-history dates.

### Install only the worktree commands

Clone the repo and symlink the commands into a directory on your `PATH`:

```bash
git clone git@github.com:dclinegdrx/dev-toolbox.git ~/src/dev-toolbox
mkdir -p ~/bin ~/.config/dev-toolbox
ln -s ~/src/dev-toolbox/bin/wtdev ~/bin/wtdev
ln -s ~/src/dev-toolbox/bin/wtreview ~/bin/wtreview
ln -s ~/src/dev-toolbox/bin/wtcleanup ~/bin/wtcleanup
cp ~/src/dev-toolbox/config/wt.env.example ~/.config/dev-toolbox/wt.env
```

Make sure `~/bin` is on your `PATH`.

If you already cloned this repository, start with the `mkdir` command instead
of cloning it again.

### Configure

Edit `~/.config/dev-toolbox/wt.env`:

```bash
export WTDEV_ROOT="$HOME/src"
export WTDEV_AGENT_CMD=""
export WTREVIEW_AGENT_CMD="$WTDEV_AGENT_CMD"
```

`WTDEV_ROOT` is the directory that contains your normal repo checkouts. For example, if your repo lives at `~/src/app`, keep `WTDEV_ROOT="$HOME/src"` and pass `app` as the repo name.

Agent launch commands are optional. If `WTDEV_AGENT_CMD` and `WTREVIEW_AGENT_CMD` are empty, the scripts still create or reuse the worktree and tmux window, but they do not send a startup command.

Existing `WTMUX_ROOT` and `WTMUX_AGENT_CMD` settings are still honored as fallbacks, but new config should use `WTDEV_ROOT` and `WTDEV_AGENT_CMD`.

### Usage

Create or open a feature worktree for a new branch:

```bash
wtdev app feature/my-change
```

If `feature/my-change` does not exist locally or on `origin`, `wtdev` creates it locally from the repo default branch, usually `origin/main`.

Open an existing local branch:

```bash
wtdev app feature/existing-local-branch
```

Open an existing remote branch:

```bash
wtdev app feature/existing-remote-branch
```

If `origin/feature/existing-remote-branch` exists but the local branch does not, `wtdev` creates a local tracking branch from the remote branch.

Create a new branch from a custom base:

```bash
wtdev app feature/my-change origin/develop
```

Create or open a review worktree from an existing remote branch:

```bash
wtreview app feature/some-change
```

By default this creates a local branch named `review-feature/some-change` from `origin/feature/some-change`, with a filesystem-safe worktree and tmux window name.

Use a custom local review branch name:

```bash
wtreview app feature/some-change review-some-change
```

### `wtcleanup`

`wtcleanup` identifies local review worktrees whose Jira tickets are Done. It is a read-only report: it scans immediate child directories containing `review`, looks up their Jira keys in one batch, and does not alter local or remote state.

#### Usage

```bash
wtcleanup
wtcleanup /Users/derek.cline/src/GoodRx
```

The scan root resolves in this order:

1. Positional root argument
2. `WTDEV_ROOT`
3. `WTMUX_ROOT`
4. `$HOME/src`

The report uses these states:

- `cleanup`: the Jira ticket is in Jira's Done status category.
- `keep`: the Jira ticket exists but is not Done.
- `unknown`: the Jira key was not returned, or the Jira query failed.
- `no ticket`: no Jira-shaped key was found in the directory name.

`CHECKED OUT` is the directory creation date on macOS when available, otherwise `-`. `LAST REVIEW` is the most recent OpenCode session update for that exact normalized worktree path, otherwise `-`.

Rows are ordered by state (`cleanup`, `keep`, `unknown`, `no ticket`), then by raw directory size from largest to smallest within each state. The summary counts every review directory and shows the raw-KiB total that `cleanup` rows could reclaim. The `Cleanup` section lists each cleanup candidate with a clickable Jira browse link for verification.

Illustrative output:

```text
JIRA         | STATE      | STATUS             | SIZE     | CHECKED OUT  | LAST REVIEW  | DIRECTORY
DEMO-123     | cleanup    | Done               | 2.0M     | 2026-01-02   | 2026-01-10   | app-review-DEMO-123-fix
DEMO-456     | keep       | In Progress        | 512K     | 2026-01-05   | -            | app-review-DEMO-456-feature
DEMO-789     | unknown    | Not found          | 128K     | 2026-01-07   | -            | app-review-DEMO-789-old
-            | no ticket  | No Jira key        | 64K      | 2026-01-08   | -            | app-review-scratch

Summary
Review directories: 4
cleanup: 1
keep: 1
unknown: 1
no ticket: 1
Potential space reclaimed: 2.0M

Cleanup
app-review-DEMO-123-fix | https://goodrx-dev.atlassian.net/browse/DEMO-123
```

If Jira cannot be queried, ticket-bearing rows remain in the report as `unknown` with `Query failed` and the command exits nonzero. OpenCode session-history enrichment is optional: unavailable or malformed history leaves `LAST REVIEW` as `-`, prints a warning, and does not change the command's exit status.

V1 is entirely read-only. It does not remove worktrees, branches, directories, tmux windows, Jira tickets, or OpenCode sessions. Interactive cleanup may be added later, but is not implemented now.

### Behavior

The scripts:

- fetch `origin`
- fast-forward the repo default branch when possible
- create or reuse a git worktree
- sanitize branch names for filesystem paths and tmux window names
- create or reuse a tmux session named after the repo
- name the first tmux window after the repo default branch
- open the target tmux window whether run inside or outside tmux

`wtdev` branch behavior:

- if the branch exists locally, it creates or reuses a worktree for that local branch
- if the branch exists on `origin` but not locally, it creates a local tracking branch from `origin/<branch>`
- if the branch does not exist locally or on `origin`, it creates a new local branch from the default branch or provided base
- new local branches are created without an upstream, so plain `git push` will not choose a remote destination for you
- it does not push the branch

`wtreview` branch behavior:

- expects the target branch to exist on `origin`
- creates a local review branch named `review-<remote-branch>` unless you provide a custom local name
- reuses an existing local review branch or worktree when present
- it does not push the branch

## OpenCode configuration

The `opencode/` directory is a separate, installable OpenCode V2 package. It
contains reusable workflow agents, `/workflow/*` slash commands, and the
`phase-implementation` skill. It does not configure an AI provider,
credentials, MCP servers, global permissions, or terminal preferences.

### Install only the OpenCode configuration

Clone this repository if needed, then run the installer:

```bash
git clone git@github.com:dclinegdrx/dev-toolbox.git ~/src/dev-toolbox
cd ~/src/dev-toolbox
./opencode/install.sh
```

The default install creates symlinks under `~/.config/opencode`, so pulling a
new revision updates the installed definitions. To make a one-time independent
copy instead, use:

```bash
./opencode/install.sh --copy
```

The OpenCode package has its own requirements, model configuration, workflow
instructions, update steps, and removal instructions. Read
[`opencode/README.md`](opencode/README.md) before using it.

## Other contents

The [`skills/README.md`](skills/README.md) documents standalone agent skills in
this repository. The OpenCode phased-development skill intentionally lives
under [`opencode/skills/`](opencode/skills/) with its matching agents and
commands.

Add future shell commands under `bin/` and keep their setup instructions with
the relevant documentation.
