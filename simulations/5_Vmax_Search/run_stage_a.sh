#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VMAX_VALUES=(0.00020 0.00030 0.00040 0.00050 0.00065 0.00080 0.00100)
CYCLES=5000
SEED=85001
NSAMP=100

for vmax in "${VMAX_VALUES[@]}"; do
    echo "[$(date -Is)] starting vmax=$vmax"
    "$HERE/run_one.sh" stage_a "$vmax" "$CYCLES" "$SEED" "$NSAMP"
    echo "[$(date -Is)] completed vmax=$vmax"
done

"$HERE/analyze.py" "$HERE/runs/stage_a"
echo "[$(date -Is)] Stage A complete"

