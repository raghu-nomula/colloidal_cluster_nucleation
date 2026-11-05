# Engineering change log — what changed and why it helps

## Purpose of this document

The phase notes describe scientific goals and results. This document instead
tracks the engineering changes made to the existing code and workflow. It
distinguishes changes that affect Monte Carlo sampling from changes that only
improve safety, observability, reproducibility or analysis.

## What was not changed

The following physical implementation already existed and was not replaced in
this clean-replication work:

- hard-core rejection below `r=sigma`;
- signed Yukawa pair energy for equal/opposite charges;
- Yukawa pair virial expression;
- periodic minimum-image distances;
- Metropolis particle displacement acceptance;
- logarithmic-volume NpT acceptance;
- full energy recalculation during a volume move;
- one-to-one restart storage of particle type and coordinates;
- LAMMPS trajectory output;
- the random-number generator.

Thus, the main pair potential and NpT acceptance physics were not rewritten
during Phases 1--5. The only selected Monte Carlo parameter change is the
explicit, documented choice `vmax=0.0005`; separate `dr=0.01` and `dr=0.04`
branches are preserved.

## Fortran source changes

### 1. `Source/sample.f`: added transparent interval diagnostics

Previous behavior:

- `fort.66` stored cycle, energy per particle, a force-virial pressure value
  and density.
- Particle and volume acceptance appeared only near the end of `out`.
- Packing fraction and imposed pressure were not written beside sampled data.
- The force-virial pressure could easily be mistaken for total pressure even
  though it omits the hard-core contact contribution.

New behavior:

- Added subroutine `SAMPLEMETRICS`.
- It writes `run_metrics.dat` containing cycle, energy per particle, density,
  packing fraction, imposed pressure, explicitly named `p_continuous`, particle
  attempts/acceptances and volume attempts/acceptances.
- Division by zero is avoided when no moves have yet been attempted.

How this helps:

- We can prove that particles are moving rather than guessing from `dr`.
- We can tune `vmax` quantitatively.
- Density and `eta=pi*rho/6` can be compared directly with the paper.
- The incomplete hard-core pressure diagnostic is no longer presented as the
  imposed NpT pressure.

Physics impact: none. This observes existing state and counters but does not
alter proposal generation or acceptance.

### 2. `Source/mc_npt.f`: connected metrics to sampling

Previous behavior:

- No dedicated interval metrics file.
- Progress reporting evaluated `MOD(icycl,ncycl/5)`, which can divide by zero
  when a test contains fewer than five cycles.

New behavior:

- Opens `run_metrics.dat` on Fortran unit 67 and writes column descriptions.
- Initializes move counters before the initial diagnostic record.
- Calls `SAMPLEMETRICS` at cycle zero and every production sampling interval.
- Closes the metrics file cleanly.
- Uses `MAX(1,ncycl/5)` for safe short regression tests.

How this helps:

- Every saved trajectory frame has corresponding thermodynamic/acceptance
  diagnostics.
- Tiny smoke tests can validate scripts without crashing.

Physics impact: none. The Monte Carlo loop and acceptance calls are unchanged.

### 3. `Source/readdat.f`: fail early on invalid runs

Previous behavior:

- Several invalid input/restart conditions could continue until a confusing
  failure or memory error.
- A restart could overwrite `NPART` after the original size check.
- Invalid particle types were not rejected.
- Small boxes silently reduced the requested cutoff.
- A dormant shifted-potential call passed the wrong number of arguments.

New behavior:

- Rejects non-positive particle count, temperature, density or `NSAMP`.
- Rejects negative move counts.
- Rechecks restart particle count against array bounds and the even-number
  requirement for a 1:1 mixture.
- Requires every restart particle type to be 1 or 2.
- Warns if the finite box reduces the requested cutoff.
- Corrects the dormant shifted-potential call signature.

How this helps:

- Long jobs fail immediately instead of wasting hours with malformed inputs.
- Restarts cannot silently introduce an invalid binary mixture.
- Small-system tests cannot unknowingly claim to use the paper's cutoff.

Physics impact: none for valid current inputs (`shift=.false.` and a sufficiently
large box). Invalid simulations now stop deliberately.

## Executable snapshot

The modified Fortran source was compiled and copied to:

`4_Clean_NoSwap_Replication/common/mc_npt_phase1`

SHA-256:

`2e6b96bc732a66da48f6ed2151a10a349effd634667a3cd08a04b8995282adca`

Every run copies this exact binary into its run directory and records the hash.
Later edits to `Source/` therefore cannot silently change an active campaign.

## Run-workflow changes

### 4. `common/run_segment.sh`: immutable self-contained segments

