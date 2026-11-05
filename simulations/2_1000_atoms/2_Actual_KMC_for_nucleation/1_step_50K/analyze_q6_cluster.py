#!/usr/bin/env python3

import argparse
import numpy as np

try:
    from scipy.special import sph_harm

    def Ylm(m, l, azimuth, polar):
        # old scipy convention:
        # sph_harm(m, l, theta_azimuth, phi_polar)
        return sph_harm(m, l, azimuth, polar)

except ImportError:
    from scipy.special import sph_harm_y

    def Ylm(m, l, azimuth, polar):
        # new scipy convention:
        # sph_harm_y(l, m, theta_polar, phi_azimuth)
        return sph_harm_y(l, m, polar, azimuth)

def minimum_image(vecs, box):
    return vecs - box * np.rint(vecs / box)


def read_lammpstrj(filename, stride=1):
    with open(filename, "r") as f:
        frame_index = 0

        while True:
            line = f.readline()
            if not line:
                break

            if not line.startswith("ITEM: TIMESTEP"):
                continue

            timestep = int(f.readline().strip())

            line = f.readline()
            if not line.startswith("ITEM: NUMBER OF ATOMS"):
                raise ValueError("Expected ITEM: NUMBER OF ATOMS")

            n_atoms = int(f.readline().strip())

            line = f.readline()
            if not line.startswith("ITEM: BOX BOUNDS"):
                raise ValueError("Expected ITEM: BOX BOUNDS")

            bounds = []
            for _ in range(3):
                lo, hi = map(float, f.readline().split()[:2])
                bounds.append((lo, hi))

            box = np.array([hi - lo for lo, hi in bounds], dtype=float)

            line = f.readline()
            if not line.startswith("ITEM: ATOMS"):
                raise ValueError("Expected ITEM: ATOMS")

            cols = line.split()[2:]

            try:
                id_col = cols.index("id")
                type_col = cols.index("type")
                x_col = cols.index("x")
                y_col = cols.index("y")
                z_col = cols.index("z")
            except ValueError as e:
                raise ValueError(f"Missing required column in ATOMS line: {cols}") from e

            data = []
            for _ in range(n_atoms):
                data.append(f.readline().split())

            arr = np.array(data, dtype=float)

            ids = arr[:, id_col].astype(int)
            types = arr[:, type_col].astype(int)
            pos = arr[:, [x_col, y_col, z_col]]

            order = np.argsort(ids)
            ids = ids[order]
            types = types[order]
            pos = pos[order]

            if frame_index % stride == 0:
                yield timestep, ids, types, pos, box

            frame_index += 1


def build_neighbors(pos, box, rcut):
    n = len(pos)
    rcut2 = rcut * rcut

    neighbor_vecs = [[] for _ in range(n)]
    pairs = []
    pair_vecs = []

    for i in range(n - 1):
        d = pos[i + 1:] - pos[i]
        d = minimum_image(d, box)
        r2 = np.einsum("ij,ij->i", d, d)

        mask = r2 < rcut2
        js_local = np.where(mask)[0]

        for jl in js_local:
            j = i + 1 + jl
            vec = d[jl]

            pairs.append((i, j))
            pair_vecs.append(vec)

            neighbor_vecs[i].append(vec)
            neighbor_vecs[j].append(-vec)

    return neighbor_vecs, pairs, pair_vecs


def compute_q_l(neighbor_vecs, l=6):
    n = len(neighbor_vecs)
    m_values = list(range(-l, l + 1))
    q = np.zeros((n, 2 * l + 1), dtype=np.complex128)

    for i, vecs in enumerate(neighbor_vecs):
        if len(vecs) == 0:
            continue

        vecs = np.array(vecs, dtype=float)
        r = np.linalg.norm(vecs, axis=1)

        good = r > 1e-12
        if not np.any(good):
            continue

        vecs = vecs[good]
        r = r[good]

        polar = np.arccos(np.clip(vecs[:, 2] / r, -1.0, 1.0))
        azimuth = np.mod(np.arctan2(vecs[:, 1], vecs[:, 0]), 2.0 * np.pi)

        for idx, m in enumerate(m_values):
            q[i, idx] = np.mean(Ylm(m, l, azimuth, polar))

    norms = np.linalg.norm(q, axis=1)
    qnorm = np.zeros_like(q)

    nonzero = norms > 1e-14
    qnorm[nonzero] = q[nonzero] / norms[nonzero, None]

    return qnorm


