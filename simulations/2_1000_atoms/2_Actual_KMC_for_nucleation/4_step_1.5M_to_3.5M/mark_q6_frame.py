#!/usr/bin/env python3

import argparse
import numpy as np

from analyze_q6_cluster import (
    read_lammpstrj,
    build_neighbors,
    compute_q_l,
    UnionFind,
)


def mark_frame(pos, box, rcut, l, dot_threshold, min_solid_bonds):
    neighbor_vecs, pairs, pair_vecs = build_neighbors(pos, box, rcut)
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

    uf = UnionFind(n)

    for i, j in solid_edges:
        if solid_like[i] and solid_like[j]:
            uf.union(i, j)

    cluster_sizes = {}

    for i in np.where(solid_like)[0]:
        root = uf.find(i)
        cluster_sizes[root] = cluster_sizes.get(root, 0) + 1

    largest_root = None
    largest_size = 0

    if cluster_sizes:
        largest_root = max(cluster_sizes, key=cluster_sizes.get)
        largest_size = cluster_sizes[largest_root]

    cluster_id = np.zeros(n, dtype=int)
    largest_cluster = np.zeros(n, dtype=int)

    root_to_id = {}
    next_id = 1

    for i in np.where(solid_like)[0]:
        root = uf.find(i)

        if root not in root_to_id:
            root_to_id[root] = next_id
            next_id += 1

        cluster_id[i] = root_to_id[root]

        if root == largest_root:
            largest_cluster[i] = 1

    return solid_like.astype(int), largest_cluster, cluster_id, solid_bond_count, largest_size


def write_marked_lammpstrj(output, timestep, ids, types, pos, box,
                           solid_like, largest_cluster, cluster_id, solid_bonds):
    with open(output, "w") as f:
        f.write("ITEM: TIMESTEP\n")
        f.write(f"{timestep}\n")
        f.write("ITEM: NUMBER OF ATOMS\n")
        f.write(f"{len(ids)}\n")
        f.write("ITEM: BOX BOUNDS pp pp pp\n")
        f.write(f"0.0 {box[0]:.16f}\n")
        f.write(f"0.0 {box[1]:.16f}\n")
        f.write(f"0.0 {box[2]:.16f}\n")
        f.write("ITEM: ATOMS id type x y z solid_like largest_cluster cluster_id solid_bonds\n")

        for i in range(len(ids)):
            f.write(
                f"{ids[i]} {types[i]} "
                f"{pos[i,0]:.12f} {pos[i,1]:.12f} {pos[i,2]:.12f} "
                f"{solid_like[i]} {largest_cluster[i]} {cluster_id[i]} {solid_bonds[i]}\n"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trajectory")
    parser.add_argument("--timestep", type=int, required=True)
    parser.add_argument("--output", default="marked_frame.lammpstrj")
    parser.add_argument("--rcut", type=float, default=1.45)
    parser.add_argument("--l", type=int, default=6)
    parser.add_argument("--dot", type=float, default=0.70)
    parser.add_argument("--min-solid-bonds", type=int, default=7)

    args = parser.parse_args()

    found = False

    for timestep, ids, types, pos, box in read_lammpstrj(args.trajectory, stride=1):
        if timestep != args.timestep:
            continue

        found = True

        solid_like, largest_cluster, cluster_id, solid_bonds, largest_size = mark_frame(
            pos=pos,
            box=box,
            rcut=args.rcut,
            l=args.l,
            dot_threshold=args.dot,
            min_solid_bonds=args.min_solid_bonds,
        )

        write_marked_lammpstrj(
            output=args.output,
            timestep=timestep,
            ids=ids,
            types=types,
            pos=pos,
            box=box,
            solid_like=solid_like,
            largest_cluster=largest_cluster,
            cluster_id=cluster_id,
            solid_bonds=solid_bonds,
        )

        print(f"Marked timestep: {timestep}")
        print(f"Total solid-like particles: {solid_like.sum()}")
        print(f"Largest cluster size: {largest_size}")
        print(f"Output written to: {args.output}")
        break

    if not found:
        raise SystemExit(f"ERROR: timestep {args.timestep} not found in trajectory")


if __name__ == "__main__":
    main()
