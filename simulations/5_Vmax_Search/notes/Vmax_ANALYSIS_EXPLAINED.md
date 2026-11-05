# Vmax analysis explained in plain language

## What question are we answering?

We are not asking which `vmax` makes nucleation happen in a short run.
That would be a dangerous criterion because nucleation is rare and noisy.

The actual question is:

> Which logarithmic-volume proposal width lets the NpT box sample volume and
> density fluctuations efficiently, without making volume moves fail too often?

For the next physical study, `dr=0.01` is fixed. So this search only tunes
the NpT volume-move proposal parameter `vmax`.

## What does `vmax` do?

`vmax` controls the size of attempted volume changes.

- Small `vmax`: proposed box changes are tiny. They are accepted often, but
  each accepted move barely changes the volume.
- Large `vmax`: proposed box changes are bigger. They explore volume faster
  when accepted, but many proposals are rejected.
- A useful `vmax` balances these two effects.

This is exactly why acceptance percentage alone is not enough.

## Stage A: broad screen

Stage A tested seven values once each:

| vmax | volume acceptance | particle acceptance |
|---:|---:|---:|
| 0.00020 | 44.93% | 86.69% |
| 0.00030 | 32.99% | 86.63% |
| 0.00040 | 26.18% | 86.69% |
| 0.00050 | 21.02% | 86.73% |
| 0.00065 | 16.44% | 86.70% |
| 0.00080 | 12.91% | 86.82% |
| 0.00100 | 10.22% | 86.84% |

This tells us two important things:

1. Increasing `vmax` decreases volume acceptance.
2. Particle acceptance stays almost unchanged.

So `vmax` is doing what it should: it mainly affects box-volume moves, not
particle-displacement moves.

Stage A alone does not prove the best value. It only tells us the useful
region. We then chose `0.00020`, `0.00030`, and `0.00050` for replicated
Stage B because they represent high, medium, and lower volume acceptance.

## Stage B: replicated comparison

Stage B ran three independent seeds for each candidate, each for 10000 MC
cycles. Every run started from the same validated parent configuration.

The important aggregate values are:

| vmax | mean volume acceptance | mean density, second half | mean density IACT | mean effective density samples |
|---:|---:|---:|---:|---:|
| 0.00020 | 46.24% | 1.03922 | 22.68 | 4.66 |
| 0.00030 | 34.32% | 1.03758 | 18.66 | 5.82 |
| 0.00050 | 22.03% | 1.03592 | 15.66 | 7.78 |

## Meaning of each analysis term

### `mean_density_second_half`

This is the actual measured density averaged over the second half of the run.
For a 10000-cycle run sampled every 50 cycles, this means the density from
cycles 5000 to 10000.

This is a physical observable.

Important point:

`vmax=0.0005` did not give the highest density. Its mean density was actually
slightly lower than the other two candidates in these short runs:

| vmax | mean density |
|---:|---:|
| 0.00020 | 1.03922 |
| 0.00030 | 1.03758 |
| 0.00050 | 1.03592 |

So we are not choosing `0.0005` because it makes the box denser.

### `density_iact_samples`

IACT means integrated autocorrelation time.

In simple words, it measures how slowly the density data forgets its previous
value.

If IACT is large, nearby saved density points are strongly correlated. The run
looks long on paper, but statistically it contains fewer independent density
fluctuations.

If IACT is smaller, density decorrelates faster. That is better for sampling.

In Stage B:

| vmax | mean density IACT |
|---:|---:|
| 0.00020 | 22.68 |
| 0.00030 | 18.66 |
| 0.00050 | 15.66 |

Lower is better here. `vmax=0.0005` had the lowest mean density IACT.

### `density_effective_samples`

This is not a density value.

It means:

> How many effectively independent density measurements did the correlated
> density trajectory contain?

It is estimated as:

```text
effective density samples = number of saved second-half density samples / IACT
```

For Stage B, the second half contains about 101 saved density points. If the
IACT is 20, then those 101 saved points behave roughly like only 5 independent
density samples.

In Stage B:

| vmax | mean effective density samples |
|---:|---:|
| 0.00020 | 4.66 |
| 0.00030 | 5.82 |
| 0.00050 | 7.78 |

Higher is better here. This is the main reason `0.0005` looked best among the
three replicated candidates.

## Why not choose the highest acceptance value?

`vmax=0.00020` had the highest volume acceptance, around 46%.

But high acceptance alone is not automatically good. If the volume proposal is
too small, the simulation accepts many moves that barely change the volume.
That can still give slow exploration of density fluctuations.

In our data, `0.00020` accepted more often but gave the worst effective density
sampling:

| vmax | volume acceptance | effective density samples |
|---:|---:|---:|
| 0.00020 | 46.24% | 4.66 |
| 0.00030 | 34.32% | 5.82 |
| 0.00050 | 22.03% | 7.78 |

So acceptance decreased, but sampling efficiency improved.

## Why not choose even larger `vmax`?

Stage A showed that larger values rapidly push the volume acceptance below
20%:

| vmax | volume acceptance |
|---:|---:|
| 0.00065 | 16.44% |
| 0.00080 | 12.91% |
| 0.00100 | 10.22% |

Those values may make larger attempted volume moves, but too many attempts are
rejected. Since Stage A was only one seed, we did not promote these larger
values into Stage B. The conservative choice was to compare values that still
had reasonable acceptance.

## Decision logic

The decision was not:

> `0.0005` creates higher density, therefore it may cause clusters.

That is not what the data shows.

The decision was:

> `0.0005` gives acceptable volume acceptance, stable particle acceptance,
> clean energy/virial bookkeeping, and the best replicated density-sampling
> efficiency among the tested Stage B candidates.

This makes `0.0005` a good algorithmic choice for NpT equilibration.

## Relation to nucleation

Better NpT volume sampling can help the liquid explore natural density
fluctuations under the imposed pressure. Those density fluctuations may matter
for nucleation.

But `vmax` should not be described as a physical knob that directly densifies
clusters or forces nucleation.

The correct interpretation is:

> By choosing `vmax=0.0005`, we avoid a volume proposal that is either too
> timid or too often rejected. This should improve the reliability of NpT
> density fluctuation sampling before nucleation trajectories are compared.

## Plots to generate

Run this from the project root:

```bash
python3 5_Vmax_Search/plot_vmax_analysis.py
```

It writes figures into:

```text
5_Vmax_Search/plots/
```

The intended figures are:

1. `stage_a_acceptance_vs_vmax.png`
   Shows that volume acceptance decreases as `vmax` increases, while particle
   acceptance stays flat.

2. `stage_b_acceptance_and_density.png`
   Shows Stage B replicated volume acceptance and actual mean density. This
   plot is important because it shows `0.0005` was not selected because it had
   the largest density.

3. `stage_b_iact_and_effective_samples.png`
   Shows the real selection criterion: lower density autocorrelation and higher
   effective independent density samples.

4. `stage_b_density_traces.png`
   Shows the raw density trajectories for the three seeds at each candidate
   `vmax`. The dashed line marks where the second-half analysis window starts.

## Final sentence for notes or paper draft

We retain `vmax=0.0005` because, among the replicated candidates, it provides
the best density-sampling efficiency while preserving acceptable volume-move
acceptance and exact bookkeeping. The choice improves NpT volume-fluctuation
sampling, but it should not be interpreted as directly biasing the system
toward higher density or nucleation.
