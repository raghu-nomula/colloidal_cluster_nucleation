# How the work developed

Dates are taken from file dates and are approximate. Details and decisions are in the lab notebook
`simulations/4_Clean_NoSwap_Replication/notes/`.

## The goal

Reproduce, qualitatively, the paper's brute-force observation at p\* = 18: without swap moves, a binary
mixture of oppositely charged colloids nucleates a **substitutionally disordered fcc** crystal; with swaps it
forms **CsCl**. The paper's forward-flux sampling (FFS) at p\* = 15 was deliberately **not** attempted. See
[reports/01_paper_manual.pdf](reports/01_paper_manual.pdf) for the paper itself.

## Timeline

| When | What | Where |
|---|---|---|
| June 2026 | No working code existed. The NpT Monte Carlo case study of Frenkel and Smit (Lennard-Jones) was found, compiled and run, then converted to a signed hard-core Yukawa potential with two particle types, hard-core rejection and LAMMPS-format trajectory output | `simulations/Source/` |
| mid-June | First tests with N = 500: liquid preparation and compression | `simulations/1_Trial_Tests_500N/` |
| June – early July | N = 1000: seven ramps from T\* = 2, p\* = 5 down to the target liquid at T\* = 1, p\* = 18; energy of the final liquid checked in LAMMPS | `simulations/2_1000_atoms/1_Metastable_Liquid/` |
| mid-June | First nucleation runs in steps (50K, 500K, 1.5M, then 1.5M → 3.5M cycles; dr = 0.01, vmax = 0.005). Cluster size from the author's q6 script gave an apparent cluster of 70 particles near 1.95M cycles | `simulations/2_1000_atoms/2_Actual_KMC_for_nucleation/`, `3_Tests_for_codes/` |
| by 2 July | The apparent cluster was **not trusted** (not obvious by eye, not supported by structure labels). The workflow was **rebuilt cleanly**: instrumented code, immutable run folders with manifests, validation of the liquid parent *without q6* (RDF, structure factor, OVITO PTM and CNA), two branches that differ only in dr | `simulations/4_Clean_NoSwap_Replication/` (Phases 1–5) |
| 2–3 July | The two production campaigns, 3 × 10⁶ cycles each (12 segments of 250 000), same start, vmax = 0.0005: **dr = 0.01 stayed liquid; dr = 0.04 crystallised at about 2.0–2.25 × 10⁶ cycles** | `dr_0.01/`, `dr_0.04/`, `analysis/production_3M/` |
| 8–10 July | Study of the volume step vmax at dr = 0.01 (Stages A, B, C). Stage C recommends 0.0004 (lower autocorrelation time); this was never used in production | `simulations/5_Vmax_Search/` |
| 25–28 October | Documentation and re-analysis, no new simulations: paper manual, cluster-size comparison with the paper's method, meeting report; q6 re-analysis of every frame; check of the "half the box" question; CNA connectivity; charge order; three slides for the collaboration meeting | `docs/reports/`, `analysis/q6_check/` |
| 5 November | This repository | |

## Decisions and why

* **No FFS, no swaps.** The aim was to check that the new code behaves as the paper's p\* = 18 brute-force run,
  not to redo the rate calculation.
* **Two displacement sizes.** The paper gives dr = 0.01 (flux) and dr = 0.04 (branching trajectories) for its FFS
  runs at p\* = 15 but nothing for the p\* = 18 brute-force run, so both were run as separate branches. The
  dr = 0.04 branch is described in the campaign README as a "requested comparison"; who requested it is not recorded.
* **vmax is not in the paper.** The volume step does not change the NpT equilibrium but changes the dynamics, so
  it was tested (2 × 2 test: dr 0.01 / 0.04 × vmax 0.001 / 0.0005; then Stages A–C) and fixed at 0.0005 for production.
* **Structure labels instead of q6.** The first q6 cluster could not be confirmed, so the clean campaign tracks
  crystallinity with OVITO CNA and PTM. A later q6 re-analysis (note 04 and 06) showed that the thresholds of
  ref. [18] over-count in this dense liquid (about 54 false solid-like particles per 1000, against fewer than 5
  in the paper), while the author's stricter thresholds (dot product 0.70, cutoff 1.45σ) match the paper's liquid.

## What the results mean, and what they do not

* The p\* = 18 no-swap run at dr = 0.04 forms a close-packed crystal (fcc and hcp, almost no bcc) with no extra
  charge order: qualitatively the paper's observation. See [reports/05_meeting_report.pdf](reports/05_meeting_report.pdf).
* One trajectory per setting, so no nucleation rate and no estimate of the time-to-nucleation distribution.
* The crystal wraps the periodic box (N = 1000) from about 2.15–2.25 × 10⁶ cycles; the final size (≈ 440–490
  particles, depending on method) is a finite-size limit, not a nucleus size. See
  [reports/06_q6_and_halfbox_check.pdf](reports/06_q6_and_halfbox_check.pdf).
* PTM and CNA find about twice as much hcp as fcc; the paper says fcc. We call the result "close-packed with
  stacking disorder".
* The paper's central comparison (barrier ordering fcc vs CsCl, the effect of swaps) was **not** reproduced.
