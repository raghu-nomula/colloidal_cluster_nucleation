#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$HERE"
if [[ -f stage_b.pid ]] && kill -0 "$(cat stage_b.pid)" 2>/dev/null; then
    echo "Stage B: RUNNING (PID $(cat stage_b.pid))"
else
    echo "Stage B: not running"
fi
created=$(find runs/stage_b -mindepth 2 -maxdepth 2 -name manifest.txt 2>/dev/null | wc -l)
completed=$(find runs/stage_b -mindepth 2 -maxdepth 2 -name manifest.txt -exec grep -l '^completed_utc=' {} \; 2>/dev/null | wc -l)
echo "Runs created: $created / 9"
echo "Runs completed: $completed / 9"
[[ -f stage_b.log ]] && { echo; tail -n 15 stage_b.log; }
