# MC–NPT guided reconstruction

This is my living notebook for reconnecting with this project. It is written
to be read slowly and updated while I work. I do not need to understand every
Fortran line before I can run or analyse the simulation responsibly.

## The one-sentence picture

The program repeatedly proposes either a particle displacement or a box-volume
change, accepts or rejects that proposal with an NPT Monte Carlo rule, and
periodically records the evolving energy, density, packing fraction and move
acceptance.

> Terminology note: the program is a Metropolis NPT Monte Carlo engine. The
> project sometimes describes the sequence of small particle moves as kinetic
> Monte Carlo. It does not use an event catalogue or a residence-time clock,
> which are features of rejection-free/event-driven KMC.

## How I will rebuild my understanding

I will work from the outside inward:

1. Learn the map of the project.
2. Follow one small run from input to output.
3. Learn what every important output means.
4. Connect the acceptance physics I remember to the exact code.
5. Change one parameter at a time in a controlled tiny experiment.
6. Write a routine for launching, monitoring and analysing future runs.

The rule for this notebook is: every new code detail must answer a physical or
practical question. Details with no current purpose can wait.

---

# Session 1 — Find the path through the project

## 1. The four-layer map

```text
Source/                         the Monte Carlo physics engine (Fortran)
   ↓ compiled executable
4_Clean_NoSwap_Replication/     the controlled scientific experiment
   ↓ run wrappers
dr_0.01/ and dr_0.04/           actual runs with two displacement sizes
   ↓ generated files
analysis/                       checks and scientific interpretation
```

The older folders `1_Trial_Tests_500N/`, `2_1000_atoms/` and
`3_Tests_for_codes/` are valuable history, but they are not the best entrance.
For now I treat them as the laboratory archive. I begin with the cleaner
replication workflow.

## 2. What each important file is responsible for

| File or directory | Plain-language role |
|---|---|
| `Source/mc_npt.f` | Main loop: chooses particle or volume moves and decides when to sample. |
| `Source/mcmove.f` | Proposes one particle displacement and applies its acceptance test. |
| `Source/mcvol.f` | Proposes a logarithmic volume change, rescales all coordinates, and applies the NPT acceptance test. |
| `Source/ener.f`, `eneri.f`, `toterg.f` | Potential-energy and virial calculations. |
| `Source/readdat.f` | Reads the simulation input, model parameters and restart configuration. |
| `Source/sample.f` | Defines the numbers written to the diagnostic outputs. |
| `4_Clean_NoSwap_Replication/common/run_segment.sh` | Creates and runs one reproducible segment. |
| `4_Clean_NoSwap_Replication/common/run_campaign.sh` | Chains segments together to make a long restartable campaign. |
| `4_Clean_NoSwap_Replication/notes/` | Existing detailed scientific record and decisions. |

## 3. The path taken by one production segment

```text
run_campaign.sh
    |
    +-- chooses the next segment, seed and starting configuration
    |
    +-- calls run_segment.sh
            |
            +-- creates fort.15       simulation controls
            +-- creates fort.25       Yukawa model controls
            +-- creates fort.11       starting/restart configuration
            +-- runs ./mc_npt
                    |
                    +-- run_metrics.dat
                    +-- traj.lammpstrj
                    +-- fort.21 -> final_config.res
                    +-- fort.66 -> sampled_data.dat
                    +-- out
```

This is the backbone of the whole project. If I can explain this path, I am no
longer lost even if some functions inside the executable are still unfamiliar.

## 4. The current clean physical experiment

Both clean branches use the same validated liquid parent and the same physical
conditions:

- particles: `N = 1000`
- reduced temperature: `T* = 1`
- imposed reduced pressure: `p* = 18`
- inverse screening length: `kappa*sigma = 6`
- cutoff: `rc = 3.5 sigma`
- particle attempts per MC cycle: `1000`
- volume attempts per MC cycle: `1`
- swap moves: none

Only the maximum particle displacement differs:

- `dr_0.01`: `dr = 0.01 sigma`
- `dr_0.04`: `dr = 0.04 sigma`

That is scientifically useful: differences between these branches should be
attributable to the displacement scale, subject to stochastic uncertainty.

## 5. First output landmarks

Do not memorise these yet. The purpose is only to know where to look.

| Output | First interpretation |
|---|---|
| `manifest.txt` | Provenance: parameters, seed, parent configuration, hashes and completion. |
| `run_metrics.dat` | Best file for monitoring thermodynamic state and acceptance. |
| `sampled_data.dat` | Older compact sampling output: cycle, energy/particle, continuous pressure estimator, density. |
| `traj.lammpstrj` | Coordinate trajectory for structural analysis and visualisation. |
| `final_config.res` | Restart state passed to the next segment. |
| `out` | Human-readable program messages and final consistency checks. |

Important warning: `p_continuous` is the ideal plus continuous-force virial
contribution. For this hard-core Yukawa model it is **not** the full mechanical
pressure because the hard-core contact contribution is absent. The imposed
NPT pressure is separately recorded as `imposed_pressure`.

## 6. My first active checkpoint

Before Session 2, I should answer these in my own words. Short answers are
enough.

1. Which file chooses whether the next proposal is a particle move or a volume
   move?
2. Which two files contain the acceptance rules I already remember physically?
3. Which input file says how many particle and volume moves occur per cycle?
4. If I want to know whether a run is still advancing, which output should I
   inspect first?
5. What is the one controlled difference between `dr_0.01` and `dr_0.04`?

### My answers

Write here, or answer Codex in the chat:

