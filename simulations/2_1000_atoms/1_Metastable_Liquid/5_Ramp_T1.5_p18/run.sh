#!/usr/bin/env bash
set -e

# Usage:
# ./run.sh START_CONFIG TEMP PRESSURE RHO_LABEL SEED
#
# Example:
# ./run.sh liquid_N1000_T2_P5.res 2.0 10.0 0.60 88402

ROOT="$(d="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"; while [ ! -d "$d/Source" ] && [ "$d" != / ]; do d="$(dirname "$d")"; done; echo "$d")"  # = simulations/ (folder that holds Source/)
EXE="$ROOT/Source/mc_npt"
BLOCK="$ROOT/Block/block"

START_CONFIG="${1:?ERROR: give starting structure file}"
TEMP="${2:?ERROR: give temperature T*}"
PRESS="${3:?ERROR: give pressure p*}"
RHO_LABEL="${4:?ERROR: give rho label}"
SEED="${5:?ERROR: give random seed}"

# Preparation-ramp parameters
NEQUIL=3500
PROD=7000
NSAMP=250

DR=0.12
VMAX=0.03
SUCC=30.

NPART=1000
NDISPL=1000
NVOL=5

if [ ! -f "$START_CONFIG" ]; then
    echo "ERROR: starting configuration not found:"
    echo "$START_CONFIG"
    exit 1
fi

rm -f fort.* out traj.lammpstrj sampled_data.dat final_config.res input_used.in model_used.in start_config.res

cp "$START_CONFIG" start_config.res
cp "$START_CONFIG" fort.11

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

echo "Running ramp:"
echo "  START_CONFIG = $START_CONFIG"
echo "  TEMP         = $TEMP"
echo "  PRESS        = $PRESS"
echo "  RHO_LABEL    = $RHO_LABEL"
echo "  SEED         = $SEED"

"$EXE" > out

cp fort.21 final_config.res

#cp fort.66 sampled_data.dat
{
    echo "# mc_cycle energy_per_particle virial_pressure_estimate density"
    cat fort.66
} > sampled_data.dat

cp fort.15 input_used.in
cp fort.25 model_used.in

cat > fort.31 << 'EOF'
data
3
'energy'
'press'
'dens'
EOF

# exclude cycle 0 from block averages if present
tail -n +2 fort.66 > fort.32
"$BLOCK" >> out

echo "Run complete."
echo "Final sampled line:"
tail -n 1 sampled_data.dat
echo
echo "Outputs:"
echo "  out"
echo "  sampled_data.dat"
echo "  final_config.res"
echo "  traj.lammpstrj"
echo "  start_config.res"
