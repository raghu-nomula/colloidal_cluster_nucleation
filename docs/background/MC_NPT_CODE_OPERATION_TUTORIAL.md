# MC–NPT code operation tutorial

This is the practical handoff for running the signed hard-core Yukawa MC–NPT
code without reconstructing the workflow from memory. It covers a small local
example, safe background execution, monitoring, restart behavior, long
segmented production, and the dedicated `vmax` search.

## 1. What the program simulates

The current production model is fixed as follows:

- `N = 1000`, with 500 type-1 and 500 type-2 particles;
- hard-core diameter `sigma = 1`;
- reduced temperature `T* = 1`;
- imposed reduced pressure `p* = 18`;
- `kappa*sigma = 6` and `rc = 3.5 sigma`;
- signed Yukawa interactions: repulsive for equal types and attractive for
  unlike types;
- no particle-type swap moves;
- paper displacement parameter `dr = 0.01` for the primary kinetic study;
- 1000 particle attempts and one logarithmic-volume attempt per MC cycle.

The potential and unit derivation are documented separately in
`YUKAWA_POTENTIAL_REDUCED_UNITS_AND_SYSTEM_SETUP.pdf`.

## 2. Files to know

| Path | Purpose |
|---|---|
| `Source/` | Fortran source and development executable. |
| `4_Clean_NoSwap_Replication/common/mc_npt_phase1` | Frozen executable used by the reproducible campaigns. |
| `4_Clean_NoSwap_Replication/common/validated_parent_N1000_T1_P18.res` | Validated common liquid parent. |
| `4_Clean_NoSwap_Replication/common/run_segment.sh` | Creates and runs one immutable segment. |
| `4_Clean_NoSwap_Replication/launch_both_3M.sh` | Existing two-branch production launcher. Do not use for the new paper-only campaign without first reviewing the branch choice. |
| `4_Clean_NoSwap_Replication/production_status.sh` | Read-only status report for the existing 3M campaigns. |
| `5_Vmax_Search/` | New independent search with `dr=0.01` fixed. |

Never edit a completed run directory. Create a new, clearly named run instead.
The manifest and hashes are evidence of exactly what was run.

## 3. Inputs and restart precedence

The executable reads traditional Fortran unit files:

- `fort.15`: MC controls (`ibeg`, cycles, seed, move counts, nominal state);
- `fort.25`: potential controls (`sigma`, cutoff, `kappa`, shift/tail flags);
- `fort.11`: starting restart when `ibeg=1` or `2`.

The restart format begins with:

```text
L   L/2
N
dr  vmax
x_1 y_1 z_1 type_1
...
```

With `ibeg=1`, the restart box, types, coordinates, `dr`, and `vmax` are read
from `fort.11`. Therefore changing only the corresponding line in `fort.15`
does not change the move sizes. The supplied run scripts correctly rewrite the
third restart line.

With `ibeg=0`, the input density creates a new lattice. With `ibeg=2`, a restart
is rescaled to the requested density. Production continuation normally uses
`ibeg=1`.

## 4. Safest small example

From the project root, run a new 1000-cycle example:

```bash
./4_Clean_NoSwap_Replication/common/run_segment.sh \
    dr_0.01 tutorial_example_1k 1000 91001 0.0005 \
    ./4_Clean_NoSwap_Replication/common/validated_parent_N1000_T1_P18.res 100
```

This creates:

```text
4_Clean_NoSwap_Replication/dr_0.01/tutorial_example_1k/
```

The command refuses to overwrite that directory. To repeat the experiment,
use a new name and normally a new seed.

Important outputs are:

- `manifest.txt`: parameters, hashes, start/end timestamps;
- `out`: human-readable progress and final energy/virial consistency;
- `run_metrics.dat`: sampled energy, density, packing fraction and acceptance;
- `traj.lammpstrj`: saved coordinate frames;
- `final_config.res`: full-precision restart for an intentional continuation;
- `sampled_data.dat`: legacy compact sampled output.

Check completion:

```bash
grep completed_utc 4_Clean_NoSwap_Replication/dr_0.01/tutorial_example_1k/manifest.txt
tail -n 20 4_Clean_NoSwap_Replication/dr_0.01/tutorial_example_1k/out
tail -n 2 4_Clean_NoSwap_Replication/dr_0.01/tutorial_example_1k/run_metrics.dat
```

The end of `out` must show that recomputed and running energy agree to floating
point precision.

## 5. Running locally in the background

For a single command, use `nohup` and `setsid` from a normal terminal:

```bash
mkdir -p local_logs
nohup setsid ./4_Clean_NoSwap_Replication/common/run_segment.sh \
    dr_0.01 my_long_run 250000 92001 0.0005 \
    ./4_Clean_NoSwap_Replication/common/validated_parent_N1000_T1_P18.res 500 \
    > local_logs/my_long_run.log 2>&1 < /dev/null &
echo $! > local_logs/my_long_run.pid
```

You may now close the terminal or VS Code. `nohup` prevents terminal hangup
from killing the command; `setsid` separates it from the terminal session.
This does not protect against shutting down the computer, a crash, or loss of
power. Suspending the computer pauses the process until wake-up.

