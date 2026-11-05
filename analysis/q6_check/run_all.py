"""Run q6 (ref18 + yours settings) on every saved frame of the campaigns and the June run."""
import sys, time, csv
from multiprocessing import Pool
import numpy as np
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from anywhere
sys.path.insert(0, '.')
from q6_fast import read_lammpstrj, analyze, SETTINGS
R = "../../simulations/4_Clean_NoSwap_Replication/"
J = "../../simulations/2_1000_atoms/2_Actual_KMC_for_nucleation/4_step_1.5M_to_3.5M/traj.lammpstrj"

def do(job):
    label, path, offset, skip_first = job
    rows = []
    for k, (ts, ty, pos, box) in enumerate(read_lammpstrj(path)):
        if skip_first and k == 0:
            continue
        row = [label, offset + ts]
        for name in ("ref18", "yours"):
            ns, lg, nb, _, _ = analyze(pos, box, **SETTINGS[name])
            row += [ns, lg]
        row.append(round(nb, 3))
        rows.append(row)
    return rows

jobs = []
for b in ("dr_0.04", "dr_0.01"):
    for s in range(1, 13):
        jobs.append((b, f"{R}{b}/production_3M_seg{s:03d}/traj.lammpstrj", (s - 1) * 250000, s > 1))
jobs.append(("june_dr0.01", J, 0, False))
t0 = time.time()
with Pool(18) as p:
    res = p.map(do, jobs)
out = {}
for job, rows in zip(jobs, res):
    out.setdefault(job[0], []).extend(rows)
for label, rows in out.items():
    with open(f"q6_{label}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["set", "cycle", "ref18_nsolid", "ref18_largest", "yours_nsolid", "yours_largest", "avg_neigh"])
        w.writerows(rows)
    a = np.array([r[1:] for r in rows], float)
    print(label, len(rows), "frames | max largest ref18 = %d, yours = %d" % (a[:, 2].max(), a[:, 4].max()))
print("time %.1fs" % (time.time() - t0))