1.mc_npt.f
2.mcmove and vol.f
3. fort.15 since it has the simulation controls
4. manifest.txt at the end states completed if not maybe still running
5.the displacement is different 0.01 vs 0.04

### Codex feedback

These answers show that I have found the backbone correctly.

1. Correct: `mc_npt.f` owns the main loop and chooses the proposal type.
2. Correct idea; the exact filenames are `mcmove.f` and `mcvol.f`.
3. Correct: `fort.15` contains `ndispl` and `nvol`.
4. Partly correct in an important way: `manifest.txt` records completion. While
   a job is running, the last cycle in `run_metrics.dat` is the clearest sign
   that it is advancing. For a segmented campaign, the campaign log/state also
   says which segments have completed.
5. Correct: only the maximum proposed particle displacement differs.

## 7. What comes next

In Session 2 I will trace a tiny run. Before running it I will predict:

- how many particle attempts it should make;
- how many volume attempts it should make;
- how many sampled rows it should write;
- which files prove that it completed cleanly.

Then I will run it and compare prediction with observation. This will be the
first complete bridge between the input, the main loop and the output.

---

# Progress log

- [x] Identified the clean workflow and the four-layer project map.
- [x] Identified the main input-to-output path.
- [x] Answered the Session 1 checkpoint in my own words.
- [ ] Traced and ran one tiny simulation.
- [ ] Built the complete output-column dictionary.
- [ ] Connected both acceptance equations to code line by line.
- [ ] Ran controlled parameter experiments.
- [ ] Wrote my final run–monitor–analyse routine.

---

# Session 2 — Predict before reading the result

The existing run `dr_0.01/pilot_200` is our first small simulation. Its
`fort.15` contains:

```text
ibeg nequil prod nsamp iseed
1    0      200  100   41001

dr    vmax   succ
0.01  0.001  0.0

ndispl nvol
1000   1
```

Plain-language translation:

- start from a restart configuration (`ibeg = 1`);
- skip equilibration and perform 200 production cycles;
- sample once every 100 production cycles;
- use random seed 41001;
- propose small particle displacements with maximum width 0.01;
- use a logarithmic volume-step width of 0.001;
- target 1000 particle proposals and one volume proposal per cycle.

## My prediction

Before looking at `run_metrics.dat` or the bottom of `out`, fill these in:

1. Approximately how many particle moves should be attempted over 200 cycles?
2. Approximately how many volume moves should be attempted?
3. At which cycle numbers should `run_metrics.dat` contain sampled states?
   Remember that the program records the initial state before cycle 1.
4. Name two independent signs that the run completed cleanly.

### My answers

1. each run 1000:1, so partcile moves = 200*1000
2.Similarly volume moves 200*1
3.0, 100 and 200 since nsamp is 100
4.in run_metric if we have all the entries as in ans. 3 or checking the status manifest maybe

### Prediction versus observation

My predictions were correct:

| Quantity | My expectation | Observed |
|---|---:|---:|
| particle attempts | about 200000 | 200004 |
| volume attempts | about 200 | 196 |
| sampled cycles | 0, 100, 200 | 0, 100, 200 |

The small move-count differences arise because each of the 1001 selections per
cycle randomly chooses a particle or volume proposal. The input controls the
probability and hence the expected count, not an exact quota.

My proposed completion evidence was also sound:

- `run_metrics.dat` reaches cycle 200;
- `manifest.txt` contains `completed_utc` and the final metrics row.

There is an even stronger numerical check in `out`. At the end, the program
recalculates the total energy and virial independently and compares each with
the incrementally maintained value. The differences were approximately
`8e-13` and `3e-12`. This tells me that the accepted-move bookkeeping remained
self-consistent throughout this pilot.

## A small but revealing subtlety

The program performs `ndispl + nvol = 1001` proposal selections per cycle, but
chooses the proposal type randomly each time. Therefore 1000 particle and one
volume move are **expected averages per cycle**, not rigid counts. The observed
totals can differ slightly from 200000 and 200. This is our first example of a
code detail changing how we interpret an input parameter.

---

# Session 3 — Learn to read one metrics row

The cycle-200 row is:

```text
200  -0.865507247990  0.993891026762  0.520400124691  18.0
-1.03858119085  200004  177211  0.88603728  196  22  0.11224490
```

The columns, in order, are:

| # | Name | Meaning |
|---:|---|---|
| 1 | `cycle` | completed production cycle |
| 2 | `energy_per_particle` | total configurational energy divided by particle count |
| 3 | `density` | number density, `N/V` |
| 4 | `eta` | packing fraction, `pi*rho/6` for unit-diameter particles |
| 5 | `imposed_pressure` | pressure used by the NPT acceptance rule |
| 6 | `p_continuous` | ideal plus continuous virial estimator; not full hard-core pressure |
| 7 | `attempts` | cumulative particle attempts |
| 8 | `accepted` | cumulative accepted particle attempts |
| 9 | `acceptance` | `accepted/attempts` |
| 10 | `volume_attempts` | cumulative volume attempts |
| 11 | `volume_accepted` | cumulative accepted volume attempts |
| 12 | `volume_acceptance` | `volume_accepted/volume_attempts` |

## My reading of the row

Complete these in ordinary language, without worrying about polished wording:

1. The final density is approximately 0.99389.
2. The particle acceptance is approximately 88.6 percent.
3. The volume acceptance is approximately 11.22 percent.
4. Out of 196 volume proposals, 22 were accepted.
5. Is column 6 expected to equal the imposed pressure of 18? Why or why not? Not because the virial term is not included

