# Phase 2 — independent validation of the parent liquid

## Purpose

The previous `q6` analysis was not trusted because an apparent cluster was not
obvious during visual inspection. Phase 2 therefore validated candidate liquid
configurations without using that `q6` implementation. The goal was to select
one common metastable liquid from which both `dr` branches can start.

## Analysis environments

The base Conda Python did not contain NumPy. The existing environment
`/home/raghu/miniconda3/envs/matsci` was found to contain NumPy, SciPy, ASE and
OVITO 3.15.4. All Phase 2 Python analyses used that environment.

## Analysis programs

### `analysis/validate_structure.py`

This direct geometric analysis reads a Fortran restart and calculates:

- total particle count;
- count of each charge type;
- box length, density and packing fraction;
- minimum periodic pair separation;
- number of forbidden hard-core overlaps (`r < sigma`);
- mean neighbor count within `1.45 sigma`;
- fraction of neighboring pairs with unlike charges;
- total RDF;
- same-charge RDF;
- opposite-charge RDF;
- maximum tested low-index static structure-factor peak.

It also writes `ovito_snapshot.lammpstrj` for independent visualization.

The structure-factor scan is a warning diagnostic. A small value supports the
absence of strong Bragg order, but it is not by itself a complete crystal
classifier.

### `analysis/ovito_structure.py`

This applies two independent OVITO algorithms:

- Polyhedral Template Matching with RMSD cutoff 0.10;
- adaptive Common Neighbor Analysis.

It counts FCC, HCP, BCC and unclassified particles and independently connects
FCC/HCP particles within `1.45 sigma` to report the largest close-packed
cluster. It also writes `ptm_marked.lammpstrj` for inspection in OVITO.

These methods do not use the project's earlier `q6` output.

## First candidate: original input to the 50k run

Results:

- particles: 1000;
- type 1: 500;
- type 2: 500;
- density: 0.993580;
- packing fraction: 0.520237;
- minimum pair distance: 1.000004 sigma;
- hard-core overlaps: 0;
- mean neighbors inside `1.45 sigma`: 12.428;
- unlike-charge neighbor fraction: 0.57113;
- maximum tested low-index structure factor: 2.289;
- PTM: 1000 OTHER;
- adaptive CNA: 1000 OTHER;
- largest FCC/HCP cluster: 0.

Interpretation: this configuration is a clean liquid, but it is less dense
than the liquid reached later during the existing `p*=18` history.

## Second candidate: existing 500k endpoint

The file examined was:

`2_1000_atoms/2_Actual_KMC_for_nucleation/2_step_50K_to_500K/500K_final_config.res`

Results:

- particles: 1000;
- type 1: 500;
- type 2: 500;
- density: 1.037080;
- packing fraction: 0.543014;
- minimum pair distance: 1.000006 sigma;
- hard-core overlaps: 0;
- mean neighbors inside `1.45 sigma`: 12.826;
- unlike-charge neighbor fraction: 0.57212;
- maximum tested low-index structure factor: 2.034;
- PTM: 1000 OTHER;
- adaptive CNA: 999 OTHER and one isolated BCC classification;
- largest FCC/HCP cluster: 0.

Interpretation: this is a denser `p*=18` liquid with no independently detected
close-packed nucleus and no strong reciprocal-space ordering. One isolated
CNA-BCC label is not a connected crystal cluster.

## Parent selection

The existing 500k endpoint was copied, without modifying coordinates, to:

`common/validated_parent_N1000_T1_P18.res`

SHA-256:

`7e406f2b61fc128cf919327341723516e88824c44104a88e84fb0d4fc09c00a0`

`common/run_segment.sh` was updated so all future branches copy this exact file
as `start_config.res`.

The original 50k-input liquid remains in `common/` for provenance. It was not
deleted or overwritten.

## Fresh validation pilots from the selected parent

Two new 200-cycle runs began from the selected parent with `vmax=0.001`.

| Branch | Seed | Particle acceptance | Volume acceptance | Final density | Final eta |
|---|---:|---:|---:|---:|---:|
| `dr=0.01` | 51001 | 86.87% | 11.67% | 1.037497 | 0.543232 |
| `dr=0.04` | 54001 | 56.96% | 7.48% | 1.037719 | 0.543348 |

Structural results:

- `dr=0.01`: PTM 1000 OTHER; CNA 1000 OTHER; FCC/HCP cluster 0.
- `dr=0.04`: PTM 1000 OTHER; CNA 999 OTHER plus one isolated BCC; FCC/HCP
  cluster 0.

Both runs retained exact energy and virial bookkeeping within numerical
precision.

## What will and will not be propagated

The selected old 500k configuration itself is the parent for future runs.
The final configurations of the new 200-cycle pilots are validation artifacts;
they will not become the production parent. This preserves an identical
starting configuration for both `dr` branches.

## Phase 2 conclusion

The selected parent is a dense, mobile, independently verified liquid at the
requested `N=1000`, `T*=1`, `p*=18` simulation condition. No close-packed
cluster is detected by PTM or CNA. It is suitable for controlled medium-length
tests of `vmax` and subsequently for the two production branches.

