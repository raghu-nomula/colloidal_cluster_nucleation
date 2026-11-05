# LAMMPS–Fortran Yukawa energy check

This checks the final MC-NPT state against the LAMMPS `yukawa` pair style with
`sigma = 1`, `kappa = 6`, and cutoff `3.5`. The Fortran potential is

    U_ij(r) = s_ij exp[-kappa(r-sigma)] / (r/sigma),

where `s_ij` is +1 for equal types and -1 for unlike types. LAMMPS uses

    U_ij(r) = A_ij exp(-kappa r) / r,

so its coefficients must be `A_ij = s_ij sigma exp(kappa sigma)`. Here their
magnitude is `exp(6) = 403.4287934927351`.

Run:

    ./run_check.sh

On an HPC system, first load whatever LAMMPS module your center provides, for
example `module load LAMMPS`, and then run the command above. The script accepts
executables named `lmp`, `lmp_mpi`, or `lammps`. You may copy this check folder
by itself: the two generated `.data` files are included, and `run_check.sh`
uses them when the original parent-directory MC files are absent.

`in.restart` uses `final_config.res`, whose coordinates and box retain full
double precision. `in.dump` independently uses the literal last frame of
`traj.lammpstrj`; expect a tiny rounding difference because that dump stores
coordinates with only eight digits after the decimal point. The Fortran value
printed at the end of production is `-874.06026` (total, not per particle).

This configuration has no hard-core overlaps. That matters because the Fortran
code rejects `r < sigma`, while plain LAMMPS `pair_style yukawa` does not include
that hard core. The conversion script now calculates the minimum-image distance
for every pair and aborts before LAMMPS if it finds `r < 1`. For the
full-precision configuration,

    r_min = 1.000004005188 > sigma = 1.

Therefore the hard-core contribution is exactly zero for this static
configuration, and plain LAMMPS Yukawa evaluates the same finite branch as the
Fortran code for every pair. This proves equality of the energy for this saved
state; it does **not** make plain LAMMPS Yukawa a dynamically equivalent model,
because an MD/minimization run could subsequently create `r < 1` overlaps.

Expected full-precision result:

    Fortran total energy (direct full-precision sum): -874.060263913129
    Fortran value printed in out:                    -874.06026

The last dump frame should differ only around `4.7e-7` because its coordinates
were rounded when written.
