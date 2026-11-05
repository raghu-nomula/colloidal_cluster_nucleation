#!/usr/bin/env python3
"""Fast q6 cluster analysis (vectorised copy of analyze_q6_cluster.py).

Two joining rules:
  join="bonds"      : original script - two solid-like particles are joined only if
                      their q6 dot product also exceeds the connection threshold
  join="neighbors"  : ref. [18] (ten Wolde et al. 1996) - any two neighbouring
                      solid-like particles belong to the same cluster

The original script and all run directories are left untouched.
"""
import numpy as np
from scipy.spatial import cKDTree
from scipy.special import sph_harm_y
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

L = 6
MS = np.arange(-L, L + 1)


def read_lammpstrj(path):
    """yield (timestep, types, pos, box) for each frame, ordered by id"""
    with open(path) as f:
        while True:
            line = f.readline()
            if not line:
                return
            if not line.startswith("ITEM: TIMESTEP"):
                continue
            ts = int(f.readline())
            f.readline()
            n = int(f.readline())
            f.readline()
            lo_hi = [list(map(float, f.readline().split()[:2])) for _ in range(3)]
            box = np.array([h - l for l, h in lo_hi])
            hdr = f.readline().split()[2:]
            arr = np.array([f.readline().split() for _ in range(n)], dtype=float)
            ic, tc = hdr.index("id"), hdr.index("type")
            xc = [hdr.index(c) for c in ("x", "y", "z")]
            order = np.argsort(arr[:, ic])
            arr = arr[order]
            yield ts, arr[:, tc].astype(int), arr[:, xc], box


def bonds(pos, box, rcut):
    pos = pos % box
    tree = cKDTree(pos, boxsize=box)
    pairs = tree.query_pairs(rcut, output_type="ndarray")
    i, j = pairs[:, 0], pairs[:, 1]
    d = pos[j] - pos[i]
    d -= box * np.rint(d / box)
    return i, j, d


def qvectors(n, i, j, d):
    """normalised q6 vectors (n x 13) from bond list"""
    ii = np.concatenate([i, j])
    dd = np.concatenate([d, -d])
    r = np.linalg.norm(dd, axis=1)
    polar = np.arccos(np.clip(dd[:, 2] / r, -1, 1))
    azim = np.mod(np.arctan2(dd[:, 1], dd[:, 0]), 2 * np.pi)
    nb = np.bincount(ii, minlength=n).astype(float)
    q = np.zeros((n, 2 * L + 1), dtype=complex)
    for k, m in enumerate(MS):
        y = sph_harm_y(L, m, polar, azim)
        q[:, k] = np.bincount(ii, weights=y.real, minlength=n) + 1j * np.bincount(ii, weights=y.imag, minlength=n)
    q[nb > 0] /= nb[nb > 0, None]
    norm = np.linalg.norm(q, axis=1)
    ok = norm > 1e-14
    q[ok] /= norm[ok, None]
    return q, nb


def analyze(pos, box, rcut, dot_thr, min_bonds, join):
    n = len(pos)
    i, j, d = bonds(pos, box, rcut)
    q, nb = qvectors(n, i, j, d)
    dots = np.real(np.einsum("ab,ab->a", np.conj(q[i]), q[j]))
    conn = dots > dot_thr
    cnt = np.bincount(i[conn], minlength=n) + np.bincount(j[conn], minlength=n)
    solid = cnt >= min_bonds
    if join == "bonds":
        use = conn & solid[i] & solid[j]
    else:
        use = solid[i] & solid[j]
    g = coo_matrix((np.ones(use.sum()), (i[use], j[use])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    sizes = np.bincount(lab[solid]) if solid.any() else np.array([0])
    return int(solid.sum()), int(sizes.max()), float(nb.mean()), solid, lab


SETTINGS = {
    "ref18": dict(rcut=1.5, dot_thr=0.5, min_bonds=7, join="neighbors"),
    "yours": dict(rcut=1.45, dot_thr=0.70, min_bonds=7, join="bonds"),
}
