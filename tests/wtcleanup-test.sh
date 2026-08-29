#!/usr/bin/env bash
set -euo pipefail
export TZ=UTC

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="$repo_root/bin/wtcleanup"
tmpdir="$(mktemp -d)"
root="$tmpdir/review root"
fakebin="$tmpdir/bin"
acli_log="$tmpdir/acli.log"
opencode_log="$tmpdir/opencode.log"

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

assert_not_contains() {
  case "$1" in
    *"$2"*) fail "expected output not to contain: $2" ;;
    *) ;;
  esac
}

line_number() {
  printf '%s\n' "$1" | grep -nF "$2" | head -n 1 | cut -d: -f1
}

mkdir -p "$root" "$fakebin"
root="$(cd "$root" && pwd -P)"
mkdir -p "$root/large REVIEW-cond-7272"
mkdir -p "$root/small-review-COND-7272"
mkdir -p "$root/a-review-ABC-1"
mkdir -p "$root/b-review-ABC-1"
mkdir -p "$root/indeterminate-review-XYZ-9"
mkdir -p "$root/missing-review-LOST-8"
mkdir -p "$root/zeta-review-no-ticket"
mkdir -p "$root/ordinary-COND-999" "$root/container/nested-review-IGN-12"
touch "$root/review-file-COND-11"

# shellcheck disable=SC2016
printf '%s\n' '#!/usr/bin/env bash' \
  'case "$2" in' \
  '  *"large REVIEW-cond-7272") printf "%s\t%s\n" 2048 "$2" ;;' \
  '  *"small-review-COND-7272") printf "%s\t%s\n" 1024 "$2" ;;' \
  '  *"a-review-ABC-1"|*"b-review-ABC-1") printf "%s\t%s\n" 512 "$2" ;;' \
  '  *"indeterminate-review-XYZ-9") printf "%s\t%s\n" 1536 "$2" ;;' \
  '  *"missing-review-LOST-8") printf "%s\t%s\n" 256 "$2" ;;' \
  '  *"zeta-review-no-ticket") printf "%s\t%s\n" 3072 "$2" ;;' \
  '  *"configured-review-ABC-12") printf "%s\t%s\n" 128 "$2" ;;' \
  '  *"no-key-review") printf "%s\t%s\n" 64 "$2" ;;' \
  '  *) exit 1 ;;' \
  'esac' > "$fakebin/du"
chmod +x "$fakebin/du"

printf '%s\n' '#!/usr/bin/env bash' 'printf "%s\n" Darwin' > "$fakebin/uname"
chmod +x "$fakebin/uname"

printf '%s\n' '#!/usr/bin/env bash' 'printf "%s\n" 2026-01-02' > "$fakebin/stat"
chmod +x "$fakebin/stat"

# shellcheck disable=SC2016
printf '%s\n' '#!/usr/bin/env bash' \
  'printf "%s\n" "$*" >> "$ACLI_LOG"' \
  'if [ "${ACLI_FAIL:-0}" -eq 1 ]; then echo "authentication failed" >&2; exit 1; fi' \
  'printf "%s\n" "${ACLI_RESPONSE:-[]}"' > "$fakebin/acli"
chmod +x "$fakebin/acli"

# shellcheck disable=SC2016
printf '%s\n' '#!/usr/bin/env bash' \
  'printf "%s\n" "$3" >> "$OPENCODE_LOG"' \
  'case "${OPENCODE_MODE:-success}" in' \
  '  unavailable) echo "service unavailable" >&2; exit 1 ;;' \
  '  malformed) printf "%s\n" "not json"; exit 0 ;;' \
  'esac' \
  'case "$3" in' \
  '  *"cursor=older-page"*) printf "%s\n" "$OPENCODE_PAGE_TWO" ;;' \
  '  *) printf "%s\n" "$OPENCODE_PAGE_ONE" ;;' \
  'esac' > "$fakebin/opencode2"
chmod +x "$fakebin/opencode2"

large_directory="$root/large REVIEW-cond-7272"
small_directory="$root/small-review-COND-7272"
session_page_one="$(jq -cn \
  --arg large "$large_directory" \
  --arg root "$root" \
  '{data: [
    {location: {directory: $large}, time: {updated: 1704110400000}},
    {location: {directory: $large}, time: {updated: 1711972800000}},
    {location: {directory: ($large + "-similar")}, time: {updated: 1735732800000}},
    {location: {directory: $root}, time: {updated: 1738411200000}},
    {location: {directory: ($large + "/child")}, time: {updated: 1740830400000}}
  ], cursor: {next: "older-page"}}')"
