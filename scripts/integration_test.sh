#!/usr/bin/env bash
# Run jiggle_version against all sample projects.
# Usage: ./scripts/jiggle_version_matrix.sh
set -Eeuo pipefail

SAMPLES_DIR="${SAMPLES_DIR:-./sample_projects}"
JIGGLE="${JIGGLE:-jiggle_version}"
EXTRA_FLAGS="${EXTRA_FLAGS:---no-color}"   # extra global flags to pass
FAILS=0
SUCCESS=0
run_cmd() {
  local proj="$1"; shift
  local label="$1"; shift
  echo "==> [$(basename "$proj")] $label"
  #
# run safely under `set -e` and capture rc
  local rc=0
  if "$JIGGLE" --project-root "$proj" $EXTRA_FLAGS "$@"; then
    rc=0
  else
    rc=$?
  fi

  # Treat rc >= 100 (user error) as success-for-test
  if (( rc == 0 || rc >= 100 )); then
    SUCCESS=$((SUCCESS+1))
  else
    echo "!!  [$proj] $label FAILED (rc=$rc)"
    FAILS=$((FAILS+1))
  fi
}

clean_project() {
  local proj="$1"
  rm -f "$proj/.jiggle_version.config" || true
}

# Discover projects (dirs directly under SAMPLES_DIR)
mapfile -d '' -t projects < <(find "$SAMPLES_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

if [[ "${#projects[@]}" -eq 0 ]]; then
  echo "No sample projects found under $SAMPLES_DIR"
  exit 1
fi

for proj in "${projects[@]}"; do
  echo "==== Testing project: $proj ===="
  # Expected files: $proj/pyproject.toml etc.
#  if [[ ! -f "$proj/pyproject.toml" ]]; then
#    echo "!!  [$proj] missing pyproject.toml"
#    FAILS=$((FAILS+1))
#    continue
#  fi

  run_cmd "$proj" "print"   print
  run_cmd "$proj" "inspect" inspect
  run_cmd "$proj" "check"   check
  run_cmd "$proj" "hash-all" hash-all
  run_cmd "$proj" "bump --dry-run" bump --dry-run

  clean_project "$proj"
  echo
done

if [[ "$SUCCESS" -gt 0 ]]; then
  echo "Matrix completed with $SUCCESS passing."
fi

if [[ "$FAILS" -gt 0 ]]; then
  echo "Matrix completed with $FAILS failures."
  exit 1
fi

echo "Matrix completed successfully."
