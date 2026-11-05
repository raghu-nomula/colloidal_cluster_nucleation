#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$HERE"
TOTAL=15
if [[ -f stage_c.pid ]] && kill -0 "$(cat stage_c.pid)" 2>/dev/null; then
    echo "Stage C: RUNNING (PID $(cat stage_c.pid))"
else
    echo "Stage C: not running"
fi
created=$(find runs/stage_c -mindepth 2 -maxdepth 2 -name manifest.txt 2>/dev/null | wc -l)
completed=$(find runs/stage_c -mindepth 2 -maxdepth 2 -name manifest.txt -exec grep -l '^completed_utc=' {} \; 2>/dev/null | wc -l)
echo "Runs created: $created / $TOTAL"
echo "Runs completed: $completed / $TOTAL"
[[ -f runs/stage_c/vmax_summary.csv ]] && echo "Summary: runs/stage_c/vmax_summary.csv"
[[ -f runs/stage_c/vmax_aggregate_summary.csv ]] && echo "Aggregate: runs/stage_c/vmax_aggregate_summary.csv"
[[ -f stage_c.log ]] && { echo; tail -n 20 stage_c.log; }
