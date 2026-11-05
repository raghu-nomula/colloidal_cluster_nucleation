#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$HERE"
if [[ -d runs/stage_c ]]; then
    echo "runs/stage_c already exists; refusing to overwrite it." >&2
    exit 1
fi
nohup setsid ./run_stage_c.sh > stage_c.log 2>&1 < /dev/null &
echo "$!" > stage_c.pid
echo "Launched Stage C with PID $!; monitor with ./status_stage_c.sh"
