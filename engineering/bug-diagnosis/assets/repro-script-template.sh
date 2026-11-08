#!/usr/bin/env bash
# Reproduction signal template. Exit 0 = bug absent (good), 1 = bug present (bad),
# 125 = this state cannot be tested (git bisect skips it).
# Usable directly with: git bisect run ./repro.sh
#
# Fill in the three marked sections. Read every credential from the environment;
# never write one into this file or its output.
set -u

TAG="[repro]"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

# --- 1. Build / prepare (exit 125 if the state cannot be built) ----------------
# Example: python -m pip install -q -e . >/dev/null 2>&1 || exit 125
:

# --- 2. Pin sources of variation ---------------------------------------------
export TZ=UTC
export LANG=C.UTF-8
export PYTHONHASHSEED=0
# export APP_CLOCK_FROZEN_AT="2026-01-01T00:00:00Z"
# export APP_RANDOM_SEED=1234

# --- 3. Trigger and assert the reported symptom ------------------------------
# Replace with the narrowest command that reaches the bug. Capture output to a file
# and assert on the specific symptom, not merely on the exit status.
OUTPUT_FILE="$WORKDIR/out.txt"
if ! echo "replace me with the trigger command" >"$OUTPUT_FILE" 2>&1; then
  echo "$TAG trigger command failed to run" >&2
  exit 125
fi

# Example assertion: the computed total must equal the reference total.
if grep -q "total mismatch" "$OUTPUT_FILE"; then
  echo "$TAG BAD: symptom present"
  exit 1
fi

echo "$TAG GOOD: symptom absent"
exit 0
