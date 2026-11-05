# Project map: what is here and how to find your way

This page answers three questions: **what exists, where is it, and what should I read first.**
Everything under `simulations/` keeps the **same folder names as on the author's PC**, so paths mentioned in the
lab notes and in the run manifests still make sense.

## 1. Reading order (30 minutes)

| Step | Read | Why |
|---|---|---|
| 1 | [README.md](../README.md) | headline result and caveats |
| 2 | [reports/01_paper_manual.pdf](reports/01_paper_manual.pdf) (6 pages) | what the paper did, step by step, and what it did *not* state |
| 3 | [reports/05_meeting_report.pdf](reports/05_meeting_report.pdf) (3 pages) and [reports/07_meeting_slides.pptx](reports/07_meeting_slides.pptx) | what was run at p\* = 18 and what came out |
| 4 | [HISTORY.md](HISTORY.md) | how the work developed and why decisions were made |
| 5 | [reports/04_cluster_size_comparison.pdf](reports/04_cluster_size_comparison.pdf), [reports/06_q6_and_halfbox_check.pdf](reports/06_q6_and_halfbox_check.pdf) | how "cluster size" is measured and why the 500-particle plateau is a finite-size limit |
| 6 | [../simulations/4_Clean_NoSwap_Replication/notes/00_INDEX.md](../simulations/4_Clean_NoSwap_Replication/notes/00_INDEX.md) | the detailed lab notebook of the main campaign |

## 2. Where is what

```
colloidal_cluster_nucleation/
├── README.md              front page
├── CONTRIBUTING.md        how to suggest changes
├── LICENSE, CITATION.cff  licence status (undecided) and how to cite
├── Makefile               "make" compiles the Fortran code
├── environment.yml        Python environment for the analysis scripts
│
├── docs/                  everything written for humans
│   ├── PROJECT_MAP.md     this page
│   ├── HISTORY.md         timeline and decisions
│   ├── REPRODUCE.md       build, run and analyse
│   ├── DATA.md            the trajectories that are NOT in the repository
│   ├── DATA_MANIFEST.csv  size and SHA-256 of each of the 135 trajectory files
│   ├── NEXT_STEPS.md      open questions and proposed work
│   ├── PATH_CHANGES.md    what was edited in the scripts so they run anywhere
│   ├── GIT_FOR_RAGHU.md   owner's cheat-sheet (review, merge, undo)
│   ├── reports/           01 paper manual, 04 cluster-size comparison, 05 meeting report,
│   │                      06 q6 and half-box check (PDF + LaTeX source), 07 meeting slides, figs/
│   └── background/        earlier guides written while the code was being reconstructed (July 2026)
│
├── simulations/           the working folders, same names as on the author's PC
│   ├── Source/            Fortran Monte Carlo code (NpT, signed hard-core Yukawa) + Makefile
│   ├── Block/             block-averaging helper program
│   ├── Run/               early outputs of the code on its first tests (with the LJ model)
│   ├── 1_Trial_Tests_500N/            first tests, N = 500, liquid preparation and compression
│   ├── 2_1000_atoms/
│   │   ├── 1_Metastable_Liquid/       seven ramps to the N = 1000 liquid at T* = 1, p* = 18
│   │   └── 2_Actual_KMC_for_nucleation/   the first ("June") nucleation runs and their q6 cluster analysis
│   ├── 3_Tests_for_codes/             tests of the q6 script and of high-pressure runs
│   ├── 4_Clean_NoSwap_Replication/    THE MAIN RESULT: clean rebuild and the two 3M-cycle campaigns
│   └── 5_Vmax_Search/                 study of the volume step vmax (dr = 0.01)
│
├── analysis/
│   ├── analyze_example_frames.py      structure analysis of the four example frames (no big files needed)
│   └── q6_check/                      re-analysis of all frames with q6, half-box check, charge order, g(r), slide builder
│
└── results/
    └── example_frames/    four single-frame trajectory files (liquid start, 2.10M, 2.25M, 3.0M cycles, dr = 0.04)
```

### Inside `simulations/4_Clean_NoSwap_Replication/` (the part to understand first)