### Codex feedback

Answers 1–4 are exactly right. For answer 5, my conclusion is right but the
reason needs one correction: `p_continuous` **does include** the ideal term and
the continuous Yukawa force-virial term. It excludes the discontinuous
hard-core contact contribution. Therefore it is not the complete mechanical
pressure and is not expected to equal the imposed NPT pressure of 18.

In symbols, the reported estimator is

```text
p_continuous = rho*T + Vir/(3*V)
```

but the full hard-core system pressure would also require the contact term.

---

# Session 4 — Follow one particle proposal

Now I connect physics I remember to `Source/mcmove.f`. One call to `MCMOVE`
does the following:

1. Increase the particle-attempt counter.
2. Choose one particle uniformly at random.
3. Calculate that particle's interactions at its old position: `eno`.
4. Propose independent random changes in `x`, `y` and `z`, each lying between
   `-dr/2` and `+dr/2`.
5. Calculate its interactions at the proposed position: `enn`.
6. Draw a uniform random number and apply the Metropolis test.
7. If accepted, update the total energy, total virial and particle coordinates.

The exact acceptance line is:

```fortran
IF (RANF(Iseed).LT.EXP(-BETA*(enn-eno))) THEN
```

Define

```text
DeltaU = enn - eno
beta   = 1/T
```

Then the acceptance probability is effectively

```text
P_accept = min(1, exp(-beta*DeltaU)).
```

The explicit `min(1, ...)` is unnecessary in the code: the random number lies
between 0 and 1. If `DeltaU < 0`, the exponential is greater than 1, so the
comparison always succeeds.

## What the energy routines contribute

`ENERI` sums the selected particle's interaction with every other particle,
using minimum-image periodic boundaries. For each pair it calls `ENER`:

- `r < sigma`: hard-core overlap, represented by energy `1e20`;
- `sigma <= r <= rc`: signed Yukawa interaction;
- `r > rc`: zero interaction.

Thus a proposal that creates an overlap has an enormous positive `DeltaU` and
is rejected in practice. Same-type pairs use a positive Yukawa sign and
opposite-type pairs use a negative sign.

## My particle-move checkpoint

1. For `dr = 0.01`, what numerical interval can each Cartesian coordinate
   change by in one proposal?
2. At `T = 1`, what happens to a move with `DeltaU = -0.2`?
3. At `T = 1`, what is the approximate acceptance probability for
   `DeltaU = +0.2`? (`exp(-0.2)` is enough.)
4. Does a rejected move alter the stored coordinates or running energy?
5. Why is a hard-core overlap almost certainly rejected?

### My answers

1.-0.05 - 0.05
2.exp(-(-0.2))/1 is higher energy than previous so it is tested against a random number and checked for Pacc
3. Pacc = 1 and accepted
4.No it doens't , just move count increases and the coordinates and energy stays the same with no update
5. because it will enormoulsy increase the energy making Pacc very low

### Codex feedback

Answers 4 and 5 are correct. The corrections to 1–3 are:

1. The interval is `[-0.005, +0.005]`, because the code multiplies `dr=0.01`
   by a random number in `[-0.5,+0.5]`.
2. `DeltaU=-0.2` means the proposed energy is lower. At `T=1`,
   `exp(-DeltaU)=exp(0.2)>1`, so the move is always accepted.
3. For `DeltaU=+0.2`, `P_accept=exp(-0.2)=0.819` approximately. Such an
   uphill move is not guaranteed, but it still has about an 82% chance.

My initial mistakes were factor-of-ten and sign-direction mistakes, not a
failure of the overall picture. The safe habit is to ask: **is the proposed
energy lower or higher?** Then substitute the sign into the exponential.

---

# Session 5 — Follow one volume proposal

`Source/mcvol.f` changes the whole box rather than one particle. One call does:

1. Record the old volume `Vo = BOX^3`.
2. Propose a change uniformly in log-volume:

   ```text
   ln(Vn) = ln(Vo) + uniform(-vmax/2, +vmax/2)
   ```

3. Convert the new volume to a cubic box length, `Ln = Vn^(1/3)`.
4. Reject immediately if the new half-box would be no larger than the fixed
   interaction cutoff.
5. Scale every coordinate by `Ln/Lo`. Fractional positions therefore remain
   the same while all real-space separations expand or contract with the box.
6. Recalculate the complete energy and virial in the proposed box.
7. Apply the NPT acceptance rule.
8. If rejected, scale the coordinates back and restore the old box exactly.

## Reading the acceptance rule

The code can be written as

```text
Delta = DeltaU + P*(Vn-Vo) - (N+1)*T*ln(Vn/Vo)
P_accept = min(1, exp(-beta*Delta))
```

where `DeltaU = Un-Uo` and `beta=1/T`.

The three competing pieces are:

- `DeltaU`: how scaling all separations changes the interaction energy;
- `P*DeltaV`: imposed pressure penalises expansion and favours compression;
- `-(N+1)T*ln(Vn/Vo)`: configurational/Jacobian factor, which favours the
  greater positional phase space of a larger volume.

Why `N+1` rather than only `N`? Scaling the `N` particle coordinates supplies
the usual `N` factor. The extra `1` comes from proposing moves uniformly in
`ln(V)` rather than uniformly in `V` (the proposal/Hastings Jacobian).

## What `vmax = 0.001` means

It does **not** mean `DeltaV` lies between `-0.0005` and `+0.0005`. It means

```text
Delta ln(V) lies in [-0.0005, +0.0005].
```

