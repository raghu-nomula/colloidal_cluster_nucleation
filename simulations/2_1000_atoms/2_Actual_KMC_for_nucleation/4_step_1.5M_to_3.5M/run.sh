#!/usr/bin/env bash
set -e

ROOT="$(d="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"; while [ ! -d "$d/Source" ] && [ "$d" != / ]; do d="$(dirname "$d")"; done; echo "$d")"  # = simulations/ (folder that holds Source/)
EXE="$ROOT/Source/mc_npt"
BLOCK="$ROOT/Block/block"

START_CONFIG="1.5M_final_config.res"

TEMP=1.0
PRESS=18.0
RHO_LABEL=1.044
SEED=68593

# Fixed-dr pilot production
NEQUIL=0
PROD=2000000
NSAMP=1000

# Paper-like no-swap kinetic MC
DR=0.01
VMAX=0.005
SUCC=0.

NPART=1000
NDISPL=1000
NVOL=1

if [ ! -x "$EXE" ]; then
    echo "ERROR: executable not found or not executable:"
    echo "$EXE"
    exit 1
fi

if [ ! -f "$START_CONFIG" ]; then
    echo "ERROR: starting configuration not found:"
    echo "$START_CONFIG"
    exit 1
fi

rm -f fort.* out traj.lammpstrj sampled_data.dat final_config.res input_used.in model_used.in fort.31 fort.32

cp "$START_CONFIG" fort.11

# Overwrite dr and vmax inside restart file.
# READDAT reads dr/vmax from fort.11 when ibeg = 1,
# so we must force the restart file to contain the desired fixed values.
awk -v dr="$DR" -v vmax="$VMAX" '
NR==3 {
    printf "%20.12E %20.12E\n", dr, vmax
    next
}
{print}
' fort.11 > fort.11.tmp
mv fort.11.tmp fort.11

echo "Restart dr/vmax after overwrite:"
awk 'NR==3{print}' fort.11
cat > fort.25 << 'EOF'
tailco shift
.false. .false.
eps sig mass rc kappa
1. 1. 1. 3.5 6.0
EOF

cat > fort.15 << EOF
ibeg  , nequil  , lmax   nsamp  iseed
1      ${NEQUIL}      ${PROD}   ${NSAMP}    ${SEED}
dr      vmax  succ
${DR}    ${VMAX}  ${SUCC}
ndispl  nvol
${NDISPL}     ${NVOL}
npart temp rho      p     struc
${NPART}  ${TEMP}  ${RHO_LABEL}     ${PRESS}   'sc'
EOF

echo "======================================"
echo "Running 50k fixed-dr production pilot"
echo "======================================"
echo "Start config : $START_CONFIG"
echo "T*           : $TEMP"
echo "p*           : $PRESS"
echo "rho label    : $RHO_LABEL"
echo "seed         : $SEED"
echo "prod cycles  : $PROD"
echo "nsamp        : $NSAMP"
echo "dr fixed     : $DR"
echo "vmax fixed   : $VMAX"
echo "succ         : $SUCC"
echo "ndispl       : $NDISPL"
echo "nvol         : $NVOL"
echo "======================================"

"$EXE" > out

cp fort.21 final_config.res

awk -v T="$TEMP" -v Pin="$PRESS" '
BEGIN {
    print "# mc_cycle inp_T* inp_P* energy_per_particle virial_pressure_estimate density"
}
{
    print $1, T, Pin, $2, $3, $4
}
' fort.66 > sampled_data.dat

cp fort.15 input_used.in
cp fort.25 model_used.in

cat > fort.31 << 'EOF'
data
3
'energy'
'press'
'dens'
EOF

# Remove cycle 0 from block averages if present.
awk '$1 != 0 {print}' fort.66 > fort.32

"$BLOCK" >> out

echo "======================================"
echo "Run complete."
echo "Final sampled line:"
tail -n 1 sampled_data.dat
echo "======================================"
