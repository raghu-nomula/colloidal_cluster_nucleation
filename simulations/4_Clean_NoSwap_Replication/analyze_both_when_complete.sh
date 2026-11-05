#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TOTAL=3000000
PY="${PYTHON:-python3}"  # set PYTHON=/path/to/python if OVITO lives in a conda env

for branch in dr_0.01 dr_0.04; do
    state="$ROOT/$branch/production_3M_control/state.txt"
    [[ -f "$state" ]] || { echo "ERROR: $branch has not started" >&2; exit 1; }
    completed=$(cat "$state")
    if (( completed < TOTAL )); then
        echo "ERROR: $branch incomplete: $completed / $TOTAL" >&2
        exit 1
    fi
done

mkdir -p "$ROOT/analysis/production_3M"
for branch in dr_0.01 dr_0.04; do
    echo "Analyzing $branch ..."
    "$PY" "$ROOT/analysis/analyze_campaign.py" \
        "$ROOT/$branch" production_3M \
        --output "$ROOT/analysis/production_3M/${branch}_structure_timeseries.csv"
done

echo "Analysis complete: $ROOT/analysis/production_3M"

