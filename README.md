# dev-toolbox

Development workflow tools, scripts, and agent helpers.

This repo starts with two git worktree + tmux helpers:

- `wtmux`: create or reuse a worktree for feature work, open a tmux window for it, and optionally launch an agent command.
- `wtreview`: create or reuse an isolated review worktree from a remote branch, open a tmux window for it, and optionally launch an agent command.

## Which command should I use?

Use `wtmux` when you are doing your own development work.

Good `wtmux` use cases:

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

## Requirements

- `bash`
- `git`
- `tmux`

## Install

Clone the repo and symlink the commands into a directory on your `PATH`:

```bash
git clone git@github.com:dclinegdrx/dev-toolbox.git ~/src/dev-toolbox
mkdir -p ~/bin ~/.config/dev-toolbox
ln -s ~/src/dev-toolbox/bin/wtmux ~/bin/wtmux
ln -s ~/src/dev-toolbox/bin/wtreview ~/bin/wtreview
cp ~/src/dev-toolbox/config/wt.env.example ~/.config/dev-toolbox/wt.env
```

Make sure `~/bin` is on your `PATH`.

## Configure

Edit `~/.config/dev-toolbox/wt.env`:

```bash
export WTMUX_ROOT="$HOME/src"
export WTMUX_AGENT_CMD=""
export WTREVIEW_AGENT_CMD="$WTMUX_AGENT_CMD"
```

`WTMUX_ROOT` is the directory that contains your normal repo checkouts. For example, if your repo lives at `~/src/app`, keep `WTMUX_ROOT="$HOME/src"` and pass `app` as the repo name.

Agent launch commands are optional. If `WTMUX_AGENT_CMD` and `WTREVIEW_AGENT_CMD` are empty, the scripts still create or reuse the worktree and tmux window, but they do not send a startup command.

## Usage

Create or open a feature worktree for a new branch:

```bash
wtmux app feature/my-change
```

If `feature/my-change` does not exist locally or on `origin`, `wtmux` creates it locally from the repo default branch, usually `origin/main`.

Open an existing local branch:

```bash
wtmux app feature/existing-local-branch
```

Open an existing remote branch:

```bash
wtmux app feature/existing-remote-branch
```

If `origin/feature/existing-remote-branch` exists but the local branch does not, `wtmux` creates a local tracking branch from the remote branch.

Create a new branch from a custom base:

```bash
wtmux app feature/my-change origin/develop
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

## Behavior

The scripts:

- fetch `origin`
- fast-forward the repo default branch when possible
- create or reuse a git worktree
- sanitize branch names for filesystem paths and tmux window names
- create or reuse a tmux session named after the repo
- name the first tmux window after the repo default branch
- open the target tmux window whether run inside or outside tmux

`wtmux` branch behavior:

- if the branch exists locally, it creates or reuses a worktree for that local branch
- if the branch exists on `origin` but not locally, it creates a local tracking branch from `origin/<branch>`
- if the branch does not exist locally or on `origin`, it creates a new local branch from the default branch or provided base
- it does not push the branch

`wtreview` branch behavior:

- expects the target branch to exist on `origin`
- creates a local review branch named `review-<remote-branch>` unless you provide a custom local name
- reuses an existing local review branch or worktree when present
- it does not push the branch

## Future Tools

Add shell commands under `bin/`. Future agent skills and related docs can live under `skills/`.
