# Parameter and decision register

## Fixed physical model

- Particles: 1000.
- Composition: 1:1 positive/negative, 500 of each.
- Diameter: `sigma = 1`.
- Temperature: `T* = 1`.
- Pressure for current brute-force study: `p* = 18`.
- Yukawa screening: `kappa*sigma = 6`.
- Potential cutoff: `3.5 sigma`.
- Hard core: separations below `sigma` forbidden.
- Swap moves: disabled.
- Particle displacement attempts: 1000 per MC cycle.
- Volume attempts: one per MC cycle.

## Displacement branches

- Keep both `dr=0.01` and `dr=0.04` as separately labelled experiments.
- Never merge their MC-cycle time axes.
- Never describe `dr=0.04` as specified by the paper for brute-force `p*=18`;
  the paper explicitly mentions it for FFS branching trajectories, while the
  `p*=18` displacement is not stated.

## Volume moves

- `vmax` changes `ln(V)`, not particle coordinates and not `sigma`.
- It is treated as an algorithmic sampling parameter.
- Automatic adjustment remains disabled during kinetic production.
- Selected production value: `vmax=0.0005`.
- In 1000-cycle tests it gave 19.6--20.5% volume acceptance, compared with
  approximately 9.3--9.4% for `vmax=0.001`.
- Completed 2000-cycle checks gave 21.6--22.0% volume acceptance.
- A later dedicated `dr=0.01` search screened seven values and replicated
  `vmax=0.0002`, `0.0003` and `0.0005` with three seeds. `0.0005` was retained:
  it gave 21.6--22.6% volume acceptance and the best mean density effective
  sample count among the replicated candidates. See
  `5_Vmax_Search/RESULTS_AND_DECISION.md`.

## Pressure reporting

- `p*=18` in the NpT acceptance is the imposed pressure.
- `p_continuous` omits the hard-core contact contribution.
- Negative `p_continuous` values do not mean the imposed NpT pressure is
  negative and do not imply the hard core is absent from acceptance.
- A proper hard-core pressure estimator may be added later using virtual
  volume perturbations, but it is not required to enforce the NpT state.

## Parent configuration

- Production parent: `common/validated_parent_N1000_T1_P18.res`.
- Both branches must verify its SHA-256 before running.
- 200-cycle validation outputs must not replace it.

## Structural evidence

- Do not declare nucleation from a single `q6` peak.
- Require independent PTM/CNA evidence, persistent cluster growth and a
  trajectory consistent with crystal growth.
- RDFs and charge-resolved RDFs are supporting structural evidence.
