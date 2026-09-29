#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
installer="$repo_root/workflows/phased-development/opencode/install.sh"
package_root="$repo_root/workflows/phased-development/opencode"
tmpdir="$(mktemp -d)"

cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

assert_contains() {
  case "$1" in
    *"$2"*) ;;
    *) fail "expected output to contain: $2" ;;
  esac
}

link_config="$tmpdir/link-config"
link_home="$tmpdir/link-home"
link_output="$(HOME="$link_home" XDG_CONFIG_HOME="$link_config" "$installer")"
link_root="$link_config/opencode"

[ -L "$link_root/agents/workflow" ] || fail "expected agents workflow symlink"
[ -L "$link_root/commands/workflow" ] || fail "expected commands workflow symlink"
[ -L "$link_root/skills/phase-implementation" ] || fail "expected phase implementation skill symlink"
[ "$(readlink "$link_root/agents/workflow")" = "$package_root/agents/workflow" ] || fail "unexpected agents symlink target"
[ "$(readlink "$link_root/commands/workflow")" = "$package_root/commands/workflow" ] || fail "unexpected commands symlink target"
[ "$(readlink "$link_root/skills/phase-implementation")" = "$package_root/skills/phase-implementation" ] || fail "unexpected skill symlink target"
assert_contains "$link_output" "$link_root/agents/workflow"

if HOME="$link_home" XDG_CONFIG_HOME="$link_config" "$installer" >"$tmpdir/overwrite-output" 2>"$tmpdir/overwrite-error"; then
  fail "expected existing destinations to prevent installation"
fi
assert_contains "$(cat "$tmpdir/overwrite-error")" "Refusing to overwrite existing path: $link_root/agents/workflow"

copy_config="$tmpdir/copy-config"
copy_home="$tmpdir/copy-home"
HOME="$copy_home" XDG_CONFIG_HOME="$copy_config" "$installer" --copy >"$tmpdir/copy-output"
copy_root="$copy_config/opencode"

[ -d "$copy_root/agents/workflow" ] || fail "expected copied agents workflow directory"
[ -d "$copy_root/commands/workflow" ] || fail "expected copied commands workflow directory"
[ -d "$copy_root/skills/phase-implementation" ] || fail "expected copied phase implementation skill directory"
[ ! -L "$copy_root/agents/workflow" ] || fail "expected copied agents workflow to be independent"
[ ! -L "$copy_root/commands/workflow" ] || fail "expected copied commands workflow to be independent"
[ ! -L "$copy_root/skills/phase-implementation" ] || fail "expected copied phase implementation skill to be independent"
cmp "$package_root/agents/workflow/coordinator.md" "$copy_root/agents/workflow/coordinator.md"
cmp "$package_root/commands/workflow/start-phase.md" "$copy_root/commands/workflow/start-phase.md"
cmp "$package_root/skills/phase-implementation/SKILL.md" "$copy_root/skills/phase-implementation/SKILL.md"

marker="copied-install-test-marker"
printf '\n%s\n' "$marker" >> "$copy_root/skills/phase-implementation/SKILL.md"
if grep -Fq "$marker" "$package_root/skills/phase-implementation/SKILL.md"; then
  fail "expected copied skill changes not to affect the packaged source"
fi

echo "opencode install tests passed"
