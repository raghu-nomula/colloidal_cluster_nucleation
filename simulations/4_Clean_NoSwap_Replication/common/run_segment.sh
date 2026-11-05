#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 || $# -gt 7 ]]; then
    echo "Usage: $0 BRANCH RUN_NAME CYCLES SEED [VMAX [START_CONFIG [NSAMP]]]" >&2
    exit 2
fi

BRANCH=$1
RUN_NAME=$2
CYCLES=$3
SEED=$4
VMAX=${5:-0.001}

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
COMMON="$ROOT/common"
CASE_DIR="$ROOT/$BRANCH"
RUN_DIR="$CASE_DIR/$RUN_NAME"
START_SOURCE=${6:-$COMMON/validated_parent_N1000_T1_P18.res}
NSAMP=${7:-100}

case "$BRANCH" in
    dr_0.01) DR=0.01 ;;
    dr_0.04) DR=0.04 ;;
    *) echo "ERROR: branch must be dr_0.01 or dr_0.04" >&2; exit 2 ;;
esac

[[ "$RUN_NAME" =~ ^[A-Za-z0-9._-]+$ ]] || {
    echo "ERROR: unsafe run name" >&2
    exit 2
}

if [[ -e "$RUN_DIR" ]]; then
    echo "ERROR: run directory already exists: $RUN_DIR" >&2
    exit 1
fi

mkdir -p "$RUN_DIR"
if [[ ! -f "$START_SOURCE" ]]; then
    echo "ERROR: starting configuration not found: $START_SOURCE" >&2
    exit 1
fi
cp "$START_SOURCE" "$RUN_DIR/start_config.res"
cp "$COMMON/mc_npt_phase1" "$RUN_DIR/mc_npt"
cp "$RUN_DIR/start_config.res" "$RUN_DIR/fort.11"

# READDAT takes dr/vmax from a restart file when ibeg=1.
awk -v dr="$DR" -v vmax="$VMAX" '
NR == 3 {printf "%20.12E %20.12E\n", dr, vmax; next}
{print}
' "$RUN_DIR/fort.11" > "$RUN_DIR/fort.11.tmp"
mv "$RUN_DIR/fort.11.tmp" "$RUN_DIR/fort.11"

cat > "$RUN_DIR/fort.25" <<EOF
tailco shift
.false. .false.
eps sig mass rc kappa
1.0 1.0 1.0 3.5 6.0
EOF

cat > "$RUN_DIR/fort.15" <<EOF
ibeg nequil prod nsamp iseed
1 0 $CYCLES $NSAMP $SEED
dr vmax succ
$DR $VMAX 0.0
ndispl nvol
1000 1
npart temp rho p struc
1000 1.0 1.0 18.0 'sc'
EOF

{
    echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "host=$(hostname)"
    echo "branch=$BRANCH"
    echo "run_name=$RUN_NAME"
    echo "cycles=$CYCLES"
    echo "seed=$SEED"
    echo "dr=$DR"
    echo "vmax=$VMAX"
    echo "sampling_interval=$NSAMP"
    echo "start_source=$(readlink -f "$START_SOURCE")"
    echo "start_sha256=$(sha256sum "$RUN_DIR/start_config.res" | awk '{print $1}')"
    echo "executable_sha256=$(sha256sum "$RUN_DIR/mc_npt" | awk '{print $1}')"
} > "$RUN_DIR/manifest.txt"

cp "$RUN_DIR/fort.15" "$RUN_DIR/input_used.in"
cp "$RUN_DIR/fort.25" "$RUN_DIR/model_used.in"

cd "$RUN_DIR"
./mc_npt > out 2>&1
cp fort.21 final_config.res
cp fort.66 sampled_data.dat

{
    echo "completed_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    tail -n 1 run_metrics.dat
} >> manifest.txt

echo "Completed: $RUN_DIR"
