#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$HERE"

if [[ -f stage_a.pid ]] && kill -0 "$(cat stage_a.pid)" 2>/dev/null; then
    echo "Stage A is already running with PID $(cat stage_a.pid)" >&2
    exit 1
fi
if [[ -d runs/stage_a ]]; then
    echo "runs/stage_a already exists; refusing to overwrite it." >&2
    exit 1
fi

nohup setsid ./run_stage_a.sh > stage_a.log 2>&1 < /dev/null &
pid=$!
echo "$pid" > stage_a.pid
echo "Launched Stage A with PID $pid"
echo "Monitor with: ./status.sh"

