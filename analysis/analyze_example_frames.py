#!/usr/bin/env python3
"""Run the structure analysis on the four example frames shipped in results/example_frames/.

No large trajectory files are needed. For every frame it prints
  * CNA (adaptive) counts: fcc / hcp / bcc / other,
  * the largest connected fcc+hcp cluster (periodic, connection distance 1.45 sigma),
  * the fraction of opposite-charge nearest-neighbour pairs (< 1.3 sigma) among fcc+hcp
    particles (for the liquid frame: among all particles),
  * the q6 solid-like count with Raghu's settings (rcut 1.45, dot > 0.70, >= 7 bonds).

Needs OVITO (python module "ovito"), numpy, scipy.   Usage:  python analyze_example_frames.py
"""
import glob, os, sys
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from ovito.io import import_file
from ovito.modifiers import CommonNeighborAnalysisModifier

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "q6_check"))
from q6_fast import read_lammpstrj, analyze, SETTINGS  # noqa: E402

FRAMES = sorted(glob.glob(os.path.join(HERE, "..", "results", "example_frames", "*.lammpstrj")))


def largest_cluster(pos, box, sel, cutoff=1.45):
    p = pos[sel] % box
    pairs = cKDTree(p, boxsize=box).query_pairs(cutoff, output_type="ndarray")
    n = len(sel)
    g = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    return int(np.bincount(lab).max()) if n else 0


def opposite_fraction(pos, types, box, sel, rc=1.3):
    pairs = cKDTree(pos[sel] % box, boxsize=box).query_pairs(rc, output_type="ndarray")
    t = types[sel]
    return float((t[pairs[:, 0]] != t[pairs[:, 1]]).mean())


print(f"{'frame':52s} fcc hcp bcc other | largest | opp.charge | q6 solid-like")
for path in FRAMES:
    _, types, pos, box = next(read_lammpstrj(path))
    pipe = import_file(path)
    pipe.modifiers.append(CommonNeighborAnalysisModifier(mode=CommonNeighborAnalysisModifier.Mode.AdaptiveCutoff))
    st = np.asarray(pipe.compute().particles["Structure Type"])
    fcc, hcp, bcc = (int((st == k).sum()) for k in (1, 2, 3))
    other = len(st) - fcc - hcp - bcc - int((st == 4).sum())
    cr = np.where(np.isin(st, [1, 2]))[0]
    allp = np.arange(len(st))
    sel = cr if len(cr) > 50 else allp          # liquid frame: use all particles for the charge reference
    n_solid = analyze(pos, box, **SETTINGS["yours"])[0]
    print(f"{os.path.basename(path):52s} {fcc:3d} {hcp:3d} {bcc:3d} {other:5d} | {largest_cluster(pos, box, cr):7d} |"
          f"   {opposite_fraction(pos, types, box, sel):.3f}   | {n_solid}")
