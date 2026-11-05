#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LAUNCH="$ROOT/common/launch_campaign_nohup.sh"

for branch in dr_0.01 dr_0.04; do
    if [[ -e "$ROOT/$branch/production_3M_control" ]]; then
        echo "ERROR: production_3M already exists for $branch" >&2
        echo "Use production_status.sh; do not create a second campaign." >&2
        exit 1
    fi
done

AVAILABLE_KB=$(df -Pk "$ROOT" | awk 'NR==2 {print $4}')
if (( AVAILABLE_KB < 5 * 1024 * 1024 )); then
    echo "ERROR: less than 5 GiB free disk space" >&2
    exit 1
fi

"$LAUNCH" dr_0.01 production_3M 3000000 250000 91001 1000
"$LAUNCH" dr_0.04 production_3M 3000000 250000 94001 1000

echo
echo "Both campaigns were submitted. Check them with:"
echo "  $ROOT/production_status.sh"
echo
echo "Closing this terminal will not stop them. Suspending the computer pauses"
echo "CPU execution; the processes continue after wake-up."

