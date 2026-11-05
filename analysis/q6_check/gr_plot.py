import sys, itertools, numpy as np
import os; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from q6_fast import read_lammpstrj
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.join(HERE, "../../simulations/4_Clean_NoSwap_Replication/dr_0.04/")
FIG = os.path.join(HERE, "../../docs/reports/figs/")

def gr(pos, box, rmax=4.8, dr=0.02):
    n = len(pos); p = pos % box
    tree = cKDTree(p, boxsize=box)
    d = tree.sparse_distance_matrix(tree, rmax, output_type="ndarray")
    d = d[d["i"] < d["j"]]["v"]
    h, edges = np.histogram(d, bins=np.arange(0, rmax + dr, dr))
    r = 0.5 * (edges[1:] + edges[:-1])
    rho = n / np.prod(box)
    g = 2 * h / (n * rho * 4 * np.pi * r**2 * dr)
    return r, g

fig, ax = plt.subplots(figsize=(6.4, 1.5), dpi=220)
for (seg, loc, lab, col, lw) in [(1, 0, "liquid start", "#888888", 1.3), (9, 100, "2.1M cycles", "#D55E00", 1.3),
                                  (12, 250, "3.0M cycles", "#1F4E79", 1.5)]:
    ts, ty, pos, box = next(itertools.islice(read_lammpstrj(f"{R}production_3M_seg{seg:03d}/traj.lammpstrj"), loc, loc + 1))
    r, g = gr(pos, box)
    ax.plot(r, g, color=col, lw=lw, label=lab)
ax.set_xlim(0.9, 4.8); ax.set_ylim(0, 7.5)
ax.set_xlabel("r / σ", fontsize=10); ax.set_ylabel("g(r)", fontsize=10, rotation=0, labelpad=6, va="center")
ax.tick_params(labelsize=9)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.legend(frameon=False, fontsize=9, loc="upper right", ncol=1)
fig.tight_layout(pad=0.4); fig.subplots_adjust(left=0.1)
fig.savefig(FIG + "gr_three_frames.png")
print("ok")