session_page_two="$(jq -cn --arg small "$small_directory" \
  '{data: [{location: {directory: $small}, time: {updated: 1719835200000}}], cursor: {next: null}}')"
export OPENCODE_LOG="$opencode_log"
export OPENCODE_PAGE_ONE="$session_page_one"
export OPENCODE_PAGE_TWO="$session_page_two"

success_response='[{"key":"COND-7272","fields":{"status":{"name":"Done","statusCategory":{"key":"done"}}}},{"key":"ABC-1","fields":{"status":{"name":"To Do","statusCategory":{"key":"new"}}}},{"key":"XYZ-9","fields":{"status":{"name":"In Progress","statusCategory":{"key":"indeterminate"}}}}]'
output="$(ACLI_LOG="$acli_log" ACLI_RESPONSE="$success_response" PATH="$fakebin:$PATH" JIRA_SITE="jira.example.test" "$script" "$root")"

assert_contains "$output" 'JIRA         | STATE      | STATUS             | SIZE     | CHECKED OUT  | LAST REVIEW'
assert_contains "$output" 'COND-7272    | cleanup    | Done'
assert_contains "$output" 'ABC-1        | keep       | To Do'
assert_contains "$output" 'XYZ-9        | keep       | In Progress'
assert_contains "$output" 'LOST-8       | unknown    | Not found'
assert_contains "$output" '-            | no ticket  | No Jira key'
assert_contains "$output" 'Review directories: 7'
assert_contains "$output" 'cleanup: 2'
assert_contains "$output" 'keep: 3'
assert_contains "$output" 'unknown: 1'
assert_contains "$output" 'no ticket: 1'
assert_contains "$output" 'Potential space reclaimed: 3.0M'
assert_contains "$output" 'large REVIEW-cond-7272 | https://jira.example.test/browse/COND-7272'
assert_contains "$output" 'small-review-COND-7272 | https://jira.example.test/browse/COND-7272'
assert_not_contains "$output" 'ordinary-COND-999'
assert_not_contains "$output" 'nested-review-IGN-12'
assert_not_contains "$output" 'review-file-COND-11'

large_row="$(printf '%s\n' "$output" | grep -F 'large REVIEW-cond-7272')"
small_row="$(printf '%s\n' "$output" | grep -F 'small-review-COND-7272')"
a_row="$(printf '%s\n' "$output" | grep -F 'a-review-ABC-1')"
assert_contains "$large_row" '2024-04-01'
assert_not_contains "$large_row" '2025-01-01'
assert_contains "$small_row" '2024-07-01'
assert_contains "$a_row" '| -            | a-review-ABC-1'
[ "$(wc -l < "$opencode_log" | tr -d ' ')" -eq 2 ] || fail "expected later OpenCode session pages to be read"
assert_contains "$(cat "$opencode_log")" 'cursor=older-page'

[ "$(wc -l < "$acli_log" | tr -d ' ')" -eq 1 ] || fail "expected one batched ACLI query"
acli_args="$(cat "$acli_log")"
assert_contains "$acli_args" 'COND-7272'
assert_contains "$acli_args" 'ABC-1'
assert_contains "$acli_args" 'XYZ-9'
assert_contains "$acli_args" 'LOST-8'
assert_contains "$acli_args" 'key,status,summary'
[ "$(printf '%s\n' "$acli_args" | grep -oF 'COND-7272' | wc -l | tr -d ' ')" -eq 1 ] || fail "expected duplicate Jira keys to be queried once"

large_line="$(line_number "$output" 'large REVIEW-cond-7272')"
small_line="$(line_number "$output" 'small-review-COND-7272')"
indeterminate_line="$(line_number "$output" 'indeterminate-review-XYZ-9')"
a_line="$(line_number "$output" 'a-review-ABC-1')"
b_line="$(line_number "$output" 'b-review-ABC-1')"
missing_line="$(line_number "$output" 'missing-review-LOST-8')"
zeta_line="$(line_number "$output" 'zeta-review-no-ticket')"

[ "$large_line" -lt "$small_line" ] || fail "expected cleanup rows sorted by size"
[ "$small_line" -lt "$indeterminate_line" ] || fail "expected cleanup group first"
[ "$indeterminate_line" -lt "$a_line" ] || fail "expected keep rows sorted by size"
[ "$a_line" -lt "$b_line" ] || fail "expected basename tie-breaker"
[ "$b_line" -lt "$missing_line" ] || fail "expected unknown after keep"
[ "$missing_line" -lt "$zeta_line" ] || fail "expected no-ticket rows last"

