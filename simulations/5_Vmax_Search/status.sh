#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$HERE"

if [[ -f stage_a.pid ]]; then
    pid=$(cat stage_a.pid)
    if kill -0 "$pid" 2>/dev/null; then
        echo "Stage A process: RUNNING (PID $pid)"
    else
        echo "Stage A process: not running (recorded PID $pid)"
    fi
else
    echo "Stage A PID file: absent"
fi

completed=$(find runs/stage_a -mindepth 2 -maxdepth 2 -name manifest.txt -exec grep -l '^completed_utc=' {} \; 2>/dev/null | wc -l)
created=$(find runs/stage_a -mindepth 2 -maxdepth 2 -name manifest.txt 2>/dev/null | wc -l)
echo "Runs created: $created / 7"
echo "Runs completed: $completed / 7"

if [[ -f stage_a.log ]]; then
    echo
    echo "Recent log:"
    tail -n 12 stage_a.log
fi

active_metrics=$(find runs/stage_a -name run_metrics.dat -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -n 1 | cut -d' ' -f2-)
if [[ -n "${active_metrics:-}" ]]; then
    echo
    echo "Latest metrics ($active_metrics):"
    tail -n 1 "$active_metrics"
fi

