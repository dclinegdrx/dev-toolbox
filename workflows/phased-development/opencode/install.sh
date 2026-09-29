#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./workflows/phased-development/opencode/install.sh [--copy]

Install the phased-development workflow for OpenCode V2.

By default, creates symlinks in ~/.config/opencode so `git pull` updates the
workflow. Use --copy to copy the files instead.

The installer never overwrites an existing destination. Move or remove an
existing workflow installation before retrying.
EOF
}

mode="link"
case "${1:-}" in
  "") ;;
  --copy) mode="copy" ;;
  --help|-h)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

package_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$package_root/../../.." && pwd)"
source_agents="$package_root/agents/workflow"
source_commands="$package_root/commands/workflow"
source_skill="$package_root/skills/phase-implementation"
opencode_config_root="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"

declare -a sources=("$source_agents" "$source_commands" "$source_skill")
for source in "${sources[@]}"; do
  if [[ ! -d "$source" ]]; then
    echo "Missing packaged source: $source" >&2
    exit 1
  fi
done

mkdir -p "$opencode_config_root/agents" "$opencode_config_root/commands" "$opencode_config_root/skills"

declare -a destinations=(
  "$opencode_config_root/agents/workflow"
  "$opencode_config_root/commands/workflow"
  "$opencode_config_root/skills/phase-implementation"
)

for destination in "${destinations[@]}"; do
  if [[ -e "$destination" || -L "$destination" ]]; then
    echo "Refusing to overwrite existing path: $destination" >&2
    echo "Move or remove it, then rerun this installer." >&2
    exit 1
  fi
done

if [[ "$mode" == "link" ]]; then
  ln -s "$source_agents" "${destinations[0]}"
  ln -s "$source_commands" "${destinations[1]}"
  ln -s "$source_skill" "${destinations[2]}"
  echo "Installed OpenCode workflow as symlinks."
  echo "Update it with: git -C \"$repo_root\" pull --ff-only"
else
  cp -R "$source_agents" "${destinations[0]}"
  cp -R "$source_commands" "${destinations[1]}"
  cp -R "$source_skill" "${destinations[2]}"
  echo "Installed copied OpenCode workflow files."
  echo "Copied files will not update automatically; rerun after pulling updates."
fi

printf '\nInstalled:\n  %s\n  %s\n  %s\n' "${destinations[@]}"
printf '\nInstall command: ./workflows/phased-development/opencode/install.sh\n'
printf 'Prerequisite: `/workflow/commit-phase` also requires the `git-commit` skill.\n'
