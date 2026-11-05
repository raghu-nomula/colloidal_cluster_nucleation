#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TOTAL=3000000

for branch in dr_0.01 dr_0.04; do
    echo "===== $branch ====="
    control="$ROOT/$branch/production_3M_control"
    pidfile="$ROOT/$branch/production_3M.campaign.pid"
    logfile="$ROOT/$branch/production_3M.campaign.log"

    completed=0
    [[ -f "$control/state.txt" ]] && completed=$(cat "$control/state.txt")
    active_segment=$(find "$ROOT/$branch" -maxdepth 1 -type d \
        -name 'production_3M_seg*' | sort | tail -n 1)
    local_cycle=0
    recent_output=0
    if [[ -n "$active_segment" && -f "$active_segment/traj.lammpstrj" ]]; then
        local_cycle=$(awk '/^ITEM: TIMESTEP$/{getline; step=$1} END{print step+0}' \
            "$active_segment/traj.lammpstrj")
        age=$(( $(date +%s) - $(stat -c %Y "$active_segment/traj.lammpstrj") ))
        (( age < 600 )) && recent_output=1
    fi
    observed=$(( completed + local_cycle ))
    percent=$(awk -v done="$observed" -v total="$TOTAL" 'BEGIN {printf "%.2f",100*done/total}')
    echo "Observed progress: $observed / $TOTAL cycles ($percent%)"
    echo "Completed clean segments: $completed cycles"

    if [[ -f "$pidfile" ]]; then
        pid=$(cat "$pidfile")
        if ps -p "$pid" >/dev/null 2>&1; then
            ps -p "$pid" -o pid=,lstart=,etime=,stat=,cmd=
        elif (( recent_output == 1 )); then
            echo "Status: active output detected (PID is outside this process namespace)"
        elif (( completed >= TOTAL )); then
            echo "Status: complete"
        else
            echo "Status: not running (inspect campaign log before resuming)"
        fi
    else
        echo "Status: not launched"
    fi

    if [[ -f "$control/cumulative_metrics.dat" ]]; then
        echo "Latest metrics:"
        awk '!/^#/ && NF {line=$0} END {if(line) print line}' "$control/cumulative_metrics.dat"
    fi
    [[ -f "$logfile" ]] && tail -n 3 "$logfile"
    echo
done

df -h "$ROOT" | awk 'NR==1 || NR==2 {print}'
