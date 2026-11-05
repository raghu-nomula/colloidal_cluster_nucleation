#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$HERE"
if [[ -d runs/stage_b ]]; then
    echo "runs/stage_b already exists; refusing to overwrite it." >&2
    exit 1
fi
nohup setsid ./run_stage_b.sh > stage_b.log 2>&1 < /dev/null &
echo "$!" > stage_b.pid
echo "Launched Stage B with PID $!; monitor with ./status_stage_b.sh"

