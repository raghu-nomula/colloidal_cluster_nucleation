# Phase 5 — production execution and post-run analysis guide

## Status

The production scripts are ready and tested. The two three-million-cycle jobs
have not yet been launched.

## One-command launch

From the project root, run:

```bash
./4_Clean_NoSwap_Replication/launch_both_3M.sh
```

This checks that neither campaign already exists, verifies at least 5 GiB of
free space, and launches both branches through `nohup`.

Each branch consists of twelve sequential 250,000-cycle segments. The two
branches run concurrently, while segments within one branch run sequentially.

## Monitoring

At any time, run:

```bash
./4_Clean_NoSwap_Replication/production_status.sh
```

It reports PID state, completed cumulative cycles, percentage, latest metrics,
recent campaign-log messages and disk space. It does not modify a running job.

The process survives closing VS Code or the terminal. Actual system suspension
pauses the CPU, so progress resumes only after the computer wakes.

## Expected runtime

The previous one-million-cycle `dr=0.01` run required about 6.3 hours on this
computer. Three million cycles may therefore require roughly 19 CPU-hours per
branch. Running both simultaneously can increase wall time because they compete
for CPU and memory bandwidth. This estimate is approximate; check real progress
after the first 250,000-cycle segment.

## After both finish

Run:

```bash
./4_Clean_NoSwap_Replication/analyze_both_when_complete.sh
```

The script refuses to analyse until both campaign state files report all
3,000,000 cycles. It then applies OVITO PTM and adaptive CNA to every saved
frame in every segment and writes:

```text
analysis/production_3M/dr_0.01_structure_timeseries.csv
analysis/production_3M/dr_0.04_structure_timeseries.csv
```

Each row contains cumulative cycle, PTM/CNA structural counts, and the largest
connected FCC/HCP cluster. Restart-boundary duplicate frames are removed.

## Inspection after automated analysis

The scientific inspection should compare:

- density and packing fraction versus cumulative cycle;
- particle and volume acceptance versus segment;
- energy consistency checks in each segment;
- PTM and CNA crystalline-particle counts;
- largest FCC/HCP cluster versus cumulative cycle;
- persistence rather than one-frame structural spikes;
- marked configurations before, during and after any sustained growth;
- total and charge-resolved RDFs for candidate nuclei;
- `dr=0.01` and `dr=0.04` as separate dynamical experiments.

No nucleation claim should be based solely on a single PTM, CNA or earlier q6
classification.

