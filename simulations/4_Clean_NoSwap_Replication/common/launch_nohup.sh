#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 || $# -gt 5 ]]; then
    echo "Usage: $0 BRANCH RUN_NAME CYCLES SEED [VMAX]" >&2
    exit 2
fi

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BRANCH=$1
RUN_NAME=$2
LOG="$HERE/../$BRANCH/${RUN_NAME}.launch.log"
PIDFILE="$HERE/../$BRANCH/${RUN_NAME}.pid"

nohup "$HERE/run_segment.sh" "$@" > "$LOG" 2>&1 &
PID=$!
echo "$PID" > "$PIDFILE"
echo "Started PID $PID"
echo "Log: $LOG"
echo "PID file: $PIDFILE"

