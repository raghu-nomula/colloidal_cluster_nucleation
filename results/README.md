# Results: where to find them

Result tables and figures stay next to the scripts that made them, so nothing is duplicated here. This page is the index.

| Result | File |
|---|---|
| Structure counts (PTM and CNA) and largest fcc/hcp cluster, one row per 1000 cycles, dr = 0.04 | `../simulations/4_Clean_NoSwap_Replication/analysis/production_3M/dr_0.04_structure_timeseries.csv` |
| The same for dr = 0.01 | `../simulations/4_Clean_NoSwap_Replication/analysis/production_3M/dr_0.01_structure_timeseries.csv` |
| Cluster growth plot, CNA only (used on slide 3) | `../docs/reports/figs/cna_largest_cluster.png` |
| Cluster growth plots, PTM and CNA | `../simulations/4_Clean_NoSwap_Replication/analysis/production_3M/*.png` |
| Per-frame q6 cluster sizes with the paper's and the author's settings | `../analysis/q6_check/q6_dr_0.04.csv`, `q6_dr_0.01.csv`, `q6_june_dr0.01.csv` |
| q6 against PTM comparison plot | `../docs/reports/figs/q6_vs_ptm.png` |
| OVITO pictures (liquid, 2.1M, 3.0M cycles) and g(r) | `../docs/reports/figs/ovito_*.png`, `gr_three_frames.png` |
| Acceptance rates, density, energy per run | `run_metrics.dat` in each run folder; cumulative: `production_3M_control/cumulative_metrics.dat` |
| vmax search tables and plots | `../simulations/5_Vmax_Search/plots/`, `…/notes/` |

**Example frames** (`example_frames/`): single frames of the dr = 0.04 run, so that the structure analysis can be
run without the big trajectories:

| File | Segment, frame | Cumulative cycles |
|---|---|---|
| `dr0.04_0.00M_liquid_start_seg001_frame000` | seg001, 0 | 0 |
| `dr0.04_2.10M_growing_seg009_frame100` | seg009, 100 | 2 100 000 |
| `dr0.04_2.25M_grown_seg009_frame250` | seg009, 250 | 2 250 000 |
| `dr0.04_3.00M_final_seg012_frame250` | seg012, 250 | 3 000 000 |