Previous workflow:

- Individual run scripts contained hard-coded paths and parameters.
- Output names were reused and sometimes deleted at the beginning of a run.
- Provenance had to be reconstructed manually.

New workflow:

- Creates a new run directory and refuses to overwrite an existing one.
- Accepts branch, run name, cycles, seed, `vmax`, parent and sampling interval.
- Maps the branch name to fixed `dr=0.01` or `dr=0.04`.
- Copies the exact parent, executable and inputs into the run directory.
- Correctly overwrites `dr/vmax` in the restart because `READDAT` uses restart
  values when `ibeg=1`.
- Records time, host, parameters, resolved parent path, parent hash and
  executable hash in `manifest.txt`.
- Preserves final restart, trajectory, original sample data and new metrics.

How this helps:

- Every segment can be audited or reproduced independently.
- The two branches differ only in explicitly recorded choices.
- Accidental output destruction is prevented.

Physics impact: it sets the requested fixed move parameters but does not change
the Fortran algorithms.

### 5. `common/run_campaign.sh`: restart-chained long runs

New behavior:

- Splits a long campaign into bounded sequential segments.
- Uses the validated parent only for segment 1.
- Uses each clean segment endpoint as the next segment's input.
- Assigns deterministic distinct seeds by segment.
- Fixes selected `vmax=0.0005` for both branches.
- Writes atomic completion state and cumulative metrics.
- Removes duplicated cycle-zero rows at restart boundaries.
- Can resume from the latest completed segment.
- Does not automatically delete or overwrite an interrupted segment.

How this helps:

- A power interruption loses at most the active segment.
- Default Fortran integer counters remain safely below overflow.
- Three million cycles acquire a single cumulative metric time axis.
- Restart continuity can be checked by SHA-256.

Physics impact: each segment changes the RNG seed, as the earlier manually
chained runs also did. Coordinates and particle types are transferred exactly.

### 6. Background launchers

Added:

- `common/launch_campaign_nohup.sh`
- `launch_both_3M.sh`

They launch the two branch campaigns with `nohup`, record PID/log locations,
check for existing campaigns and check free disk space.

How this helps:

- Closing the terminal or VS Code does not terminate the jobs.
- Duplicate production campaigns are not launched accidentally.

Physics impact: none. System suspension still pauses all computation.

### 7. `production_status.sh`: non-destructive monitoring

It reports cleanly completed cycles, the latest saved local trajectory cycle,
recent metrics, log messages and disk usage. It now treats recently modified
trajectory output as evidence of activity when the process PID belongs to a
different namespace and is invisible to `ps`.

How this helps:

- Monitoring does not touch simulation state.
- It avoids falsely declaring host-terminal jobs dead from inside the Codex
  sandbox's separate PID namespace.

Physics impact: none.

## Analysis changes

### 8. `analysis/validate_structure.py`

Added direct checks independent of the disputed q6 analysis:

- composition;
- periodic minimum separation and overlap count;
- density and packing fraction;
- neighbor count and unlike-charge neighbor fraction;
- total, same-charge and unlike-charge RDFs;
- low-index static structure-factor warning metric;
- OVITO-ready snapshot export.

How this helps: establishes whether a parent is physically valid and liquid-like
without assuming the previous q6 thresholds are correct.

### 9. `analysis/ovito_structure.py`

Added independent OVITO Polyhedral Template Matching and adaptive Common
Neighbor Analysis, plus connected FCC/HCP cluster counting and marked output.

How this helps: a structural claim is no longer based on one custom q6 code.

### 10. `analysis/analyze_campaign.py`

Added whole-campaign PTM/CNA time-series analysis over every saved frame and
every segment. It writes cumulative cycle, structure counts and largest
FCC/HCP cluster, skipping duplicated restart-boundary frames.

### 11. `analyze_both_when_complete.sh`

Refuses to analyse until both state files report 3,000,000 completed cycles,
then produces separate structural time series for each branch.

How this helps: incomplete campaigns cannot accidentally be presented as final
comparisons.

## Selected parameter changes and evidence

The only common proposal parameter deliberately changed from the previous long
runs is:

```text
vmax: 0.005 (old runs) -> 0.0005 (new campaigns)
```

Reason: old volume acceptance was about 2.2%. Controlled tests gave about 20%
acceptance at 0.0005 while retaining liquid structure and exact energy/virial
bookkeeping. `vmax` is a proposal size in `ln(V)`, not a particle diameter.

`dr=0.01` is retained as one branch. `dr=0.04` is an explicitly separate
comparison requested by the user; raw MC-cycle time must not be equated between
the branches.

