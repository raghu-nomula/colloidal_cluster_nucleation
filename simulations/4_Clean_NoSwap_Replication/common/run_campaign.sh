#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 6 ]]; then
    echo "Usage: $0 BRANCH CAMPAIGN TOTAL_CYCLES SEGMENT_CYCLES SEED_BASE NSAMP" >&2
    exit 2
fi

BRANCH=$1
CAMPAIGN=$2
TOTAL=$3
SEGMENT=$4
SEED_BASE=$5
NSAMP=$6

[[ "$CAMPAIGN" =~ ^[A-Za-z0-9._-]+$ ]] || {
    echo "ERROR: unsafe campaign name" >&2
    exit 2
}
(( TOTAL > 0 && SEGMENT > 0 && NSAMP > 0 )) || {
    echo "ERROR: cycle counts and NSAMP must be positive" >&2
    exit 2
}

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
CONTROL="$ROOT/$BRANCH/${CAMPAIGN}_control"
STATE="$CONTROL/state.txt"
COMBINED="$CONTROL/cumulative_metrics.dat"
VMAX=0.0005

mkdir -p "$CONTROL"
if [[ ! -f "$STATE" ]]; then
    echo 0 > "$STATE"
    cat > "$COMBINED" <<EOF
# cumulative_cycle energy_per_particle density eta imposed_pressure p_continuous attempts accepted acceptance volume_attempts volume_accepted volume_acceptance
EOF
    {
        echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "branch=$BRANCH"
        echo "campaign=$CAMPAIGN"
        echo "total_cycles=$TOTAL"
        echo "segment_cycles=$SEGMENT"
        echo "seed_base=$SEED_BASE"
        echo "sampling_interval=$NSAMP"
        echo "vmax=$VMAX"
    } > "$CONTROL/campaign_manifest.txt"
fi

COMPLETED=$(cat "$STATE")
if (( COMPLETED >= TOTAL )); then
    echo "Campaign already complete: $COMPLETED / $TOTAL cycles"
    exit 0
fi

PARENT="$ROOT/common/validated_parent_N1000_T1_P18.res"
if (( COMPLETED > 0 )); then
    LAST_INDEX=$(( (COMPLETED + SEGMENT - 1) / SEGMENT ))
    LAST_NAME=$(printf '%s_seg%03d' "$CAMPAIGN" "$LAST_INDEX")
    PARENT="$ROOT/$BRANCH/$LAST_NAME/final_config.res"
    [[ -f "$PARENT" ]] || {
        echo "ERROR: resume parent missing: $PARENT" >&2
        exit 1
    }
fi

while (( COMPLETED < TOTAL )); do
    INDEX=$(( COMPLETED / SEGMENT + 1 ))
    REMAINING=$(( TOTAL - COMPLETED ))
    CYCLES=$SEGMENT
    (( REMAINING < SEGMENT )) && CYCLES=$REMAINING
    RUN_NAME=$(printf '%s_seg%03d' "$CAMPAIGN" "$INDEX")
    SEED=$(( SEED_BASE + INDEX - 1 ))

    "$HERE/run_segment.sh" "$BRANCH" "$RUN_NAME" "$CYCLES" "$SEED" \
        "$VMAX" "$PARENT" "$NSAMP"

    RUN_DIR="$ROOT/$BRANCH/$RUN_NAME"
    OFFSET=$COMPLETED
    awk -v offset="$OFFSET" \
        '!/^#/ && NF && !(offset > 0 && $1 == 0) { $1=$1+offset; print }' \
        "$RUN_DIR/run_metrics.dat" >> "$COMBINED"

    COMPLETED=$(( COMPLETED + CYCLES ))
    echo "$COMPLETED" > "$STATE.tmp"
    mv "$STATE.tmp" "$STATE"
    PARENT="$RUN_DIR/final_config.res"
    echo "Campaign progress: $COMPLETED / $TOTAL cycles"
done

echo "completed_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CONTROL/campaign_manifest.txt"
echo "Campaign complete: $BRANCH $CAMPAIGN"