Equivalently, `Vn/Vo` lies between `exp(-0.0005)` and `exp(+0.0005)`, very
close to a relative volume change of `-0.05%` to `+0.05%`.

## My volume-move checkpoint

1. In a volume proposal, is only one particle moved or are all coordinates
   scaled?
2. If the box length grows, what happens to every pair separation before
   periodic wrapping is considered?
3. At positive pressure, does the `P*DeltaV` term favour expansion or
   compression?
4. If a proposal is rejected, what two kinds of state must be restored?
5. Is `vmax=0.001` an absolute volume change or a log-relative step width?
6. In one sentence, why does the volume rule contain more than just
   `exp(-beta*DeltaU)`?

### My answers

1.all are scaled
2. the pair seperation increases ?
3.compression it opposes it, technically I didn't get it much
4. one is the box should rescale back and then the atoms should do corresonding
5.in log scale
6.THis is a thing I coudln't figured out

### Codex feedback

I got four of the six ideas:

1. Correct: all coordinates are scaled together.
2. Correct: when the box grows, every pair separation grows by the same scale
   factor.
3. Correct conclusion: positive external pressure favours compression. A
   useful picture is a hand pushing a piston inward. For expansion,
   `DeltaV>0`, so `P*DeltaV>0`; this raises `Delta` and reduces acceptance.
   For compression, `DeltaV<0`; the pressure contribution helps acceptance.
4. Correct: the old box dimensions and the correspondingly scaled particle
   coordinates must both be restored. The running energy and virial were not
   overwritten before acceptance, so they already retain their old values.
5. Correct: `vmax` is the width of the proposal in `ln(V)`.
6. The missing idea is: because the volume changes, the rule must include not
   only interaction energy but also work against the external pressure and the
   change in available coordinate-space.

The short memory version is:

```text
particle move: interaction-energy cost
volume move:   interaction energy + pressure work + volume/entropy factor
```

## Two-sentence retry

Complete these in my own words:

1. External pressure opposes expansion because it is acting against it.
2. A volume move needs extra NPT terms because to account for extra work and the additional entropy favor

### Codex feedback on my retry

The concepts are correct. A polished version is:

1. External pressure opposes expansion because expansion performs positive
   work against the pressure exerted by the surroundings.
2. A volume move needs the extra NPT terms to account for pressure-volume work
   and the change in configurational entropy caused by changing the available
   volume.

I can now keep the three contributions separate:

```text
DeltaU                         internal interaction-energy change
P*DeltaV                       work against the external pressure
-(N+1)T*ln(Vn/Vo)              configurational entropy/Jacobian contribution
```

---

# Session 6 — First controlled comparison

We already have two short pilots, so we can learn from them without spending
more CPU time:

```text
dr_0.01/pilot_200
dr_0.04/pilot_200
```

I checked their provenance before comparing them:

- identical starting-configuration SHA-256 hashes;
- identical executable SHA-256 hashes;
- same `N`, `T`, imposed pressure, `vmax`, move frequencies and cycle count;
- different particle step width: `dr=0.01` versus `dr=0.04`;
- different random seeds: 41001 versus 44001.

The seed difference means these are different stochastic realisations, not a
move-for-move paired experiment. The controlled **physical/algorithmic
parameter** under study is still `dr`. A robust conclusion should eventually
use longer runs and/or multiple seeds rather than treating one 200-cycle pilot
as definitive.

## Predict before comparing the final rows

For each Cartesian component:

```text
dr=0.01 proposes Delta x in [-0.005,+0.005]
dr=0.04 proposes Delta x in [-0.020,+0.020]
```

Larger proposals move farther when accepted, but are more likely to produce a
large positive energy change or a hard-core overlap. This creates the familiar
Monte Carlo tradeoff between step size and acceptance.

### My predictions

1. Which branch should have the higher particle acceptance: `dr_0.01` or
   `dr_0.04`? Why?
2. Should changing `dr` directly change the mathematical volume-move
   acceptance rule?
3. If the final density or energy differs slightly after only 200 cycles, is
   that alone enough to claim a systematic effect of `dr`? Why?
4. Which metric would I compare first to test my answer to question 1?

### My answers

1.0.01 because , I believe higher accpetance because larger steps can create compltely new things thus detla U may not benegative
2. no, vol still depends on vmax
3. maybe mostly but it is combined effect of both dr and vmax
4. the particle acceptance

### Codex feedback and pilot result

Answers 1, 2 and 4 are correct. For answer 3, 200 cycles from one seed are not
enough to claim a systematic effect: stochastic fluctuations could produce a
small energy or density difference. `vmax` is the same in both pilots, so it
is a controlled parameter rather than a difference between them.

| Pilot | `dr` | particle acceptance | volume acceptance | final density |
|---|---:|---:|---:|---:|
| `dr_0.01/pilot_200` | 0.01 | 88.60% | 11.22% | 0.99389 |
| `dr_0.04/pilot_200` | 0.04 | 61.79% | 12.50% | 0.99365 |

The main prediction is supported: increasing the proposal width lowers
particle acceptance substantially. The volume acceptances and final densities
are close enough that this tiny pilot alone does not establish meaningful
differences in those quantities.

## Does the acceptance contrast survive the long run?

Both production campaigns completed 3,000,000 cycles. Summing the final move
counters from all 12 segments gives:

| Campaign | particle acceptance | volume acceptance |
|---|---:|---:|
| `dr_0.01/production_3M` | 86.66% | 21.43% |
| `dr_0.04/production_3M` | 57.44% | 21.92% |

