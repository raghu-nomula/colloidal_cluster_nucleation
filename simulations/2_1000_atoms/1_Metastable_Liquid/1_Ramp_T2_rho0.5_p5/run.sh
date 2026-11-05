#!/usr/bin/env bash
set -e

ROOT="$(d="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"; while [ ! -d "$d/Source" ] && [ "$d" != / ]; do d="$(dirname "$d")"; done; echo "$d")"  # = simulations/ (folder that holds Source/)
EXE="$ROOT/Source/mc_npt"
BLOCK="$ROOT/Block/block"

rm -f fort.* out traj.lammpstrj sampled_data.dat final_config.res input_used.in model_used.in

cat > fort.25 << 'EOF'
tailco shift
.false. .false.
eps sig mass rc kappa
1. 1. 1. 3.5 6.0
EOF

cat > fort.15 << 'EOF'
ibeg  , nequil  , lmax   nsamp  iseed
0      3000      5000   250    88401
dr      vmax  succ
0.12    0.03  30.
ndispl  nvol
1000     5
npart temp rho      p     struc
1000  2.0  0.5      5.0   'sc'
EOF

"$EXE" > out

cp fort.21 final_config.res
cp fort.66 sampled_data.dat
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
echo "Outputs:"
echo "  out"
echo "  sampled_data.dat"
echo "  final_config.res"
echo "  traj.lammpstrj"
