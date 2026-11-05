# How to build, run and analyse

All commands are run from the repository root unless stated otherwise. Linux with `gfortran`, `make` and
`conda` is assumed (tested on Ubuntu with gfortran and conda; nothing here is Windows-specific but it was not tested).

## 1. Python environment

```bash
conda env create -f environment.yml
conda activate yukawa-nucleation
```

OVITO's Python module (`ovito`) is used for the structure labels (CNA, PTM).

## 2. Check the analysis on the saved example frames (minutes, no big files)

```bash
python analysis/analyze_example_frames.py
```

Expected output (CNA = adaptive common-neighbour analysis; "largest" = largest connected fcc + hcp cluster,
connection distance 1.45σ; "opp.charge" = fraction of opposite-charge nearest-neighbour pairs below 1.3σ among
fcc + hcp particles, for the liquid frame among all particles; q6 = the author's settings):

```
frame                                    fcc hcp bcc other | largest | opp.charge | q6 solid-like
dr0.04_0.00M_liquid_start_...frame000      0   0   1   999 |       0 |   0.604   | 0
dr0.04_2.10M_growing_...frame100          84 111  43   762 |     193 |   0.581   | 526
dr0.04_2.25M_grown_...frame250           146 302   7   545 |     448 |   0.579   | 761
dr0.04_3.00M_final_...frame250           146 294   8   552 |     440 |   0.578   | 791
```

The example frames can also be opened in [OVITO](https://www.ovito.org): add *Common neighbor analysis*
(adaptive); green = fcc, red = hcp, blue = bcc, white = other. Adding *Replicate* (2 × 2 × 2) shows that the
crystal is one body that wraps through the periodic box.

## 3. Compile the Monte Carlo code

```bash
make            # uses gfortran; "make FC=ifort" for another compiler
```

This builds `simulations/Source/mc_npt` and `simulations/Block/block` and copies the executable to
`simulations/4_Clean_NoSwap_Replication/common/mc_npt_phase1`, where the campaign scripts expect it.

**About checksums:** the run manifests record the SHA-256 of the original executable
(`2e6b96bc…`). A freshly compiled binary has a different checksum (different compiler and build time), but the
original executable and `simulations/Source/` of the repository come from the same source state (the original
`Source/mc_npt` and `common/mc_npt_phase1` were byte-identical). Compare results, not checksums.

## 4. Run a (short) simulation yourself

This is **new computation**; one 250 000-cycle segment took about 1.5 hours on the author's PC (see the times in
any `manifest.txt`). A short test of one segment, from the validated parent, is the following
(**not yet tested in this repository copy**; the script itself is the one used for the published runs):

```bash
cd simulations/4_Clean_NoSwap_Replication
common/run_segment.sh dr_0.04 my_test_1k 1000 12345 0.0005
```

Arguments: `BRANCH RUN_NAME CYCLES SEED [VMAX [START_CONFIG [NSAMP]]]`. The script creates a new folder
`dr_0.04/my_test_1k/` (it refuses to overwrite), copies the executable and parent into it, and writes
`manifest.txt` with seed, parent and hashes. Branch `dr_0.01` or `dr_0.04` fixes the maximum displacement.
A whole campaign is started with `common/launch_campaign_nohup.sh` (see `launch_both_3M.sh` for the exact
commands used for the two 3-million-cycle campaigns, seeds 91001 and 94001).

Parameters not changeable from the command line (N = 1000, T\* = 1, p\* = 18, κσ = 6, rc = 3.5σ, 1000
displacement attempts and 1 volume attempt per cycle) are in `common/` and in the `input_used.in` of any run.

Please do not commit new trajectories; see [DATA.md](DATA.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).

## 5. Re-create the result tables from the trajectories (needs the big files)

```bash
cd simulations/4_Clean_NoSwap_Replication
./analyze_both_when_complete.sh          # set PYTHON=/path/to/python if OVITO is in a conda env
```

This needs the 24 production trajectories in `dr_0.01/production_3M_seg*/` and `dr_0.04/production_3M_seg*/`
(393 MB, [DATA.md](DATA.md)). The q6 re-analysis scripts are in `analysis/q6_check/` (`run_all.py`,
`halfbox.py`, `cutoff_scan.py`, `validate_q6.py`); they expect the trajectories in the same folders.
The tables that these scripts produce are already in the repository:
`simulations/4_Clean_NoSwap_Replication/analysis/production_3M/*_structure_timeseries.csv` and
`analysis/q6_check/*.csv`.

## 6. Rebuild the reports and the slides

* Reports: `cd docs/reports && pdflatex 05_meeting_report.tex` (needs a LaTeX installation).
* Slides: `python analysis/q6_check/make_slides.py` (needs `python-pptx`).
