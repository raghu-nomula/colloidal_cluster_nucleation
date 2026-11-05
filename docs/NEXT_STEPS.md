# Open questions and proposed next steps

Status as of 2026-11. "Needs new simulations" is marked, because everything done so far after the production
campaigns was analysis of existing files.

## Done (analysis only)

* Paper manual, comparison of the paper's cluster-size method with the author's, meeting report and slides
  ([reports/](reports/)).
* q6 re-analysis of every frame with the paper's and the author's thresholds; half-the-box check; charge order;
  CNA connectivity (all fcc/hcp particles form one periodic-boundary-connected body at 2.25M and 3.0M cycles).

## Open, analysis only (existing frames)

1. **Compare g(r) with the paper's Fig. 2** (g(r) of an 80-particle cluster at p\* = 15). Use frames near
   2.1M cycles, before the crystal wraps the box. Peak positions shift with density, so compare peak ratios.
   fcc and hcp have nearly identical g(r), so this shows "close-packed", not fcc versus hcp.
2. **PTM (486) against q6 (≈ 790) crystalline counts**: which is closer to the truth? Look at frames of
   `dr_0.04/production_3M_seg008` and `seg009` in OVITO (Replicate 2 × 2 × 2, hide "other").
3. **The q6 "precursor" between 1.5M and 2.0M cycles** (q6 cluster grows steadily before CNA/PTM see a crystal):
   real pre-structure or over-counted ordered liquid?
4. **Re-tune the q6 thresholds** (dot product 0.5–0.8) so that the liquid gives fewer than 5 solid-like
   particles per 1000, as the paper states.
5. **Full same-charge and opposite-charge g(r) of the crystal** (the neighbour-fraction measure used so far is a
   single number).
6. Settle who proposed `dr = 0.04` (see [HISTORY.md](HISTORY.md)).

## Needs new simulations

1. **More seeds** for dr = 0.04 (and dr = 0.01): the time-to-nucleation distribution; one trajectory per
   setting is all that exists.
2. **Larger system** (N = 2000 or more) to see an isolated nucleus instead of a box-wrapping crystal.
3. **A swap move** (exchange of a positive and a negative particle) and a rerun at p\* = 18: the paper reports CsCl.
   This is the step that would test the paper's central claim (the source code has no swap move).
4. **vmax = 0.0004** instead of 0.0005, as the vmax search recommends (never used in production).
5. **FFS at p\* = 15** (the paper's rate and critical-nucleus results), the natural link to the infRETIS project.
