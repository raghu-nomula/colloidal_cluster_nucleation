#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 6 ]]; then
    echo "Usage: $0 BRANCH CAMPAIGN TOTAL_CYCLES SEGMENT_CYCLES SEED_BASE NSAMP" >&2
    exit 2
fi

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/.." && pwd)
BRANCH=$1
CAMPAIGN=$2
LOG="$ROOT/$BRANCH/${CAMPAIGN}.campaign.log"
PIDFILE="$ROOT/$BRANCH/${CAMPAIGN}.campaign.pid"

nohup "$HERE/run_campaign.sh" "$@" > "$LOG" 2>&1 &
PID=$!
echo "$PID" > "$PIDFILE"
echo "Started campaign PID $PID"
echo "Log: $LOG"
echo "PID file: $PIDFILE"

