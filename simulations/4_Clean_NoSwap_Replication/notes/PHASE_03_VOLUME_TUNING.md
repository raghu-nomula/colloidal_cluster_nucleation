# Phase 3 — volume-move tuning and medium-run gate

## Objective

Choose one fixed `vmax` for both displacement branches without modifying the
physical state, particle move sizes or common parent. Confirm that the chosen
value gives useful volume acceptance and that both branches remain liquid over
a run longer than the 200-cycle Phase 2 checks.

This phase did not attempt to observe nucleation and did not promote any Phase
3 endpoint as a new common parent.

## Fixed inputs

- Parent: `common/validated_parent_N1000_T1_P18.res`
- Parent SHA-256:
  `7e406f2b61fc128cf919327341723516e88824c44104a88e84fb0d4fc09c00a0`
- Executable: `common/mc_npt_phase1`
- Executable SHA-256:
  `2e6b96bc732a66da48f6ed2151a10a349effd634667a3cd08a04b8995282adca`
- `N=1000`, `T*=1`, `p*=18`
- `kappa*sigma=6`, `rc=3.5 sigma`
- 1000 displacement attempts and one volume attempt per cycle
- no swaps
- fixed move sizes (`succ=0`)

## Part A: 2x2 tuning matrix

Four 1000-cycle runs crossed the two requested displacement sizes with two
volume proposal sizes. Within each `dr` branch the same random seed was used
for both `vmax` tests to reduce avoidable differences in the random stream.

| dr | vmax | seed | Particle acceptance | Volume acceptance | Final rho | Final eta |
|---:|---:|---:|---:|---:|---:|---:|
| 0.01 | 0.0010 | 61001 | 86.44% | 9.28% | 1.038020 | 0.543506 |
| 0.01 | 0.0005 | 61001 | 86.65% | 19.63% | 1.035466 | 0.542169 |
| 0.04 | 0.0010 | 64001 | 57.25% | 9.45% | 1.037183 | 0.543068 |
| 0.04 | 0.0005 | 64001 | 57.16% | 20.50% | 1.037731 | 0.543354 |

All four endpoints had:

- zero hard-core overlaps;
- exact 500:500 composition;
- PTM classification of 1000 OTHER;
- no connected PTM FCC/HCP cluster;
- at most isolated CNA labels;
- consistent running and recomputed energy/virial.

## Selection of vmax

`vmax=0.0005` was selected. It approximately doubled volume acceptance from
9% to 20% without materially changing particle acceptance or producing crystal
classifications. The same value will be used in both branches so the comparison
does not mix volume-proposal algorithms.

The goal is not a universal optimal acceptance percentage. The choice simply
provides substantially less waste than `0.001` while keeping logarithmic volume
steps small and fixed.

## Part B: medium-run execution history

Two concurrent 10,000-cycle jobs were attempted in the Codex execution
sandbox. The first attempt was terminated before either executable flushed any
data; the directories named `phase3_medium_10k` contain zero-length run files
and are retained only as failure records.

A retry named `phase3_medium_10k_retry1` reached approximately cycle 2000 in
both branches before the sandbox reaped the processes. These jobs did not shut
down cleanly, did not produce final restart files and are not used as scientific
results or future inputs.

To obtain cleanly completed runs under the sandbox time constraint, the medium
gate was reduced to 2000 cycles and each branch was run separately. This changes
only the validation duration, not any model or move parameter.

## Completed 2000-cycle medium runs

| dr | seed | Particle acceptance | Volume acceptance | Final rho | Final eta |
|---:|---:|---:|---:|---:|---:|
| 0.01 | 71001 | 86.72% | 22.02% | 1.038896 | 0.543965 |
| 0.04 | 74001 | 57.22% | 21.58% | 1.035332 | 0.542098 |

### dr=0.01 endpoint

- minimum distance: 1.000002 sigma;
- overlaps: 0;
- mean neighbors within 1.45 sigma: 12.862;
- unlike-charge neighbor fraction: 0.57036;
- maximum tested low-index structure factor: 2.520;
- PTM: 1000 OTHER;
- CNA: 999 OTHER, one isolated BCC;
- largest FCC/HCP cluster: 0.

### dr=0.04 endpoint

- minimum distance: 1.000006 sigma;
- overlaps: 0;
- mean neighbors within 1.45 sigma: 12.794;
- unlike-charge neighbor fraction: 0.56839;
- maximum tested low-index structure factor: 2.647;
- PTM: 1000 OTHER;
- CNA: 998 OTHER, one isolated HCP and one isolated BCC;
- largest CNA FCC/HCP cluster: 1.

Both endpoints passed the independent energy and virial consistency checks.

## Interpretation

The smaller volume step provides stable sampling with about 20% acceptance.
Both particle displacement sizes remain physically mobile and structurally
liquid. The isolated CNA classifications are not persistent connected nuclei
and PTM identifies no crystalline particles at either endpoint.

Differences between the final densities are normal stochastic fluctuations and
short-run relaxation. They do not justify using one endpoint as the other's
parent.

## Decision

- Fix `vmax=0.0005` for both production branches.
- Keep `dr=0.01` and `dr=0.04` as separately labelled experiments.
- Return both branches to the unchanged validated common parent for long runs.
- Do not propagate any tuning or medium-run final configuration.
- Long jobs must be segmented and restartable because of counter limits,
  machine interruptions and the need for cumulative bookkeeping.

