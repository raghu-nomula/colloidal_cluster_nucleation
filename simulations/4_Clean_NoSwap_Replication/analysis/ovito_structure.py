#!/usr/bin/env python3
"""Independent OVITO PTM and CNA classification for one configuration."""

import argparse
import json
from pathlib import Path

import numpy as np
from ovito.io import export_file, import_file
from ovito.modifiers import CommonNeighborAnalysisModifier
from ovito.modifiers import PolyhedralTemplateMatchingModifier


NAMES = {0: "OTHER", 1: "FCC", 2: "HCP", 3: "BCC", 4: "ICO", 5: "SC"}


def counts(values):
    return {NAMES.get(int(key), str(int(key))): int(np.sum(values == key)) for key in np.unique(values)}


def largest_close_packed_cluster(positions, structure, box, cutoff):
    selected = np.where((structure == 1) | (structure == 2))[0]
    if len(selected) == 0:
        return 0
    parent = np.arange(len(selected))
    size = np.ones(len(selected), dtype=int)

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        root_left, root_right = find(left), find(right)
        if root_left == root_right:
            return
        if size[root_left] < size[root_right]:
            root_left, root_right = root_right, root_left
        parent[root_right] = root_left
        size[root_left] += size[root_right]

    selected_positions = positions[selected]
    cutoff2 = cutoff * cutoff
    for i in range(len(selected) - 1):
        delta = selected_positions[i + 1 :] - selected_positions[i]
        delta -= box * np.rint(delta / box)
        near = np.where(np.einsum("ij,ij->i", delta, delta) < cutoff2)[0]
        for offset in near:
            union(i, i + 1 + int(offset))
    cluster_sizes = {}
    for i in range(len(selected)):
        root = find(i)
        cluster_sizes[root] = cluster_sizes.get(root, 0) + 1
    return max(cluster_sizes.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trajectory")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--rmsd-cutoff", type=float, default=0.10)
    parser.add_argument("--cluster-cutoff", type=float, default=1.45)
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    ptm_pipeline = import_file(args.trajectory)
    ptm = PolyhedralTemplateMatchingModifier(
        rmsd_cutoff=args.rmsd_cutoff,
        output_rmsd=True,
    )
    ptm_pipeline.modifiers.append(ptm)
    ptm_data = ptm_pipeline.compute()
    ptm_types = np.asarray(ptm_data.particles["Structure Type"]).copy()
    positions = np.asarray(ptm_data.particles.positions).copy()
    box = np.diag(np.asarray(ptm_data.cell.matrix)[:, :3]).copy()
    ptm_counts = counts(ptm_types)
    ptm_largest = largest_close_packed_cluster(
        positions, ptm_types, box, args.cluster_cutoff
    )
    export_file(
        ptm_pipeline,
        output / "ptm_marked.lammpstrj",
        "lammps/dump",
        columns=[
            "Particle Identifier",
            "Particle Type",
            "Position.X",
            "Position.Y",
            "Position.Z",
            "Structure Type",
            "RMSD",
        ],
    )

    cna_pipeline = import_file(args.trajectory)
    cna = CommonNeighborAnalysisModifier(
        mode=CommonNeighborAnalysisModifier.Mode.AdaptiveCutoff
    )
    cna_pipeline.modifiers.append(cna)
    cna_data = cna_pipeline.compute()
    cna_types = np.asarray(cna_data.particles["Structure Type"]).copy()
    cna_counts = counts(cna_types)
    cna_largest = largest_close_packed_cluster(
        np.asarray(cna_data.particles.positions),
        cna_types,
        box,
        args.cluster_cutoff,
    )

    summary = {
        "source": str(Path(args.trajectory).resolve()),
        "ptm_rmsd_cutoff": args.rmsd_cutoff,
        "cluster_cutoff": args.cluster_cutoff,
        "ptm_counts": ptm_counts,
        "ptm_largest_fcc_hcp_cluster": ptm_largest,
        "adaptive_cna_counts": cna_counts,
        "adaptive_cna_largest_fcc_hcp_cluster": cna_largest,
    }
    with open(output / "ovito_summary.json", "w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
