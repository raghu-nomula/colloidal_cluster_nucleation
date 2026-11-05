# simulations/

This folder mirrors the working folder on the author's PC **with the same names**, so that the paths in the run
manifests and the lab notes stay valid. Compiled programs and large trajectories are not included
([../docs/DATA.md](../docs/DATA.md)); `make` in the repository root builds the programs.

| Folder | What it is | Status |
|---|---|---|
| `Source/` | Fortran NpT Monte Carlo code: signed hard-core Yukawa pair potential (`ener.f`, `eneri.f`, `potential.inc`), two particle types (`conf.inc`), displacement and volume moves (`mcmove.f`, `mcvol.f`), LAMMPS-format trajectory output (`mc_npt.f`), `Makefile`. **There is no swap move in this code.** Adapted from the Frenkel–Smit LJ case study | in use |
| `Block/` | block-averaging helper (`block.f`) | in use |
| `Run/` | first output files of the code with the original LJ model (`lj.*`) and a `PairTest/` of the pair potential | historical |
| `1_Trial_Tests_500N/` | first tests with N = 500: preparing a liquid and compressing it step by step | historical |
| `2_1000_atoms/1_Metastable_Liquid/` | seven ramps (`1_…` to `7_…`) from T\* = 2, p\* = 5 to the N = 1000 liquid at T\* = 1, p\* = 18, with a LAMMPS energy check of the final configuration | done |
| `2_1000_atoms/2_Actual_KMC_for_nucleation/` | first ("June") nucleation runs in steps up to 3.5M cycles (dr = 0.01, vmax = 0.005) and the author's q6 cluster script; `4_step_1.5M_to_3.5M/` holds the run with the apparent 70-particle cluster | superseded by `4_…` |
| `3_Tests_for_codes/` | tests of the q6 script and of high-pressure runs | historical |
| `4_Clean_NoSwap_Replication/` | **main result**: validated liquid parent, instrumented code, run scripts, two 3M-cycle campaigns (dr = 0.01 and 0.04), structure analysis, lab notebook | done, see its `README.md` and `notes/00_INDEX.md` |
| `5_Vmax_Search/` | study of the volume step vmax at dr = 0.01 (Stages A–C) | done, see its `README.md` |

Run scripts (`run.sh`, `common/run_segment.sh`, …) find their root folder themselves. If you add a new
experiment, copy the pattern of `4_Clean_NoSwap_Replication/common/run_segment.sh` and **create a new folder**
rather than editing an old one.