So the particle-acceptance contrast is persistent, whereas the volume
acceptance is very similar. This is consistent with `dr` entering the particle
proposal directly but not entering the mathematical volume-move rule.

Acceptance alone does not tell us which `dr` is scientifically better. A
smaller `dr` accepts more moves but each accepted move is shorter; a larger
`dr` accepts fewer moves but travels farther per accepted move. For equilibrium
sampling we would study decorrelation or effective sample size. For a
kinetic interpretation, changing `dr` also changes the effective dynamics and
must be justified as part of the model.

## My evidence-based conclusion

Finish these two statements:

1. The data strongly support the conclusion that increasing `dr` ______.
2. The data do not yet prove that one `dr` is better because ______.

### My answers

1. reduces acceptance probability
2. then you don't get a good variation in the sample not much decorrelation

### Codex feedback

1. Correct: increasing `dr` reduces the observed particle acceptance.
2. Decorrelation is the correct quantity to think about, but acceptance alone
   does not tell me whether variation is good or bad. Tiny accepted steps can
   decorrelate slowly; larger but less frequently accepted steps can sometimes
   decorrelate faster. I would need an autocorrelation or effective-sample-size
   measurement before deciding which branch samples equilibrium more
   efficiently.

---

# Session 7 — My run, monitor, verify and analyse routine

This is the practical routine I can return to when I feel lost.

## A. Before launching a new campaign

I write down or verify:

1. What scientific question does the run answer?
2. What is the starting configuration, and has it been validated?
3. Which executable is used?
4. What are `N`, `T`, `P`, `dr`, `vmax`, `ndispl`, `nvol`, cycle count,
   sampling interval and seed?
5. Which single parameter is intentionally different from the control?
6. Is there enough disk space?
7. Does a run directory with this name already exist?

The last question prevents accidentally overwriting or duplicating work.

## B. Know what the wrapper creates

For this clean workflow, `run_segment.sh` creates a new directory and records:

```text
fort.11        restart/starting configuration
fort.15        simulation controls
fort.25        interaction-model controls
manifest.txt   provenance and hashes
input_used.in  preserved copy of fort.15
model_used.in  preserved copy of fort.25
```

It then runs `mc_npt` and produces the metrics, trajectory, final restart and
program output. `run_campaign.sh` chains these segments and keeps cumulative
cycle state.

## C. Monitor without changing the job

From the project root:

```bash
./4_Clean_NoSwap_Replication/production_status.sh
```

I read the report in this order:

1. `Observed progress`: completed segments plus the active local segment.
2. `Completed clean segments`: safely checkpointed progress.
3. `Status`: active, complete, not running, or not launched.
4. `Latest metrics`: most recent sampled state.
5. Campaign-log tail: confirmation of segment completion or an error.
6. Free disk space.

For a single segment I can also inspect:

```bash
tail -n 3 PATH_TO_RUN/run_metrics.dat
tail -n 30 PATH_TO_RUN/out
```

## D. Verify completion rather than assuming it

A trustworthy completed segment has several independent signals:

- `manifest.txt` contains `completed_utc`;
- `run_metrics.dat` reaches the requested final cycle;
- `out` reaches `Done ... out of ...`;
- final recomputed and running energy agree closely;
- final recomputed and running virial agree closely;
- `final_config.res` exists and is nonempty.

A completed campaign additionally has:

- its control `state.txt` equal to the requested total cycles;
- `Campaign complete` at the end of its campaign log;
- every expected segment directory and restart file.

## E. Analyse in layers

I do not jump directly from “job finished” to “nucleation occurred.” I ask:

1. **Numerical health:** energy/virial consistency and no errors.
2. **Thermodynamic trajectory:** energy, density, packing fraction and move
   acceptance versus cumulative cycle.
3. **Structural trajectory:** PTM, CNA, largest connected crystalline cluster
   and their persistence across frames.
4. **Independent confirmation:** RDFs and visual inspection around any
   persistent growth event.
5. **Comparison:** treat `dr=0.01` and `dr=0.04` as separate dynamical
   experiments; do not declare a result from one isolated classifier spike.

For the current completed campaigns, the prepared structural-analysis command
is:

```bash
./4_Clean_NoSwap_Replication/analyze_both_when_complete.sh
```

It is expected to write:

```text
4_Clean_NoSwap_Replication/analysis/production_3M/
    dr_0.01_structure_timeseries.csv
    dr_0.04_structure_timeseries.csv
```

As of 3 July 2026, both 3M campaigns are complete, but those production
structure-timeseries files have not yet been generated.

## My hands-on checkpoint

Run this yourself in the project terminal:

```bash
./4_Clean_NoSwap_Replication/production_status.sh
```

Then write:

1. Status of `dr_0.01`: ______
2. Status of `dr_0.04`: ______
3. One piece of evidence for completion: ______
4. The next scientific action—not another simulation—is: ______

---

# Session 8 — Configuration lineage: the family tree of the runs

Configuration lineage answers one question: **which physical state became the
input to which run?** Without this, two beautifully analysed simulations might
still be scientifically incomparable.

## The production family tree

```text
earlier p*=18 metastable liquid
common/metastable_liquid_N1000_T1_P18.res
SHA256 c6264c65...
        |
        +-- continued through the earlier 50k -> 500k history
                |
                +-- 500k endpoint, copied unchanged as
                    common/validated_parent_N1000_T1_P18.res
                    SHA256 7e406f2b...
                          |
                          +-- dr_0.01/production_3M_seg001
                          |       -> seg002 -> ... -> seg012
                          |
                          +-- dr_0.04/production_3M_seg001
                                  -> seg002 -> ... -> seg012
```

