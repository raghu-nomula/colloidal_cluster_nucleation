"""Half-the-box check on selected dr=0.04 frames: extent / wrapping of the crystalline cluster and charge order."""
import sys, itertools
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from collections import deque
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from anywhere
sys.path.insert(0, '.')
from q6_fast import read_lammpstrj, analyze, SETTINGS
from ovito.io import import_file
from ovito.modifiers import PolyhedralTemplateMatchingModifier

R = "../../simulations/4_Clean_NoSwap_Replication/dr_0.04/"
FR = [(8, 250, "end of seg008 (2.00M)"), (9, 50, "2.05M"), (9, 100, "2.10M"), (9, 150, "2.15M"), (9, 250, "2.25M"), (12, 250, "3.00M (final)")]
CUT = 1.45

def largest_component(pos, box, mask):
    idx = np.where(mask)[0]
    p = pos[idx] % box
    tree = cKDTree(p, boxsize=box)
    pr = tree.query_pairs(CUT, output_type="ndarray")
    n = len(idx)
    g = coo_matrix((np.ones(len(pr)), (pr[:, 0], pr[:, 1])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    big = np.argmax(np.bincount(lab))
    members = np.where(lab == big)[0]
    # BFS with unwrapped coordinates to measure extent and detect wrapping
    inset = set(members.tolist())
    adj = {m: [] for m in members}
    for a, b in pr:
        if a in inset and b in inset:
            d = p[b] - p[a]; d -= box * np.rint(d / box)
            adj[a].append((b, d)); adj[b].append((a, -d))
    u = {members[0]: np.zeros(3)}
    dq = deque([members[0]]); wrap = np.zeros(3, bool)
    while dq:
        a = dq.popleft()
        for b, d in adj[a]:
            if b not in u:
                u[b] = u[a] + d; dq.append(b)
            else:
                off = u[a] + d - u[b]
                wrap |= np.abs(np.rint(off / box)) > 0
    U = np.array(list(u.values()))
    return idx[members], np.ptp(U, axis=0), wrap

def opp_fraction(pos, types, box, sel, cut=1.3):
    p = pos % box
    tree = cKDTree(p, boxsize=box)
    pairs = tree.query_pairs(cut, output_type="ndarray")
    inset = np.zeros(len(pos), bool); inset[sel] = True
    m = inset[pairs[:, 0]] & inset[pairs[:, 1]]
    pr = pairs[m]
    return float(np.mean(types[pr[:, 0]] != types[pr[:, 1]])), len(pr)

print("%-22s %5s | %-26s | %-30s | %s" % ("frame", "ptm", "PTM fcc/hcp(+bcc) cluster", "q6 'yours' cluster", "opposite-charge fraction (nn<1.3)"))
for seg, loc, label in FR:
    path = f"{R}production_3M_seg{seg:03d}/traj.lammpstrj"
    ts, types, pos, box = next(itertools.islice(read_lammpstrj(path), loc, loc + 1))
    L = box[0]
    pl = import_file(path, multiple_frames=True)
    pl.modifiers.append(PolyhedralTemplateMatchingModifier(rmsd_cutoff=0.10))
    st = np.asarray(pl.compute(loc).particles["Structure Type"])
    crys = np.isin(st, [1, 2, 3])          # fcc, hcp, bcc (structure-blind, like the paper's n)
    nfcc, nhcp, nbcc = [(st == k).sum() for k in (1, 2, 3)]
    m1, ext1, w1 = largest_component(pos, box, crys)
    _, _, _, solid, _ = analyze(pos, box, **SETTINGS["yours"])
    m2, ext2, w2 = largest_component(pos, box, solid)
    fc = np.isin(st, [1, 2])
    of, npairs = opp_fraction(pos, types, box, np.where(fc)[0])
    s1 = "n=%3d ext=%s wrap=%s" % (len(m1), "/".join("%.1f" % e for e in ext1), "".join("xyz"[k] for k in range(3) if w1[k]) or "no")
    s2 = "n=%3d ext=%s wrap=%s" % (len(m2), "/".join("%.1f" % e for e in ext2), "".join("xyz"[k] for k in range(3) if w2[k]) or "no")
    print("%-22s %5s | %-26s | %-30s | %.2f (%d pairs)  [fcc %d hcp %d bcc %d]" % (label, "L=%.2f" % L, s1, s2, of, npairs, nfcc, nhcp, nbcc))
