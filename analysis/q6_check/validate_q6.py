"""Check q6_fast.py reproduces the original cluster_size.dat (your settings) on the June trajectory."""
import sys, itertools, time
import numpy as np
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from anywhere
sys.path.insert(0, '.')
from q6_fast import read_lammpstrj, analyze, SETTINGS
D = "../../simulations/2_1000_atoms/2_Actual_KMC_for_nucleation/4_step_1.5M_to_3.5M/"
ref = np.loadtxt(D + "cluster_size.dat")
t0 = time.time()
bad = 0; n = 0
for k, (ts, ty, pos, box) in enumerate(itertools.islice(read_lammpstrj(D + "traj.lammpstrj"), 0, 2001)):
    if k % 40 != 0 and not (1940 <= k <= 1990):   # sample frames + the peak region
        continue
    ns, lg, nb, _, _ = analyze(pos, box, **SETTINGS["yours"])
    r = ref[k]
    n += 1
    if int(r[0]) != ts or int(r[1]) != ns or int(r[2]) != lg:
        bad += 1
        print("MISMATCH frame", k, "ts", ts, "orig", r[:3], "fast", (ts, ns, lg))
print("frames compared:", n, "mismatches:", bad, "time %.1fs" % (time.time() - t0))