| Path | What it is |
|---|---|
| `README.md`, `notes/` | the lab notebook: `00_INDEX.md` (start), Phase 1–5 records, `DECISIONS.md`, `KNOWN_LIMITATIONS.md`, `CONFIGURATION_LINEAGE.md`, `CODE_AND_WORKFLOW_CHANGE_LOG.md` |
| `common/` | the validated liquid parent `validated_parent_N1000_T1_P18.res` (density 1.037, packing fraction 0.543), run scripts (`run_segment.sh`, `run_campaign.sh`, `launch_*.sh`) |
| `dr_0.01/`, `dr_0.04/` | the two branches. Each holds pilots (`pilot_200`, `phase3_*`), smoke tests, and the production campaign `production_3M_seg001 … seg012` plus `production_3M_control/` (state and cumulative metrics) |
| `dr_0.0x/production_3M_segNNN/` | one run of 250 000 cycles: `input_used.in`, `manifest.txt` (seed, parent, hashes, times), `run_metrics.dat`, `final_config.res`, and (on the owner's PC only) `traj.lammpstrj` |
| `analysis/` | `ovito_structure.py` (PTM/CNA and cluster routines), `analyze_campaign.py`, `validate_structure.py`, and `production_3M/` with the result tables `dr_0.0x_structure_timeseries.csv` and plots |
| `presentation/` | an earlier 16-slide deck and its build script |
| `launch_both_3M.sh`, `production_status.sh`, `analyze_both_when_complete.sh` | how the two campaigns were started, monitored and analysed |

## 3. Which file answers which question

| Question | Look here |
|---|---|
| What does the paper claim and how? | `docs/reports/01_paper_manual.pdf` |
| What exactly was run at p\* = 18? | `docs/reports/05_meeting_report.pdf`; parameters in each `manifest.txt` and `input_used.in` |
| What are the main numbers? | `simulations/4_Clean_NoSwap_Replication/analysis/production_3M/dr_0.04_structure_timeseries.csv` (and `dr_0.01_…`): one row per 1000 cycles with PTM and CNA counts and the largest fcc/hcp cluster |
| Why was `vmax = 0.0005` used? | `reports/05` section 3; `simulations/4_Clean_NoSwap_Replication/notes/PHASE_03_VOLUME_TUNING.md`; `simulations/5_Vmax_Search/notes/` |
| How is the cluster size defined, and how does it differ from the paper? | `docs/reports/04_cluster_size_comparison.pdf` |
| Is the ≈ 500-particle plateau a real nucleus size? | no, see `docs/reports/06_q6_and_halfbox_check.pdf` |
| Where did each run start from, and with which seed and executable? | `manifest.txt` inside the run folder; lineage in `notes/CONFIGURATION_LINEAGE.md` |
| What is not known or not done? | `notes/KNOWN_LIMITATIONS.md`, `docs/NEXT_STEPS.md` |
| How do I get the trajectory files? | `docs/DATA.md` |

## 4. Conventions that save confusion

* **Units are reduced:** T\*, p\*, σ = 1, κσ = 6, cutoff 3.5σ. One MC **cycle** = 1000 displacement attempts + 1 volume attempt.
* **Segments:** a production campaign is 12 segments of 250 000 cycles. Inside a segment the cycle counter in the
  trajectory restarts at 0 and a frame is saved every 1000 cycles (251 frames; frame 0 repeats the last frame of the
  previous segment). **Cumulative cycles = (segment − 1) × 250 000 + local cycle.**
  Example: `dr_0.04/production_3M_seg009`, frame 100 is at 2 100 000 cycles.
* **dr** is the maximum displacement per particle move; **vmax** is the maximum change of ln V per volume move.
  `dr` changes the dynamics (speed per cycle), so the two branches must not be compared on a raw cycle axis.
  `vmax` is algorithmic (it does not change the NpT equilibrium). Production used `vmax = 0.0005`; a later search
  recommends 0.0004, which was **never used in production**.
* **Two generations of work.** The *June* runs (`2_1000_atoms/2_Actual_KMC_for_nucleation`) used the author's q6
  cluster script and an apparent cluster of 70 particles that was later judged not to be a crystal. The *clean*
  campaign (`4_Clean_NoSwap_Replication`) rebuilt the workflow and uses OVITO structure labels (CNA, PTM).
* **Cluster definitions differ:** paper = q6 bond-order (ref. [18], structure-blind); clean campaign = connected
  fcc + hcp particles (structure-labelled). Always say which one a number refers to.
* **Completed run folders are never edited**: each is a self-contained record (`manifest.txt` has the hashes).
* The folder name `3_step_500K_to_15000K` means 500 000 → 1.5 million cycles.

## 5. Known rough edges

* Run manifests and old notes contain absolute paths such as `/home/raghu/…`. They are historical records and
  were left as they are. The **scripts** were made path-independent (see [PATH_CHANGES.md](PATH_CHANGES.md)).
* Some old scripts in `1_Trial_Tests_500N` refer to a folder `1_Tests`, the earlier name of that folder.
* The trajectories needed to re-run the analysis of the campaigns are not in the repository ([DATA.md](DATA.md)).
* `docs/background/` was written during reconstruction (July 2026) and may contain statements that were
  later refined; the reports in `docs/reports/` are the up-to-date summaries.
* Earlier drafts `01_paper_refresher.md`, `02_project_story.md`, `03_self_quiz.md` are deliberately not included
  (partly out of date).
* Who proposed `dr = 0.04` (the "requested comparison" in the campaign README) is not recorded in the files.
