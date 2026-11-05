# Vmax search results and decision

## Outcome

Retain `vmax=0.0005` for the paper-displacement branch with `dr=0.01`.

This is a sampling-efficiency decision, not a nucleation-outcome decision.
The absence of visible nucleation in an earlier `dr=0.01` trajectory is not
evidence that `vmax` was insufficient.

## Stage A: broad screen

Seven 5000-cycle runs used the same validated parent and seed:

| vmax | Volume acceptance | Particle acceptance |
|---:|---:|---:|
| 0.00020 | 44.93% | 86.69% |
| 0.00030 | 32.99% | 86.63% |
| 0.00040 | 26.18% | 86.69% |
| 0.00050 | 21.02% | 86.73% |
| 0.00065 | 16.44% | 86.70% |
| 0.00080 | 12.91% | 86.82% |
| 0.00100 | 10.22% | 86.84% |

The monotonic acceptance curve is physically sensible. Particle acceptance is
independent of the tested volume proposal width within stochastic variation.

## Stage B: replicated comparison

The candidates `0.00020`, `0.00030`, and `0.00050` were each run for 10000
cycles with seeds 86101, 86201, and 86301. Every run started independently
from the identical validated parent. None used another candidate's endpoint.

| vmax | Volume acceptance range | Mean acceptance | Mean density IACT (sample intervals) | Mean effective density samples |
|---:|---:|---:|---:|---:|
| 0.00020 | 45.88--46.43% | 46.24% | 22.68 | 4.65 |
| 0.00030 | 33.59--34.80% | 34.32% | 18.66 | 5.80 |
| 0.00050 | 21.63--22.63% | 22.03% | 15.66 | 7.78 |

The autocorrelation estimates are necessarily noisy for rare, correlated NpT
volume fluctuations, but `0.0005` has the best average effective-sample count
of the replicated candidates. It also has extensive successful history in the
completed segmented 3M campaigns and exact energy/virial bookkeeping.

## Interpretation

Smaller values accept more often but move `ln(V)` less per accepted proposal.
The search provides no evidence that their higher acceptance improves density
exploration. Values above `0.0005` rapidly fall below 20% acceptance and were
not promoted merely because the crude `acceptance*vmax^2` screening proxy
increases; that proxy does not account for the bias of accepted steps toward
small magnitudes.

The observed density IACT is a diagnostic, not a physical kinetic observable.
Changing `vmax` changes the volume-move proposal dynamics. Therefore the value
must be frozen before generating trajectories intended for kinetic comparison.

## Fixed setting for the next study

- `dr=0.01`, matching the paper's kinetic MC displacement statement;
- `vmax=0.0005`;
- `succ=0`, so neither move width is automatically adjusted;
- `N=1000`, `T*=1`, `p*=18`;
- 1000 particle attempts and one volume attempt per MC cycle;
- no swaps;
- independent replicates start from the same validated parent and use distinct
  seeds.

Raw and aggregate tables are under `runs/stage_a/` and `runs/stage_b/`.

