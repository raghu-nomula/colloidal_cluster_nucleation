#!/usr/bin/env bash
set -e

ROOT="$(d="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"; while [ ! -d "$d/Source" ] && [ "$d" != / ]; do d="$(dirname "$d")"; done; echo "$d")"  # = simulations/ (folder that holds Source/)
EXE="$ROOT/Source/mc_npt"

TEMP=1.0
PRESS=18.0
RHO_LABEL=1.0
SEED=91001

# Only generate/check crystal frame
NEQUIL=0
PROD=100
NSAMP=1

# No real motion; keep the fcc frame
DR=0.0
VMAX=0.0
SUCC=0.

NPART=864
NDISPL=864
NVOL=1

rm -f fort.* out traj.lammpstrj sampled_data.dat final_config.res input_used.in model_used.in

cat > fort.25 << 'EOF'
tailco shift
.false. .false.
eps sig mass rc kappa
1. 1. 1. 3.5 6.0
EOF

cat > fort.15 << EOF
ibeg  , nequil  , lmax   nsamp  iseed
0      ${NEQUIL}      ${PROD}   ${NSAMP}    ${SEED}
dr      vmax  succ
${DR}    ${VMAX}  ${SUCC}
ndispl  nvol
${NDISPL}     ${NVOL}
npart temp rho      p     struc
${NPART}  ${TEMP}  ${RHO_LABEL}     ${PRESS}   'fcc'
EOF

echo "Running q6 positive control: fcc crystal"
"$EXE" > out

cp fort.21 final_config.res

awk -v T="$TEMP" -v Pin="$PRESS" '
BEGIN {
    print "# mc_cycle input_Tstar input_Pstar energy_per_particle continuous_virial_pressure_estimate density"
}
{
    print $1, T, Pin, $2, $3, $4
}
' fort.66 > sampled_data.dat

cp fort.15 input_used.in
cp fort.25 model_used.in

echo "Run complete."
echo "Check trajectory: traj.lammpstrj"
