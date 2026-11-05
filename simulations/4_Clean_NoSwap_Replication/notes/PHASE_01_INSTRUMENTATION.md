# Phase 1 — instrumentation and controlled branches

## Purpose

The existing simulations recorded final acceptance statistics in `out`, but
did not place them beside density and energy at every sampling interval. Runs
were also distributed over several directories and restart time reset to zero
at every segment. Phase 1 created a clean, reproducible experiment area and
made the diagnostics explicit before any new long simulation.

This phase did not attempt to demonstrate nucleation.

## Scope of the comparison

Two no-swap experiments were created at the same thermodynamic state:

- `dr_0.01`: maximum particle displacement `0.01 sigma`.
- `dr_0.04`: maximum particle displacement `0.04 sigma`.

The branches use the same number of particles, potential, pressure,
temperature, volume-move size and initial coordinates. Different random seeds
are required for independent stochastic trajectories.

The `dr=0.04` branch is a requested comparison. It must not be interpreted on
the same raw MC-cycle time scale as `dr=0.01`, because accepted displacement
sizes and therefore effective diffusion differ.

## Source-code changes

The following files in `Source/` were modified.

### `sample.f`

Added `SAMPLEMETRICS`, which writes `run_metrics.dat` (`fort.67`) containing:

1. MC cycle within the current segment;
2. energy per particle;
3. number density;
4. packing fraction `eta = pi*rho/6`;
5. imposed NpT pressure;
6. continuous-force virial pressure estimate;
7. particle attempts;
8. accepted particle moves;
9. particle acceptance fraction;
10. volume attempts;
11. accepted volume moves;
12. volume acceptance fraction.

The force-virial quantity is explicitly called `p_continuous`. It omits the
hard-core contact contribution and is not the total mechanical pressure.

### `mc_npt.f`

- Opens and labels `run_metrics.dat`.
- Records initial and sampled metrics.
- Prevents division by zero in progress reporting for runs shorter than five
  cycles by using `MAX(1,ncycl/5)`.

### `readdat.f`

Added checks for positive particle count, temperature, density and sampling
frequency; non-negative move counts; valid restart size; even particle count;
and particle types 1 or 2. It now warns if a small box silently reduces the
requested cutoff. A dormant shifted-potential call was corrected to pass the
required charge-sign argument.

## Build and regression test

The modified program was compiled with `gfortran`. A five-cycle restart test
used the previous 1.5-million-cycle configuration. The test confirmed:

- metrics were written at every requested sample;
- short-run progress reporting did not divide by zero;
- running and independently recomputed energy agreed;
- running and independently recomputed virial agreed;
- the restart retained 500 particles of each type.

The compiled executable was copied to:

`common/mc_npt_phase1`

SHA-256 at creation:

`2e6b96bc732a66da48f6ed2151a10a349effd634667a3cd08a04b8995282adca`

Every run copies this executable into its own run directory and stores its hash
in `manifest.txt`.

## Initial common configuration used in the first pilots

The first pair of pilots used:

`common/metastable_liquid_N1000_T1_P18.res`

This was the configuration used as input to the original 50k kinetic-MC run,
not the output of that run. Its SHA-256 is:

`c6264c653ea21f6ec507875f71bbbc28fe6cb4bd9730a0bfe63a9cb752b3fd31`

## Pilot parameters

Both initial pilots used:

- `N = 1000`
- `T* = 1.0`
- `p* = 18.0`
- `kappa*sigma = 6`
- `rc = 3.5 sigma`
- no swap moves
- 1000 displacement attempts per cycle
- one volume attempt per cycle
- 200 MC cycles
- `vmax = 0.001`
- fixed move sizes (`succ = 0`)

Only `dr` and random seed differed.

## Initial pilot results

| Branch | Seed | Particle acceptance | Volume acceptance | Final density | Final eta |
|---|---:|---:|---:|---:|---:|
| `dr=0.01` | 41001 | 88.60% | 11.22% | 0.993891 | 0.520400 |
| `dr=0.04` | 44001 | 61.79% | 12.50% | 0.993650 | 0.520274 |

The initial liquid was physically mobile. The earlier concern that nucleation
was absent because almost all moves were rejected was therefore ruled out.

## Run scripts

`common/run_segment.sh` creates a new immutable run directory, copies the
starting configuration and executable, overwrites restart `dr/vmax`, writes
the exact Fortran inputs, records hashes and host information, runs the
simulation, and preserves outputs.

`common/launch_nohup.sh` launches the runner through `nohup` so it can survive
terminal closure or logout on the user's normal Linux session.

No process can compute while the computer is suspended. During true system
sleep, CPU execution pauses and continues only after wake-up.

## Sandbox-specific event

An initial attempt to test `launch_nohup.sh` inside the Codex execution sandbox
was reaped when the tool session exited. No run directory or simulation output
was produced by that attempt. The pilots were immediately rerun as one
supervised parallel command and completed normally. This is a property of the
tool execution environment, not evidence that `nohup` fails in a normal Linux
terminal.

## Phase 1 conclusion

The instrumented code and controlled directory structure work. Both particle
move sizes yield substantial acceptance and stable short runs. The initial
common liquid was safe but relatively dilute for the later portion of the old
`p*=18` trajectory, so Phase 2 compared it with a denser existing liquid before
selecting the production parent.

