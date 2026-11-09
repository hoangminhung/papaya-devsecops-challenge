#!/usr/bin/env bash
# Run every local check on examples/. Nothing here contacts AWS, GitHub settings or any
# other live system. Tools that are not installed are SKIPPED with a message, never
# reported as passed. Set ACTIONLINT / ZIZMOR to the binaries if they are not on PATH.
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")" || exit 1

ACTIONLINT="${ACTIONLINT:-actionlint}"
ZIZMOR="${ZIZMOR:-zizmor}"
fail=0
skipped=()

section() { printf '\n=== %s ===\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }
run() { "$@" || { echo "FAILED: $*"; fail=1; }; }

section "tool versions"
python3 --version
python3 -c 'from importlib.metadata import version as v; print("jsonschema", v("jsonschema"), "| PyYAML", v("PyYAML"))'
for t in jq yamllint shellcheck "$ACTIONLINT" "$ZIZMOR"; do
  if have "$t"; then printf '%s: %s\n' "$(basename "$t")" "$("$t" --version 2>&1 | head -1)"
  else printf '%s: not installed\n' "$(basename "$t")"; fi
done

section "JSON syntax (jq)"
if have jq; then
  while IFS= read -r f; do run jq empty "$f"; done < <(find . -name '*.json' -not -path './*/node_modules/*' | sort)
  echo "checked $(find . -name '*.json' -not -path './*/node_modules/*' | wc -l) files"
else skipped+=("jq"); echo "SKIPPED: jq not installed"; fi

section "YAML style (yamllint)"
if have yamllint; then
  run yamllint -d '{extends: default, rules: {line-length: {max: 120}, document-start: disable, truthy: {check-keys: false}, comments: {min-spaces-from-content: 1}}}' github/workflows
else skipped+=("yamllint"); echo "SKIPPED: yamllint not installed"; fi

section "GitHub Actions (actionlint)"
if have "$ACTIONLINT"; then
  # actionlint 1.7.12 (latest, March 2026) predates GitHub's same-repository `$/` syntax for
  # reusable workflows (GitHub docs, workflow-syntax, jobs.<job_id>.uses). Only that message
  # is ignored.
  SC=(); have shellcheck && SC=(-shellcheck "$(command -v shellcheck)")
  run "$ACTIONLINT" "${SC[@]}" -ignore 'reusable workflow call "\$/' github/workflows/*.yml
  echo "actionlint done"
else skipped+=("actionlint"); echo "SKIPPED: actionlint not installed"; fi

section "GitHub Actions security (zizmor, offline, auditor persona)"
if have "$ZIZMOR"; then
  run "$ZIZMOR" --offline --no-progress --persona=auditor github/workflows/*.yml
else skipped+=("zizmor"); echo "SKIPPED: zizmor not installed"; fi

section "unit tests (python3 -m unittest)"
run python3 -W error::ResourceWarning -m unittest discover -s tests -v

section "result"
if [ ${#skipped[@]} -gt 0 ]; then echo "SKIPPED (not verified): ${skipped[*]}"; fi
if [ "$fail" -ne 0 ]; then echo "RESULT: FAILED"; exit 1; fi
echo "RESULT: all executed checks passed"
