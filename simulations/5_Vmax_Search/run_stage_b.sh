#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VMAX_VALUES=(0.00020 0.00030 0.00050)
SEEDS=(86101 86201 86301)
CYCLES=10000
NSAMP=50

# Three independent seed streams run concurrently. Within each stream the
# Vmax candidates run sequentially from the same immutable parent.
pids=()
for seed in "${SEEDS[@]}"; do
    (
        for vmax in "${VMAX_VALUES[@]}"; do
            echo "[$(date -Is)] seed=$seed starting vmax=$vmax"
            "$HERE/run_one.sh" stage_b "$vmax" "$CYCLES" "$seed" "$NSAMP"
            echo "[$(date -Is)] seed=$seed completed vmax=$vmax"
        done
    ) &
    pids+=("$!")
done

failed=0
for pid in "${pids[@]}"; do
    wait "$pid" || failed=1
done
(( failed == 0 )) || { echo "At least one Stage B worker failed" >&2; exit 1; }

"$HERE/analyze.py" "$HERE/runs/stage_b"
echo "[$(date -Is)] Stage B complete"

