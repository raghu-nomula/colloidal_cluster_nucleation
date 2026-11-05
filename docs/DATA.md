# The trajectory data (not in this repository)

The Monte Carlo runs wrote **135 trajectory files (`*.lammpstrj`, 1.67 GB in total)**. They are too large for a
normal git repository (many are 50–130 MB), so they are **kept out of git and stay on the author's PC**; only 21
tiny snapshot files (under 200 KB each) are in the repository. The manifest lists all 135.
Everything else (inputs, manifests, notes, result tables, figures) is in the repository.

**To get a trajectory: ask the repository owner.** Give the path from the first column of
[DATA_MANIFEST.csv](DATA_MANIFEST.csv). After receiving a file, check it with
`sha256sum <file>` against the checksum in the same row, and put it back at the same relative path under
`simulations/` (the analysis scripts expect that).

## What is where

| Group | Files | Size | Path under `simulations/` | Used for |
|---|---|---|---|---|
| Main campaign dr = 0.04 | 12 | 196 MB | `4_Clean_NoSwap_Replication/dr_0.04/production_3M_seg001…012/traj.lammpstrj` | the crystal; all main figures |
| Main campaign dr = 0.01 | 12 | 197 MB | `4_Clean_NoSwap_Replication/dr_0.01/production_3M_seg001…012/traj.lammpstrj` | control that stayed liquid |
| Pilots, smoke tests, phase-3 tests | 46 | 36 MB | `4_Clean_NoSwap_Replication/dr_0.0x/…` | short checks before production |
| vmax search | 35 | 965 MB | `5_Vmax_Search/runs/stage_*/…` | volume-step study |
| First ("June") runs and tests | 30 | 274 MB | `2_1000_atoms/…`, `1_Trial_Tests_500N/…`, `3_Tests_for_codes/…`, `Run/` | liquid preparation, q6 cluster of 70 |

(Sizes are rounded; exact values are in the manifest.) The largest single file is 131 MB
(`2_1000_atoms/2_Actual_KMC_for_nucleation/4_step_1.5M_to_3.5M/traj.lammpstrj`).

## File format

LAMMPS dump text format, one frame per 1000 MC cycles, 251 frames per production segment, columns
`id type x y z` (type 1 and 2 are the two charge signs). Segment counters restart at 0; see the conventions in
[PROJECT_MAP.md](PROJECT_MAP.md#4-conventions-that-save-confusion).

## What is in the repository instead

* [results/example_frames/](../results/example_frames/): four single frames of the dr = 0.04 run (liquid start,
  2.10M, 2.25M and 3.00M cycles), enough to run [analysis/analyze_example_frames.py](../analysis/analyze_example_frames.py).
* A few tiny snapshot files (marked frames of the June run, OVITO snapshots of pilots) kept next to their runs.
* All result tables derived from the trajectories (CSV), so most questions can be answered without them.

## For the owner

* The files are on the PC at
  `/home/raghu/1_phd_raghu/1_work_progress/3_infRETIS_project/0_re-concstruct_paper/2_MC_NPT_Yukawa_potential/`
  (same relative paths as in the manifest). **Do not delete them**: they cannot be recovered without rerunning.
* Back them up outside the PC (external disk or institute storage). No hosting service is used at the moment;
  the checksums in the manifest let anyone verify a copy.
* Never `git add` trajectories: `.gitignore` blocks them on purpose.
