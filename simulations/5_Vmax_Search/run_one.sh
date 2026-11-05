#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 5 ]]; then
    echo "Usage: $0 STAGE VMAX CYCLES SEED NSAMP" >&2
    exit 2
fi

STAGE=$1
VMAX=$2
CYCLES=$3
SEED=$4
NSAMP=$5

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SEARCH="$ROOT/5_Vmax_Search"
PARENT="$ROOT/4_Clean_NoSwap_Replication/common/validated_parent_N1000_T1_P18.res"
EXE="$ROOT/4_Clean_NoSwap_Replication/common/mc_npt_phase1"
TAG=$(printf '%s' "$VMAX" | sed 's/^0\.//; s/[^0-9]/_/g')
RUN_DIR="$SEARCH/runs/$STAGE/vmax_${TAG}_seed_${SEED}"

[[ "$STAGE" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "Unsafe stage name" >&2; exit 2; }
[[ "$CYCLES" =~ ^[1-9][0-9]*$ ]] || { echo "Cycles must be positive" >&2; exit 2; }
[[ "$SEED" =~ ^[1-9][0-9]*$ ]] || { echo "Seed must be positive" >&2; exit 2; }
[[ "$NSAMP" =~ ^[1-9][0-9]*$ ]] || { echo "NSAMP must be positive" >&2; exit 2; }
[[ -f "$PARENT" && -x "$EXE" ]] || { echo "Parent or executable missing" >&2; exit 1; }
[[ ! -e "$RUN_DIR" ]] || { echo "Refusing to overwrite $RUN_DIR" >&2; exit 1; }

mkdir -p "$RUN_DIR"
cp "$PARENT" "$RUN_DIR/start_config.res"
cp "$PARENT" "$RUN_DIR/fort.11"
cp "$EXE" "$RUN_DIR/mc_npt"

# A restart supplies dr and vmax; force the controlled search values there.
awk -v vmax="$VMAX" '
NR == 3 {printf "%20.12E %20.12E\n", 0.01, vmax; next}
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
0.01 $VMAX 0.0
ndispl nvol
1000 1
npart temp rho p struc
1000 1.0 1.0 18.0 'sc'
EOF

cp "$RUN_DIR/fort.15" "$RUN_DIR/input_used.in"
cp "$RUN_DIR/fort.25" "$RUN_DIR/model_used.in"

{
    echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "stage=$STAGE"
    echo "cycles=$CYCLES"
    echo "seed=$SEED"
    echo "dr=0.01"
    echo "vmax=$VMAX"
    echo "nsamp=$NSAMP"
    echo "parent=$(readlink -f "$PARENT")"
    echo "parent_sha256=$(sha256sum "$PARENT" | awk '{print $1}')"
    echo "executable_sha256=$(sha256sum "$EXE" | awk '{print $1}')"
} > "$RUN_DIR/manifest.txt"

cd "$RUN_DIR"
./mc_npt > out 2>&1
cp fort.21 final_config.res
cp fort.66 sampled_data.dat
{
    echo "completed_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    tail -n 1 run_metrics.dat
} >> manifest.txt