Check whether it is alive:

```bash
pid=$(cat local_logs/my_long_run.pid)
kill -0 "$pid" && echo RUNNING || echo NOT_RUNNING
ps -p "$pid" -o pid,etime,%cpu,%mem,stat,cmd
tail -f local_logs/my_long_run.log
```

`tail -f` is only a viewer; press `Ctrl-C` to leave the viewer without stopping
the simulation. Because Fortran output can be buffered, the metrics file is
often more informative:

```bash
tail -n 2 4_Clean_NoSwap_Replication/dr_0.01/my_long_run/run_metrics.dat
```

Stop only when genuinely intended:

```bash
kill "$(cat local_logs/my_long_run.pid)"
```

A killed segment may lack `final_config.res` and `completed_utc`; never treat
such a directory as a completed scientific run.

## 6. Long production should be segmented

Do not make one irreplaceable multi-million-cycle process. Use sequential
segments, for example 250,000 cycles each. Segment 1 starts from the immutable
validated parent; segment 2 starts from segment 1's `final_config.res`, and so
on. Each segment gets a new random seed and its own manifest.

Segmentation gives:

- restart points after machine interruption;
- bounded file sizes and counters;
- explicit provenance at every boundary;
- easy status percentages;
- a place to verify energy consistency before continuing.

When joining trajectories, remove the duplicate boundary frame: the last frame
of one segment is the first state of the next segment.

For unattended campaigns, use a wrapper script that calls `run_segment.sh`
sequentially and launches that wrapper with `nohup setsid`. Never run dependent
segments simultaneously.

## 7. Choosing seeds and parents

- Independent replicates: same parent and parameters, different seeds.
- Continuation: previous completed endpoint as parent, new seed.
- Parameter comparison: every candidate starts from the same parent; do not
  chain candidate endpoints.
- Record the seed and verify parent/executable hashes in every manifest.

Changing `dr` or `vmax` changes the proposal dynamics. Do not merge time axes
from runs with different values as if they formed one kinetic trajectory.

## 8. Dedicated `vmax` search

The paper explicitly uses `dr=0.01`; the new tuning campaign therefore fixes
that value. Stage A tests:

```text
0.00020  0.00030  0.00040  0.00050  0.00065  0.00080  0.00100
```

Every run has 5000 cycles, the same seed, and the same validated parent. Launch:

```bash
cd 5_Vmax_Search
./launch_stage_a.sh
```

Monitor from any terminal:

```bash
./status.sh
```

When complete:

```bash
./analyze.py runs/stage_a
```

The search does not require 3M cycles. Stage A rejects obviously inefficient
regions. The implemented Stage B compares `0.00020`, `0.00030`, and `0.00050`
using three independent seeds and 10,000 cycles per run:

```bash
./launch_stage_b.sh
./status_stage_b.sh
```

## 9. How `vmax` should—and should not—be selected

The proposal is

```text
ln(V_new) = ln(V_old) + (random - 0.5)*vmax.
```

Very small `vmax` gives high acceptance but tiny box motion. Very large `vmax`
gives large proposals that are mostly rejected. The useful region balances
step size and acceptance.

The Stage-A table includes `acceptance*vmax^2` as a screening proxy. It is not
an exact diffusion coefficient, since accepted proposals are not uniformly
distributed. Stage B replication is required. A broad stable plateau is more
credible than the largest value in one noisy column.

Most importantly, do not select `vmax` because nucleation did or did not occur
in a tuning run. Nucleation is rare and stochastic. Using it as the tuning
criterion would select the simulation algorithm from the desired outcome.
Once `vmax` is selected, freeze it before comparing nucleation trajectories.

## 10. Routine status and sanity checklist

Before launch:

1. Confirm available disk space with `df -h .`.
2. Confirm no same-named directory exists.
3. Confirm `dr=0.01`, selected fixed `vmax`, `T*=1`, `p*=18`.
4. Confirm the common parent and executable hashes.
5. Estimate trajectory size from cycles divided by `NSAMP`.

During execution:

1. Check PID state and elapsed CPU time.
2. Inspect the latest `run_metrics.dat` line.
3. Watch particle and volume acceptance for abrupt changes.
4. Watch density and packing fraction for obviously invalid values.
5. Check disk space periodically.

After completion:

1. Require `completed_utc` in the manifest.
2. Require final energy and virial bookkeeping agreement in `out`.
3. Verify 1000 particles, 500 of each type, and no `r<1` overlaps.
4. Preserve the complete run directory.
5. Perform structural analysis using persistent clusters and multiple
   classifiers, not a single noisy order-parameter spike.

## 11. Common mistakes

- Treating `sigma` as radius: it is the particle diameter.
- Treating packing fraction `eta` as number density: `rho*=6 eta/pi`.
- Editing only `fort.15` during a restart: `fort.11` overrides move sizes.
- Reusing a completed directory name.
- Starting all parameter candidates from each other's endpoints.
- Assuming a high acceptance fraction automatically means efficient sampling.
- Changing `vmax` after production starts and still calling it one kinetic run.
- Declaring nucleation from one frame or one classifier.
- Assuming `nohup` survives a computer shutdown—it only survives terminal
  closure.