class UnionFind:
    def __init__(self, n):
        self.parent = np.arange(n)
        self.size = np.ones(n, dtype=int)

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)

        if ra == rb:
            return

        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra

        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def analyze_frame(pos, box, rcut, l, dot_threshold, min_solid_bonds):
    neighbor_vecs, pairs, pair_vecs = build_neighbors(pos, box, rcut)

    avg_neighbors = np.mean([len(v) for v in neighbor_vecs])

    qnorm = compute_q_l(neighbor_vecs, l=l)

    n = len(pos)
    solid_bond_count = np.zeros(n, dtype=int)
    solid_edges = []

    for i, j in pairs:
        if np.linalg.norm(qnorm[i]) < 1e-14 or np.linalg.norm(qnorm[j]) < 1e-14:
            continue

        dot = np.real(np.vdot(qnorm[i], qnorm[j]))

        if dot > dot_threshold:
            solid_bond_count[i] += 1
            solid_bond_count[j] += 1
            solid_edges.append((i, j))

    solid_like = solid_bond_count >= min_solid_bonds
    n_solid = int(np.sum(solid_like))

    uf = UnionFind(n)

    for i, j in solid_edges:
        if solid_like[i] and solid_like[j]:
            uf.union(i, j)

    cluster_sizes = {}

    for i in np.where(solid_like)[0]:
        root = uf.find(i)
        cluster_sizes[root] = cluster_sizes.get(root, 0) + 1

    largest_cluster = max(cluster_sizes.values()) if cluster_sizes else 0

    return n_solid, largest_cluster, avg_neighbors


def main():
    parser = argparse.ArgumentParser(
        description="Compute q6-based largest solid-like cluster size from LAMMPS trajectory."
    )

    parser.add_argument("trajectory", help="LAMMPS trajectory file, e.g. traj.lammpstrj")
    parser.add_argument("--output", default="cluster_size.dat")
    parser.add_argument("--rcut", type=float, default=1.45, help="Neighbor cutoff")
    parser.add_argument("--l", type=int, default=6, help="Bond-order l value")
    parser.add_argument("--dot", type=float, default=0.70, help="Solid bond dot-product threshold")
    parser.add_argument("--min-solid-bonds", type=int, default=7, help="Minimum solid-like bonds")
    parser.add_argument("--stride", type=int, default=1, help="Analyze every nth frame")

    args = parser.parse_args()

    print("Q6 cluster analysis")
    print(f"trajectory        = {args.trajectory}")
    print(f"output            = {args.output}")
    print(f"rcut              = {args.rcut}")
    print(f"l                 = {args.l}")
    print(f"dot threshold     = {args.dot}")
    print(f"min solid bonds   = {args.min_solid_bonds}")
    print(f"stride            = {args.stride}")

    with open(args.output, "w") as out:
        out.write("# timestep n_solid largest_solid_cluster avg_neighbors\n")

        for frame_no, (timestep, ids, types, pos, box) in enumerate(
            read_lammpstrj(args.trajectory, stride=args.stride)
        ):
            n_solid, largest_cluster, avg_neighbors = analyze_frame(
                pos=pos,
                box=box,
                rcut=args.rcut,
                l=args.l,
                dot_threshold=args.dot,
                min_solid_bonds=args.min_solid_bonds,
            )

            out.write(f"{timestep} {n_solid} {largest_cluster} {avg_neighbors:.6f}\n")
            out.flush()

            print(
                f"frame {frame_no:6d} timestep {timestep:10d} "
                f"n_solid {n_solid:6d} largest {largest_cluster:6d} "
                f"avg_neigh {avg_neighbors:8.3f}"
            )


if __name__ == "__main__":
    main()