printf '%s\n' '#!/usr/bin/env bash' 'printf "%s\n" Linux' > "$fakebin/uname"
fallback_output="$(ACLI_LOG="$acli_log" ACLI_RESPONSE="$success_response" PATH="$fakebin:$PATH" "$script" "$root")"
assert_contains "$fallback_output" 'COND-7272    | cleanup    | Done               | 2.0M     | -            | 2024-04-01'

empty_root="$tmpdir/empty root"
mkdir -p "$empty_root"
rm -f "$acli_log"
empty_output="$(ACLI_LOG="$acli_log" PATH="$fakebin:$PATH" "$script" "$empty_root")"
assert_contains "$empty_output" 'No review directories found.'
[ ! -e "$acli_log" ] || fail "expected ACLI to be skipped for an empty root"

no_key_root="$tmpdir/no key root"
mkdir -p "$no_key_root/no-key-review"
rm -f "$acli_log"
no_key_output="$(ACLI_LOG="$acli_log" PATH="$fakebin:$PATH" "$script" "$no_key_root")"
assert_contains "$no_key_output" 'no ticket  | No Jira key'
[ ! -e "$acli_log" ] || fail "expected ACLI to be skipped when no Jira keys exist"

set +e
failure_output="$(ACLI_LOG="$acli_log" ACLI_FAIL=1 PATH="$fakebin:$PATH" "$script" "$root" 2>"$tmpdir/query-error")"
failure_status=$?
set -e
[ "$failure_status" -ne 0 ] || fail "expected ACLI failure to return nonzero"
assert_contains "$failure_output" 'COND-7272    | unknown    | Query failed'
assert_contains "$failure_output" '-            | no ticket  | No Jira key'
assert_contains "$(cat "$tmpdir/query-error")" 'Jira query failed'

set +e
malformed_output="$(ACLI_LOG="$acli_log" ACLI_RESPONSE='not json' PATH="$fakebin:$PATH" "$script" "$root" 2>"$tmpdir/malformed-error")"
malformed_status=$?
set -e
[ "$malformed_status" -ne 0 ] || fail "expected malformed JSON to return nonzero"
assert_contains "$malformed_output" 'LOST-8       | unknown    | Query failed'
assert_contains "$(cat "$tmpdir/malformed-error")" 'malformed JSON'

set +e
history_unavailable_output="$(ACLI_LOG="$acli_log" ACLI_RESPONSE="$success_response" OPENCODE_MODE=unavailable PATH="$fakebin:$PATH" "$script" "$root" 2>"$tmpdir/history-unavailable-error")"
history_unavailable_status=$?
set -e
[ "$history_unavailable_status" -eq 0 ] || fail "expected unavailable session history not to fail"
assert_contains "$history_unavailable_output" 'COND-7272    | cleanup    | Done               | 2.0M     | -            | -'
[ "$(grep -cF 'OpenCode session history unavailable' "$tmpdir/history-unavailable-error")" -eq 1 ] || fail "expected one unavailable-history warning"

set +e
history_malformed_output="$(ACLI_LOG="$acli_log" ACLI_RESPONSE="$success_response" OPENCODE_MODE=malformed PATH="$fakebin:$PATH" "$script" "$root" 2>"$tmpdir/history-malformed-error")"
history_malformed_status=$?
set -e
[ "$history_malformed_status" -eq 0 ] || fail "expected malformed session history not to fail"
assert_contains "$history_malformed_output" 'COND-7272    | cleanup    | Done               | 2.0M     | -            | -'
[ "$(grep -cF 'OpenCode session history unavailable' "$tmpdir/history-malformed-error")" -eq 1 ] || fail "expected one malformed-history warning"

config_home="$tmpdir/config"
configured_root="$tmpdir/configured root"
legacy_root="$tmpdir/legacy root"
mkdir -p "$config_home/dev-toolbox" "$configured_root/configured-review-ABC-12" "$legacy_root/legacy-review-IGN-1"
printf 'export WTDEV_ROOT=%q\nexport WTMUX_ROOT=%q\n' "$configured_root" "$legacy_root" > "$config_home/dev-toolbox/wt.env"
config_response='[{"key":"ABC-12","fields":{"status":{"name":"Done","statusCategory":{"key":"done"}}}}]'
config_output="$(HOME="$tmpdir/home" XDG_CONFIG_HOME="$config_home" ACLI_LOG="$acli_log" ACLI_RESPONSE="$config_response" PATH="$fakebin:$PATH" "$script")"
assert_contains "$config_output" 'configured-review-ABC-12'
assert_not_contains "$config_output" 'legacy-review-IGN-1'

if PATH="$fakebin:$PATH" "$script" "$tmpdir/missing root" >/dev/null 2>&1; then
  fail "expected invalid root to fail"
fi

echo "wtcleanup tests passed"