These two `.res` files are not duplicates: their hashes differ because they
represent different points in the earlier trajectory. The validated parent is
the later state chosen for production.

## Why the parent was considered suitable

The existing validation record describes the selected 500k endpoint as:

- density approximately 1.03708;
- packing fraction approximately 0.54301;
- no hard-core overlaps;
- no PTM crystal classifications;
- one isolated CNA-BCC classification only;
- no strong tested low-index structure-factor peak.

Taken together, these checks were considered consistent with a metastable
liquid rather than an already crystallised parent. No single classifier was
used as the entire argument.

## Why the pilots are not ancestors of production

Several 200-cycle pilots start from one of the parent configurations, but their
final configurations are validation outputs only. Production deliberately
returns to the identical validated parent in both branches.

That prevents this accidental comparison:

```text
dr=0.01 starts from parent A
dr=0.04 starts from an evolved output of parent A
```

Instead, both branches begin from byte-identical `7e406f2b...` input files.
Their first-segment manifests independently record that same starting hash and
the same executable hash.

## How a segment chain continues

Within each branch:

```text
seg001/start_config.res = validated parent
seg001/final_config.res = seg002/start_config.res
seg002/final_config.res = seg003/start_config.res
...
seg011/final_config.res = seg012/start_config.res
```

This is an exact file handoff, not an approximate comparison. For example, in
`dr_0.01`, the SHA-256 of the segment-1 final configuration is
`f16c0172...`, and the segment-2 starting configuration has exactly the same
hash. The same check succeeds in the other branch.

Each segment uses a new seed, but continues the coordinates, types, box, `dr`
and `vmax` stored in the previous restart. Segmentation therefore provides
checkpoints and manageable files; it is intended to represent one continuous
Monte Carlo campaign.

## What a SHA-256 hash tells me

A hash is a compact fingerprint of a file:

- matching hashes provide strong evidence that the file contents are exactly
  identical;
- different hashes tell me the contents differ;
- a hash does not by itself say whether a configuration is physically valid.

Physical validation and identity checking are complementary: structural tests
say the parent is suitable, while the hash says both branches received that
same parent.

## My lineage checkpoint

1. Which of the two common `.res` files is the direct production parent?
2. Did production begin from either 200-cycle pilot endpoint?
3. What proves that both branches started from identical configuration data?
4. What becomes the starting configuration of segment 2?
5. Does a matching SHA-256 prove that a liquid is physically valid? What does
   it prove?

### My answers
I don't know where find te has of final structure in each segement, but I can find the hash of the segment start configuration as it is in manifest
1. 
2. No it didn't
3. the start cofig hashes in both seg001 is same
4. final of seg 1
5. no it doesn't mean that, only physical validation on observing the nucleation by means like clustering or ovito seeing RDF

### Codex feedback

My understanding of the chain is good:

1. The direct production parent is
   `common/validated_parent_N1000_T1_P18.res`.
2. Correct: neither 200-cycle pilot endpoint became a production parent.
3. Correct: both `seg001` manifests record the same start hash,
   `7e406f2b...`.
4. Correct: segment 1's final configuration becomes segment 2's starting
   configuration.
5. Correct central idea: matching hashes prove identical file contents, not
   physical validity. Overlap checks, PTM, CNA, RDF and related diagnostics
   support the claim that the parent is a liquid. Observing later nucleation is
   a different scientific question.

My note about not finding the final hash is also correct. `manifest.txt`
records the starting hash but does not currently record a labelled final hash.
The handoff can still be verified directly:

```bash
sha256sum \
  4_Clean_NoSwap_Replication/dr_0.01/production_3M_seg001/final_config.res \
  4_Clean_NoSwap_Replication/dr_0.01/production_3M_seg002/start_config.res
```

If the two printed hashes match, the handoff was exact.

---

# Session 9 — Who does what in the campaign scripts?

There are two levels of orchestration:

```text
run_campaign.sh                 manager of the complete journey
       |
       +-- run_segment.sh       builder and runner of one checkpoint
       +-- run_segment.sh
       +-- ...
       +-- run_segment.sh
```

## `run_segment.sh`: one sealed experiment

It receives:

```text
BRANCH RUN_NAME CYCLES SEED [VMAX [START_CONFIG [NSAMP]]]
```

It then:

1. Converts the branch name into `dr=0.01` or `dr=0.04`.
2. Refuses to continue if the requested run directory already exists.
3. Copies the chosen parent to `start_config.res` and `fort.11`.
4. Copies the executable into the run directory.
5. Writes `fort.15` and `fort.25` from explicit parameters.
6. Records provenance and hashes in `manifest.txt`.
7. Runs `./mc_npt > out 2>&1`.
8. Copies the final restart and sampled output to clearly named files.
9. Appends completion time and final metrics to the manifest.

The word “sealed” here means that the segment directory retains the exact
input, executable, parent fingerprint, output and completion evidence needed
to reconstruct what happened.

## `run_campaign.sh`: chain and checkpoint manager

For production it was called with the conceptual values:

```text
branch          dr_0.01 or dr_0.04
campaign        production_3M
total           3000000 cycles
segment         250000 cycles
seed base       91001 or 94001
sampling        every 1000 cycles
vmax            fixed internally at 0.0005
```

It creates a control directory containing:

| File | Job |
|---|---|
| `state.txt` | Number of safely completed campaign cycles. |
| `campaign_manifest.txt` | Campaign-level parameters and completion time. |
| `cumulative_metrics.dat` | Segment metrics combined onto one cumulative cycle axis. |

