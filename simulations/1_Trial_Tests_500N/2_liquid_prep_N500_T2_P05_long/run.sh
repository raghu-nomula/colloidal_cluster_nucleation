#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
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
0      2000      3000   100    78356
dr      vmax  succ
0.20    0.02  50.
ndispl  nvol
500      1
npart temp rho      p     struc
500   2.0  0.5      0.5   'fcc'
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

tail -n +2 fort.66 > fort.32
"$BLOCK" >> out

echo "Run complete."
echo "Outputs:"
echo "  out"
echo "  sampled_data.dat"
echo "  final_config.res"
echo "  traj.lammpstrj"
echo "  input_used.in"
echo "  model_used.in"
