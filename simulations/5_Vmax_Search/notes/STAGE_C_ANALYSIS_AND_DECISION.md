# Stage C analysis and Vmax decision

## Data used

Stage C contains 15 completed runs: five `vmax` values, three seeds each,
`20000` cycles, and `nsamp=25`.

IACT is calculated from the saved density series in the second half of each run.
Because `nsamp=25`, one IACT unit means one saved density sample, or 25 MC
cycles.

## Aggregate second-half summary

| vmax | volume acceptance | mean IACT | median IACT | mean ESS | mean density |
|---:|---:|---:|---:|---:|---:|
| 0.00040 | 26.21% | 50.94 | 37.22 | 9.38 | 1.03711 |
| 0.00050 | 21.18% | 83.19 | 82.35 | 4.90 | 1.03793 |
| 0.00060 | 17.77% | 70.44 | 71.85 | 6.13 | 1.03831 |
| 0.00065 | 16.47% | 91.95 | 87.41 | 4.39 | 1.03737 |
| 0.00070 | 15.27% | 84.68 | 90.65 | 4.81 | 1.03738 |

From this main second-half metric, `vmax=0.0004` is the strongest candidate:
it has the lowest mean IACT, lowest median IACT, highest mean ESS, and still
has healthy volume acceptance around 26%.

The high ESS for `0.0004` is not caused by one lucky seed. The seed-level
second-half IACT values are:

| vmax | seed 87101 | seed 87201 | seed 87301 |
|---:|---:|---:|---:|
| 0.00040 | 31.92 | 83.69 | 37.22 |
| 0.00050 | 96.74 | 82.35 | 70.49 |
| 0.00060 | 92.07 | 47.39 | 71.85 |
| 0.00065 | 85.38 | 87.41 | 103.08 |
| 0.00070 | 90.65 | 92.79 | 70.60 |

So `0.0004` has two clearly good seeds and one slower seed. `0.0006` has one
good seed and two slower seeds. `0.0005` is more uniformly moderate-to-slow in
the full second-half IACT estimate.

## Block-wise check

To test whether one long-window IACT estimate was misleading, the trajectories
were also split into 5000-cycle blocks. The late blocks give this mean IACT
across the three seeds:

| vmax | 10000-15000 cycles | 15000-20000 cycles |
|---:|---:|---:|
| 0.00040 | 37.98 | 42.08 |
| 0.00050 | 37.01 | 34.06 |
| 0.00060 | 54.45 | 42.57 |
| 0.00065 | 65.00 | 54.93 |
| 0.00070 | 70.32 | 39.80 |

This adds nuance. In shorter late blocks, `0.0005` also looks good. But over
the full second-half window, `0.0005` has a larger IACT, meaning it carries
slower long-time density correlation across the complete 10000-cycle analysis
window. Since our goal is robust NpT density fluctuation sampling, the full
second-half metric should carry more weight than a favorable short block.

## Interpretation

The refined scan does not support moving above `vmax=0.0005`. Higher values
reduce volume acceptance and do not give a robust IACT or ESS improvement.
`vmax=0.0006` is somewhat better than `0.0005` in the full-window mean IACT/ESS,
but it is not the minimum and it costs acceptance. `0.00065` and `0.00070` are
worse by the sampling-efficiency criteria.

The real comparison is therefore between `0.0004` and `0.0005`:

- `0.0004`: best full-window IACT/ESS, healthy 26% volume acceptance, but one
  seed is slower than the other two.
- `0.0005`: historically used and still acceptable, but Stage C does not show
  it as the best density-sampling choice.

## Recommended decision

Use `vmax=0.0004` for the next `dr=0.01` NpT production branch, unless there is
a separate reason to preserve exact continuity with older `vmax=0.0005`
campaigns.

This is a proposal-efficiency choice. It should be described as improving NpT
volume/density fluctuation sampling, not as physically densifying the system or
forcing nucleation.

## Generated files

- `plots/stage_c/stage_c_summary_acceptance_iact_ess_density.png`
- `plots/stage_c/stage_c_seed_consistency.png`
- `plots/stage_c/stage_c_density_traces.png`
- `plots/stage_c/stage_c_block_iact.png`
- `plots/stage_c/stage_c_bookkeeping.png`
- `runs/stage_c/stage_c_block_iact.csv`
- `runs/stage_c/stage_c_bookkeeping.csv`

## Bookkeeping

Maximum absolute final energy bookkeeping difference: `3.865e-12`.
Maximum absolute final virial bookkeeping difference: `4.729e-11`.
These are roundoff-level values.