For each segment it:

1. Calculates the segment number and seed.
2. Chooses the parent: validated parent for segment 1, previous final restart
   thereafter.
3. Calls `run_segment.sh`.
4. Appends that segment's metrics with the correct cycle offset.
5. Updates `state.txt` only after the segment completes successfully.

That final ordering matters. If a segment crashes halfway through,
`state.txt` still represents the last clean checkpoint rather than claiming
unfinished work as completed.

## Seeds across the campaign

The seed is:

```text
seed = seed_base + segment_index - 1
```

So `dr_0.01` uses 91001 for segment 1, 91002 for segment 2, and so on. The new
seed avoids replaying the same pseudo-random sequence after every restart.
It does not reset particle coordinates or erase physical continuity.

## Smoke runs versus production

Directories such as `phase4_smoke_seg001` and `phase4_smoke2_seg001` are short
engineering tests of segmentation and restart plumbing. Like the pilots, they
are not ancestors of `production_3M`. Their manifests are useful examples of
the same bookkeeping system on smaller runs.

## My campaign checkpoint

1. Which script knows the total target of 3,000,000 cycles?
2. Which script actually creates `fort.15` and executes `mc_npt`?
3. Why is `state.txt` updated only after a segment succeeds?
4. Where does segment 5 obtain its starting configuration?
5. Does changing the seed between segments break the continuous physical
   trajectory?
6. Are the `phase4_smoke...` endpoints part of the production lineage?

### My answers

1.campaign.sh
2.segment.sh
3.to keep alog of previous step if fails can restart from there with different seed
4.from end of 4
5.No I don't think so, it's just randomising the volume/dr and no velocities are changed so issue
6.smoke has no relation to production it's just to check campaign is running

### Codex feedback

My campaign-level picture is correct. The exact script names are
`run_campaign.sh` and `run_segment.sh`.

1. `run_campaign.sh` knows the total target and manages the segment chain.
2. `run_segment.sh` writes `fort.15` and actually executes `mc_npt`.
3. Correct central idea: delaying the `state.txt` update ensures that it always
   marks the last successfully completed checkpoint. On resumption the manager
   can reconstruct which segment should come next. The seed is determined from
   that segment number; recovery does not require inventing a seed by hand.
4. Correct: segment 5 receives segment 4's `final_config.res`.
5. Correct conclusion, with one refinement: this Monte Carlo state has no
   velocities. Physical continuity comes from preserving the coordinates,
   particle types, box and model parameters. The new seed merely supplies a
   fresh sequence of future random proposals.
6. Correct: the smoke campaigns test the machinery but do not belong to the
   production family tree.

The compact memory version is:

```text
campaign script = where are we in the whole journey?
segment script  = how do I construct and run this one checkpoint?
```

---

# Session 10 — Read the production trajectory before naming the event

Both branches begin from the same validated parent. Their cycle-zero metrics
are therefore identical:

```text
energy/N = -0.95937883
density  =  1.03708041
```

I first compare broad thermodynamic behaviour. The final 500,000-cycle means
are:

| Branch | mean energy/N | mean density | particle acceptance | volume acceptance |
|---|---:|---:|---:|---:|
| `dr_0.01` | -0.94660 | 1.04468 | 86.76% | 21.55% |
| `dr_0.04` | -0.80909 | 1.10217 | 57.84% | 22.83% |

The final sampled states are:

| Branch | final energy/N | final density |
|---|---:|---:|
| `dr_0.01` | -0.96742 | 1.04609 |
| `dr_0.04` | -0.81700 | 1.10378 |

This is not a small end-point fluctuation. The averages over an entire 500k
window show that the `dr_0.04` trajectory occupies a distinctly denser and
higher-energy state late in the campaign. The similar volume acceptance rates
also show that this contrast is not simply one branch having a broken or
frozen volume mover.

Thermodynamic data alone do **not** identify the structure. A density change
can alert me to a transition, but it cannot tell me whether the new state is
BCC, FCC, another ordered structure, a dense disordered state, or an analysis
artifact. That requires the coordinate trajectories and structural
classifiers in Session 11.

## My thermodynamic checkpoint

Answer in ordinary language:

1. Why is comparing the final 500k mean stronger than comparing only the last
   row?
2. Which branch shows the clear late-time thermodynamic change?
3. Does the table by itself prove that crystallisation occurred? Why?
4. Since both branches started identically, what are two broad explanations
   for why their later trajectories differ?
5. What data must we examine next to decide whether a persistent crystalline
   structure formed?

### My answers

Write here, or answer Codex in the chat.
becuase it inlcudes a good past and averaging over the values helps in better understanding
2. what is this ?
3. no it just tells one has higher density 
4. dr is diff, then seeds can also matter a little as they direct the randomisation
5. structure parameters

### Codex feedback

1. Correct. The last row is one fluctuating snapshot, whereas the mean uses
   501 sampled states across a long late-time window. A persistent difference
   in that mean is harder to explain as one accidental fluctuation.
2. “Late-time thermodynamic change” means that the energy and density move to
   and remain in a noticeably different regime near the later part of the
   trajectory. Here it is `dr_0.04`: its late density is about `1.102`, well
   above its initial `1.037` and the `dr_0.01` late mean of about `1.045`.
3. Correct. The table establishes a density and energy difference, not the
   microscopic arrangement of particles. It therefore cannot by itself prove
   crystallisation.
4. Correct. The branches use different `dr` values, which change their Monte
   Carlo dynamics, and different random-number sequences, which can make a
   stochastic transition occur at different times or in only one finite run.
   With one trajectory per branch, these effects cannot yet be cleanly
   separated.
