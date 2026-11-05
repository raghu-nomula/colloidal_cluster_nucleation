# Analysis scripts

| Script | What it does | Needs |
|---|---|---|
| `analyze_example_frames.py` | CNA counts, largest fcc + hcp cluster, opposite-charge neighbour fraction and q6 solid-like count for the four frames in `../results/example_frames/` | OVITO, numpy, scipy |
| `q6_check/q6_fast.py` | vectorised version of the author's q6 cluster script (two settings: `ref18` = ten Wolde et al. 1996, `yours` = rcut 1.45, dot > 0.70, ≥ 7 bonds) | numpy, scipy |
| `q6_check/validate_q6.py` | shows that `q6_fast.py` reproduces the original `cluster_size.dat` of the June run | June trajectory (not in repo) |
| `q6_check/run_all.py` | q6 on every frame of both campaigns and the June run; writes the `q6_*.csv` files in the same folder | all trajectories (not in repo) |
| `q6_check/halfbox.py` | extent and wrapping of the crystalline cluster in the periodic box on six frames, charge order | trajectories, OVITO |
| `q6_check/cutoff_scan.py` | connectivity of the crystalline particles versus connection distance | trajectories, OVITO |
| `q6_check/cna_charge_and_plot.py`, `gr_plot.py` | CNA-based charge order and the plots used on the slides | trajectories, OVITO, matplotlib |
| `q6_check/make_slides.py` | rebuilds `docs/reports/07_meeting_slides.pptx` | python-pptx, matplotlib figures in `docs/reports/figs/` |

Result tables already computed: `q6_check/q6_dr_0.04.csv`, `q6_dr_0.01.csv`, `q6_june_dr0.01.csv`.
The structure-analysis tools used for the main campaign (`ovito_structure.py`, `analyze_campaign.py`,
`validate_structure.py`) are in `../simulations/4_Clean_NoSwap_Replication/analysis/`, next to their results.

Scripts marked "trajectories (not in repo)" expect the trajectory files at their original relative paths under
`simulations/`; see [../docs/DATA.md](../docs/DATA.md).
