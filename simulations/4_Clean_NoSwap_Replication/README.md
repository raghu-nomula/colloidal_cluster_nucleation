# Clean no-swap replication

Detailed bookkeeping is maintained in [notes/00_INDEX.md](notes/00_INDEX.md).
The notes are the authoritative explanation of configuration lineage,
parameter decisions, validation results and known limitations.

This directory contains two controlled `p*=18` experiments that differ only
in maximum particle displacement:

- `dr_0.01`: natural small-step kinetic-MC control.
- `dr_0.04`: parallel displacement-size comparison requested for this study.

Both production branches start from the exact same validated liquid
`common/validated_parent_N1000_T1_P18.res` and use `N=1000`, `T*=1`, `p*=18`,
`kappa*sigma=6`, `rc=3.5 sigma`, no swaps, 1000 displacement attempts and one
volume attempt per MC cycle.

The first phase consists only of short pilots. Long production runs must not
be launched until density, packing fraction, energy bookkeeping and acceptance
are checked. `vmax` is an algorithmic pilot parameter and defaults to 0.001.

The validated parent is the previous 500k endpoint. It has density 1.03708,
packing fraction 0.54301, no overlaps, no PTM crystal classifications, and
only one isolated CNA-BCC classification. Its maximum tested low-index
structure factor is 2.03, consistent with a liquid rather than a Bragg solid.

`run_metrics.dat` records the imposed pressure and labels the force-virial
quantity as `p_continuous`; it is not the total hard-core pressure.

`launch_nohup.sh` makes a run survive terminal closure or logout. It cannot
continue computing while the computer is suspended; Linux pauses all CPU work
during system sleep and continues it after wake-up.
