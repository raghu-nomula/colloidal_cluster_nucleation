# Vmax search at fixed paper displacement `dr=0.01`

## Status

Stages A, B, and C are complete. Stage C refined the region around `vmax=0.0005`
and shifted the data-driven recommendation to `vmax=0.0004`.

Current decision:

> Use `vmax=0.0004` for the next `dr=0.01` NpT production branch, unless exact
> continuity with older `vmax=0.0005` campaigns is more important than the Stage C
> sampling-efficiency improvement. See `notes/STAGE_C_ANALYSIS_AND_DECISION.md`.

This is an algorithmic NpT proposal-width study. It is not a nucleation-outcome
study, and `vmax` should not be interpreted as a physical knob that directly
forces densification or nucleation.

## Directory Flow

```text
5_Vmax_Search/
├── README.md                         main runbook and current plan
├── run_one.sh                        single-run worker used by all stages
├── run_stage_a.sh                    broad single-seed screen
├── run_stage_b.sh                    replicated comparison around candidates
├── run_stage_c.sh                    focused IACT-minimum refinement
├── launch_stage_*.sh                 background launchers using nohup/setsid
├── status*.sh                        progress checks
├── analyze.py                        basic summary table generator
├── plot_vmax_analysis.py             plotting helper for existing diagnostics
├── notes/                            detailed explanations and archived notes
├── plots/                            generated diagnostic figures
└── runs/                             raw run outputs by stage
```

Detailed explanations live in:

```text
notes/Vmax_ANALYSIS_EXPLAINED.md
notes/STAGE_AB_RESULTS_AND_DECISION.md
notes/STAGE_C_ANALYSIS_AND_DECISION.md
```

## Fixed Physical Setup

Every Vmax-search run uses the same physical model and parent configuration:

```text
N = 1000
T* = 1
p* = 18
dr = 0.01
kappa*sigma = 6
rc = 3.5 sigma
swaps = off
succ = 0, so move widths are not automatically adjusted
1000 particle displacement attempts and 1 volume attempt per MC cycle
parent = 4_Clean_NoSwap_Replication/common/validated_parent_N1000_T1_P18.res
```

All candidates restart independently from the same validated parent. Candidate
endpoints are never chained into later candidates.

## Stage A: Broad Screen

Purpose: map the basic acceptance curve.

```text
vmax values: 0.00020 0.00030 0.00040 0.00050 0.00065 0.00080 0.00100
seed: 85001
cycles: 5000
nsamp: 50
```

Outcome:

```text
vmax       volume acceptance
0.00020    44.93%
0.00030    32.99%
0.00040    26.18%
0.00050    21.02%
0.00065    16.44%
0.00080    12.91%
0.00100    10.22%
```

Conclusion: increasing `vmax` decreases volume acceptance, while particle
acceptance stays essentially flat. This confirmed that `vmax` mainly controls
volume-move proposal behavior.

## Stage B: Replicated Candidate Comparison

Purpose: compare high, medium, and lower volume-acceptance candidates using
independent seeds.

```text
vmax values: 0.00020 0.00030 0.00050
seeds: 86101 86201 86301
cycles: 10000
nsamp: 50
```

Aggregate result:

```text
vmax       mean vol. acc.   mean density   mean IACT   mean ESS
0.00020    46.24%           1.03922        22.68       4.66
0.00030    34.32%           1.03758        18.66       5.82
0.00050    22.03%           1.03592        15.66       7.78
```

Interpretation:

- `0.0005` did not create the largest density.
- `ESS` is not density; it is the estimated number of effectively independent
  density samples after accounting for autocorrelation.
- `0.0005` had the lowest mean density IACT and highest mean ESS among the
  replicated Stage B candidates.

This made `0.0005` the provisional best value, but Stage B did not test values
slightly above `0.0005` with replicates.

## Why Stage C Is Needed

Stage B showed IACT decreasing from `0.00020` to `0.00050`:

```text
0.00020 -> IACT 22.68
0.00030 -> IACT 18.66
0.00050 -> IACT 15.66
```

That means we have not yet bracketed a local IACT minimum. The minimum may be
near `0.0005`, or it may sit slightly above it. Going higher can improve volume
exploration, but it also lowers volume acceptance. Stage C is designed to find
that balance more carefully.

## Stage C: Focused IACT-Minimum Refinement

Status: complete.

Purpose: refine the Vmax choice around `0.0005` using longer runs and denser
sampling, without requiring active monitoring.

```text
vmax values: 0.00040 0.00050 0.00060 0.00065 0.00070
seeds: 87101 87201 87301
cycles: 20000
nsamp: 25
total runs: 15
```

Reasoning:

- `0.00040` checks the lower side near the current best.
- `0.00050` repeats the current best with longer runs.
- `0.00060` and `0.00065` test whether IACT keeps improving above `0.0005`.
- `0.00070` tests the onset of too-low volume acceptance without jumping all
  the way to the clearly low-acceptance `0.00080` or `0.00100` region.

Stage C captured the full run data. The deeper analysis is recorded in
`notes/STAGE_C_ANALYSIS_AND_DECISION.md`; the main result is that `0.0004` gives
the best full-window density IACT/ESS while keeping healthy volume acceptance.

## Commands

From this directory:

```bash
cd 5_Vmax_Search
```

Launch Stage C in the background:

```bash
./launch_stage_c.sh
```

Check progress when desired:

```bash
./status_stage_c.sh
```

Generate or regenerate basic summaries after completion:

```bash
./analyze.py runs/stage_c
```

Existing Stage A/B diagnostic plots can be regenerated with:

```bash
conda activate matsci
python3 plot_vmax_analysis.py
```

Stage C-specific analysis plots and decision tables can be regenerated with:

```bash
conda activate matsci
python3 analyze_stage_c.py
```

## Data Captured Per Run

Each run directory keeps:

```text
manifest.txt
input_used.in
model_used.in
start_config.res
final_config.res
run_metrics.dat
sampled_data.dat
traj.lammpstrj
out
fort.* bookkeeping files
mc_npt executable copy
```

The manifest records the stage, `vmax`, seed, cycles, `nsamp`, parent checksum,
executable checksum, creation time, completion time, and final metrics line.
