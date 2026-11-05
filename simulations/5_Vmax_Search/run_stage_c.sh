#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VMAX_VALUES=(0.00040 0.00050 0.00060 0.00065 0.00070)
SEEDS=(87101 87201 87301)
CYCLES=20000
NSAMP=25
STAGE=stage_c
TOTAL=$(( ${#VMAX_VALUES[@]} * ${#SEEDS[@]} ))

# Three independent seed streams run concurrently. Within each stream the
# Vmax candidates run sequentially from the same immutable parent. This avoids
# chaining candidate endpoints while still letting the campaign run unattended.
pids=()
for seed in "${SEEDS[@]}"; do
    (
        for vmax in "${VMAX_VALUES[@]}"; do
            echo "[$(date -Is)] seed=$seed starting vmax=$vmax cycles=$CYCLES nsamp=$NSAMP"
            "$HERE/run_one.sh" "$STAGE" "$vmax" "$CYCLES" "$seed" "$NSAMP"
            echo "[$(date -Is)] seed=$seed completed vmax=$vmax"
        done
    ) &
    pids+=("$!")
done

failed=0
for pid in "${pids[@]}"; do
    wait "$pid" || failed=1
done
(( failed == 0 )) || { echo "At least one Stage C worker failed" >&2; exit 1; }

# Produce the same basic summary table for bookkeeping. Deeper IACT/minimum
# analysis is intentionally left for a later analysis pass.
"$HERE/analyze.py" "$HERE/runs/$STAGE"
echo "[$(date -Is)] Stage C complete; completed $TOTAL / $TOTAL runs"
