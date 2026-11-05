# Phase 4 — segmented production preparation

## Objective

Prepare long no-swap runs that are restartable, preserve exact lineage, avoid
32-bit attempt-counter overflow within one executable invocation, and provide a
cumulative cycle axis across segments. This phase prepares and tests machinery;
it does not launch the multi-million-cycle production campaigns.

## Changes to the segment runner

`common/run_segment.sh` now optionally accepts:

1. an explicit starting configuration;
2. an explicit sampling interval.

The default remains the validated common parent. Every segment records the
resolved source path and SHA-256 of the actual copied start file.

## Campaign runner

`common/run_campaign.sh` accepts:

```text
BRANCH CAMPAIGN TOTAL_CYCLES SEGMENT_CYCLES SEED_BASE NSAMP
```

It performs these steps:

- fixes `vmax=0.0005`;
- starts segment 1 from the validated common parent;
- starts each later segment from the preceding clean final restart;
- uses a new deterministic seed for each segment;
- stores each segment in a separate immutable directory;
- writes progress atomically to `state.txt`;
- builds `cumulative_metrics.dat` with cumulative cycle numbers;
- skips duplicate cycle-zero rows at restart boundaries;
- exits without rerunning if the requested campaign is already complete;
- resumes from the last completed segment when state and restart agree.

An interrupted segment directory is deliberately not deleted automatically.
It requires inspection because silently replacing partial scientific output is
unsafe.

## Detached launcher

`common/launch_campaign_nohup.sh` launches a campaign with `nohup`, records its
PID and redirects output to a branch-specific campaign log. This survives
terminal closure on a normal Linux session. Computation pauses during actual
computer suspension and continues after wake-up.

## First smoke test and discovered issue

Both branches ran a 20-cycle campaign split into two 10-cycle segments.
Restart hashes matched exactly, proving that segment 2 started from segment 1's
final coordinates. The first smoke test revealed that cumulative metrics
contained both segment 1's final row and segment 2's cycle-zero row at the same
cumulative cycle.

The merge rule was corrected to omit cycle zero for every segment after the
first. The original smoke-test directories remain as a transparent record of
the issue.

## Corrected smoke test

Campaign `phase4_smoke2` was run for both branches with two 10-cycle segments.

Results:

- cumulative cycles were exactly `0, 5, 10, 15, 20`;
- no boundary cycle was duplicated;
- both campaign states ended at 20 cycles;
- segment 1 final SHA-256 exactly equaled segment 2 start SHA-256 in each
  branch;
- both campaigns completed cleanly.

## Proposed production layout

For a three-million-cycle comparison:

- total cycles: 3,000,000 per branch;
- segment length: 250,000 cycles;
- segments: 12 per branch;
- sampling interval: 1,000 cycles;
- fixed `vmax=0.0005`;
- common validated parent for segment 1;
- separate seed ranges for the two branches.

Proposed launch commands from the project root:

```bash
4_Clean_NoSwap_Replication/common/launch_campaign_nohup.sh \
  dr_0.01 production_3M 3000000 250000 91001 1000

4_Clean_NoSwap_Replication/common/launch_campaign_nohup.sh \
  dr_0.04 production_3M 3000000 250000 94001 1000
```

These commands are documented but were not executed during Phase 4.

## Decision gate before launch

Before launching, confirm available disk space, expected runtime, whether both
campaigns should compete for CPU simultaneously, and the desired structural
analysis frequency. Long trajectories remain separated by segment, while the
compact metrics have one cumulative time axis.

