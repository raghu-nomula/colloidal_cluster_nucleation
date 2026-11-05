import sys, itertools, numpy as np, pandas as pd
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from anywhere
sys.path.insert(0, ".")
from scipy.spatial import cKDTree
from q6_fast import read_lammpstrj
from ovito.io import import_file
from ovito.modifiers import CommonNeighborAnalysisModifier
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = "../../simulations/4_Clean_NoSwap_Replication/"

def opp_fraction(pos, ty, box, sel, rc=1.3):
    p = pos[sel] % box
    t = ty[sel]
    pr = cKDTree(p, boxsize=box).query_pairs(rc, output_type="ndarray")
    return float((t[pr[:, 0]] != t[pr[:, 1]]).mean()), len(pr), len(sel)

for seg, loc, lab in [(1, 0, "liquid start"), (9, 100, "2.10M"), (9, 250, "2.25M"), (12, 250, "3.00M")]:
    path = f"{R}dr_0.04/production_3M_seg{seg:03d}/traj.lammpstrj"
    ts, ty, pos, box = next(itertools.islice(read_lammpstrj(path), loc, loc + 1))
    if lab == "liquid start":
        sel = np.arange(len(ty))
    else:
        pl = import_file(path, multiple_frames=True)
        pl.modifiers.append(CommonNeighborAnalysisModifier(mode=CommonNeighborAnalysisModifier.Mode.AdaptiveCutoff))
        st = np.asarray(pl.compute(loc).particles["Structure Type"])
        sel = np.where(np.isin(st, [1, 2]))[0]
    f, npairs, n = opp_fraction(pos, ty, box, sel)
    print(f"{lab:13s} particles {n:4d} pairs {npairs:5d} opposite-charge fraction {f:.3f}")

# plot: CNA largest fcc/hcp cluster, both dr
ACC, ORG = "#1F4E79", "#D55E00"
fig, ax = plt.subplots(figsize=(5.6, 2.9), dpi=220)
for dr, col in (("0.01", ORG), ("0.04", ACC)):
    d = pd.read_csv(f"{R}analysis/production_3M/dr_{dr}_structure_timeseries.csv")
    ax.plot(d.cumulative_cycle / 1e6, d.cna_largest_fcc_hcp_cluster, color=col, lw=1.6, label=f"dr = {dr}")
ax.axhline(1000, color="#999999", lw=0.8, ls="--")
ax.text(0.05, 1000, "all 1000 particles", fontsize=9, color="#666666", va="bottom")
ax.set_xlim(0, 3.0); ax.set_ylim(0, 1100)
ax.set_xlabel("MC cycles (millions)", fontsize=11)
ax.set_ylabel("largest crystalline cluster", fontsize=11)
ax.tick_params(labelsize=10)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.annotate("grows from ~2.0M cycles;\nwraps the box by ~2.25M", xy=(2.25, 448), xytext=(0.55, 640),
            fontsize=9.5, color=ACC, arrowprops=dict(arrowstyle="-", color=ACC, lw=0.8))
ax.legend(frameon=False, fontsize=10, loc="center left", bbox_to_anchor=(0.0, 0.3))
fig.tight_layout()
out = "../../docs/reports/figs/cna_largest_cluster.png"
fig.savefig(out)
print("saved", out)
