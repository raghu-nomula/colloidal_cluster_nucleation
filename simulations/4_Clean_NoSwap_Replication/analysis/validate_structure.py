#!/usr/bin/env python3
"""Independent geometric validation for restart configurations.

This intentionally does not use q6. It checks composition, hard-core
overlaps, neighbor statistics, charge mixing, radial distribution functions,
and low-index reciprocal-space density peaks.
"""

import argparse
import json
from pathlib import Path

import numpy as np


def read_restart(path):
    with open(path) as handle:
        box, hbox = map(float, handle.readline().split()[:2])
        n_particles = int(handle.readline())
        dr, vmax = map(float, handle.readline().split()[:2])
        rows = [handle.readline().split() for _ in range(n_particles)]

    data = np.asarray(rows, dtype=float)
    if data.shape != (n_particles, 4):
        raise ValueError(f"Expected {n_particles} coordinate/type rows")
    positions = data[:, :3]
    types = data[:, 3].astype(int)
    return box, hbox, dr, vmax, positions, types


def pair_data(positions, types, box):
    distances = []
    same_charge = []
    n_particles = len(positions)
    for i in range(n_particles - 1):
        delta = positions[i + 1 :] - positions[i]
        delta -= box * np.rint(delta / box)
        distances.append(np.linalg.norm(delta, axis=1))
        same_charge.append(types[i + 1 :] == types[i])
    return np.concatenate(distances), np.concatenate(same_charge)


def normalized_rdf(distances, selected, pair_count, box, edges):
    counts, _ = np.histogram(distances[selected], bins=edges)
    shell_volume = 4.0 * np.pi * (edges[1:] ** 3 - edges[:-1] ** 3) / 3.0
    expected = pair_count * shell_volume / box**3
    rdf = np.divide(counts, expected, out=np.zeros_like(expected), where=expected > 0)
    return counts, rdf


def reciprocal_peak(positions, box, nmax=6):
    best_s = -1.0
    best_hkl = None
    n_particles = len(positions)
    factor = 2.0 * np.pi / box
    for h in range(-nmax, nmax + 1):
        for k in range(-nmax, nmax + 1):
            for ell in range(-nmax, nmax + 1):
                if h == 0 and k == 0 and ell == 0:
                    continue
                phase = factor * (h * positions[:, 0] + k * positions[:, 1] + ell * positions[:, 2])
                amplitude = np.exp(1j * phase).sum()
                structure_factor = float((amplitude.real**2 + amplitude.imag**2) / n_particles)
                if structure_factor > best_s:
                    best_s = structure_factor
                    best_hkl = [h, k, ell]
    return best_s, best_hkl


def write_lammps_snapshot(path, positions, types, box):
    with open(path, "w") as handle:
        handle.write("ITEM: TIMESTEP\n0\n")
        handle.write(f"ITEM: NUMBER OF ATOMS\n{len(positions)}\n")
        handle.write("ITEM: BOX BOUNDS pp pp pp\n")
        for _ in range(3):
            handle.write(f"0.0 {box:.12f}\n")
        handle.write("ITEM: ATOMS id type x y z\n")
        for index, (position, particle_type) in enumerate(zip(positions, types), start=1):
            handle.write(
                f"{index} {particle_type} {position[0]:.12f} "
                f"{position[1]:.12f} {position[2]:.12f}\n"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("restart")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--neighbor-cutoff", type=float, default=1.45)
    parser.add_argument("--rdf-bins", type=int, default=250)
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    box, hbox, dr, vmax, positions, types = read_restart(args.restart)
    n_particles = len(positions)
    counts_by_type = {int(t): int(np.sum(types == t)) for t in np.unique(types)}
    distances, same_charge = pair_data(positions, types, box)

    density = n_particles / box**3
    packing_fraction = np.pi * density / 6.0
    minimum_distance = float(distances.min())
    overlap_count = int(np.sum(distances < 1.0))

    neighbors = distances < args.neighbor_cutoff
    neighbor_pairs = int(np.sum(neighbors))
    mean_neighbors = 2.0 * neighbor_pairs / n_particles
    unlike_neighbor_fraction = (
        float(np.mean(~same_charge[neighbors])) if neighbor_pairs else 0.0
    )

    max_r = box / 2.0
    edges = np.linspace(0.0, max_r, args.rdf_bins + 1)
    centers = 0.5 * (edges[1:] + edges[:-1])
    all_mask = np.ones(len(distances), dtype=bool)
    n1 = counts_by_type.get(1, 0)
    n2 = counts_by_type.get(2, 0)
    all_pairs = n_particles * (n_particles - 1) / 2
    same_pairs = n1 * (n1 - 1) / 2 + n2 * (n2 - 1) / 2
    unlike_pairs = n1 * n2

    _, g_all = normalized_rdf(distances, all_mask, all_pairs, box, edges)
    _, g_same = normalized_rdf(distances, same_charge, same_pairs, box, edges)
    _, g_unlike = normalized_rdf(distances, ~same_charge, unlike_pairs, box, edges)
    np.savetxt(
        output / "rdf.dat",
        np.column_stack((centers, g_all, g_same, g_unlike)),
        header="r g_all g_same_charge g_unlike_charge",
    )

    peak_s, peak_hkl = reciprocal_peak(positions, box)
    summary = {
        "source": str(Path(args.restart).resolve()),
        "particles": n_particles,
        "type_counts": counts_by_type,
        "box": box,
        "stored_hbox": hbox,
        "stored_dr": dr,
        "stored_vmax": vmax,
        "density": density,
        "packing_fraction": packing_fraction,
        "minimum_pair_distance": minimum_distance,
        "hard_core_overlaps": overlap_count,
        "neighbor_cutoff": args.neighbor_cutoff,
        "mean_neighbor_count": mean_neighbors,
        "unlike_charge_neighbor_fraction": unlike_neighbor_fraction,
        "max_low_index_structure_factor": peak_s,
        "max_structure_factor_hkl": peak_hkl,
    }
    with open(output / "summary.json", "w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    write_lammps_snapshot(output / "ovito_snapshot.lammpstrj", positions, types, box)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