5. Correct direction. More specifically, I need the structural trajectory:
   PTM/CNA classifications and the size and persistence of connected
   crystalline clusters across many frames. RDFs and visual inspection can
   then provide independent confirmation.

The important discipline from this session is:

```text
thermodynamic change = evidence that something happened
structural persistence = evidence about what happened
```

---

# Session 11 — Distinguish a crystalline fluctuation from persistent growth

The production structure files contain one row for every saved trajectory
frame. Two classifiers independently assign a local-environment label to each
particle:

- PTM: polyhedral template matching;
- CNA: common-neighbour analysis.

Both report per-particle labels such as FCC, HCP, BCC and other. The quantity
I use next is not the classifier output by itself, but the size of the
**largest connected domain of neighbouring particles that are labelled FCC or
HCP**. A few isolated crystalline-looking particles are common in a liquid;
hundreds joined into one persistent connected domain are qualitatively
different.

## What the two trajectories show

| Measurement | `dr_0.01` | `dr_0.04` |
|---|---:|---:|
| maximum PTM connected cluster | 13 | 559 |
| final PTM connected cluster | 4 | 484 |
| mean PTM cluster, final 500k | 2.6 | 509.0 |
| maximum CNA connected cluster | 12 | 535 |
| final CNA connected cluster | 3 | 440 |
| mean CNA cluster, final 500k | 2.4 | 465.3 |

For `dr_0.01`, neither classifier ever finds a connected cluster of 50
particles. Its small clusters appear and disappear, which is consistent with
ordinary liquid fluctuations.

For `dr_0.04`, the PTM connected cluster first reaches:

```text
100 particles at cycle 2,049,000
250 particles at cycle 2,112,000
500 particles at cycle 2,285,000
```

CNA independently reaches 100 at the same sampled cycle and later grows above
500. Most importantly, during **all 501 frames** in the final 500k window,
both classifiers report a largest connected cluster above 100 particles. This
is persistence, not a one-frame classifier spike.

The late cluster contains a mixture of FCC- and HCP-labelled local
environments. At cycle 3,000,000, PTM labels 160 particles FCC and 324 HCP,
forming a connected FCC/HCP cluster of 484. This supports a persistent close-
packed crystalline domain; the mixture may include stacking faults rather
than representing a single perfect bulk lattice.

## What I may and may not conclude

The combined evidence is strong:

```text
thermodynamic change in dr_0.04
        +
large connected crystalline cluster
        +
persistence across hundreds of frames
        +
agreement between PTM and CNA
```

Therefore `dr_0.04` shows persistent crystalline growth during this campaign,
while `dr_0.01` remains liquid-like by these diagnostics.

I should not yet call cycle 2,049,000 the exact nucleation time. It is simply
the first saved frame at which the chosen cluster threshold of 100 is crossed.
An exact transition-state or commitment time would require a defined order
parameter, finer temporal resolution and/or committor-style analysis.

I also cannot conclude from one campaign per `dr` that `dr=0.04` universally
causes crystallisation and `dr=0.01` prevents it. The result establishes what
happened in these two trajectories. Replicate seeds are needed to estimate
nucleation probabilities or rates and separate stochastic timing from a
systematic `dr` effect.

## My structural checkpoint

1. Why is a connected cluster of 500 particles stronger evidence than 500
   crystalline labels scattered independently through the box?
2. What distinguishes the small clusters in `dr_0.01` from the late cluster
   in `dr_0.04`?
3. Why does agreement between PTM and CNA strengthen the conclusion?
4. Can I call cycle 2,049,000 the exact nucleation time? Why or why not?
5. What additional simulations are required before claiming that changing
   `dr` systematically changes the nucleation probability or rate?

### My answers

1. A connected cluster is stronger evidence because it shows that the local
   environment labels are not just scattered independently through the box,
   but are spatially linked into a larger structure.
2. The small clusters in `dr_0.01` are tiny and short-lived local-environment
   fluctuations, whereas the late structure in `dr_0.04` is a larger and
   persistent connected domain that survives across many frames.
3. Agreement between PTM and CNA strengthens the conclusion because two
   independent local-environment analyses point to the same spatially linked
   domain.
4. No. Cycle 2,049,000 is only the first saved frame where the chosen
   threshold is crossed, not an exact nucleation time.
5. I would need more independent trajectories with multiple seeds for each
   `dr` value before claiming that changing `dr` systematically changes the
   nucleation probability or rate.

Note for Session 11: PTM and CNA are most useful as indicators of local
structural environment, but the stronger interpretation comes from whether
those labels form a spatially connected and persistent domain over time.

---

# Session 12 — Turn the evidence into a concise conclusion

The goal of this session is to stop collecting raw observations and instead ask
what I can say with confidence. I want a short, defensible summary of what the
current trajectories show, what remains uncertain, and what the next useful
experiment would be.

## My closing checkpoint

1. What is the strongest claim that the current evidence supports?
2. What is the most important limitation of this conclusion?
3. What would I test next if I wanted to strengthen the argument?

### My answers

1. In this trajectory, the larger `dr` case appears to produce a larger and
   more persistent crystalline-like domain than the smaller `dr` case.
2. The main limitation is that this conclusion is tied to the specific
   thermodynamic conditions and the single trajectory analysed here, so it is
   not yet a general rule.
3. I would strengthen the argument by extending the run beyond 3 million
   cycles and testing additional `dr` values, ideally with multiple seeds.