#!/usr/bin/env python3
"""PTM/CNA time series for every saved frame of a completed campaign."""

import argparse
import csv
from pathlib import Path

import numpy as np
from ovito.io import import_file
from ovito.modifiers import CommonNeighborAnalysisModifier
from ovito.modifiers import PolyhedralTemplateMatchingModifier

from ovito_structure import largest_close_packed_cluster


def structure_counts(values):
    return [int(np.sum(values == code)) for code in range(6)]


def analyze_trajectory(path, offset, writer, cluster_cutoff, rmsd_cutoff,
                       skip_initial_frame=False):
    ptm_pipeline = import_file(str(path), multiple_frames=True)
    ptm_pipeline.modifiers.append(
        PolyhedralTemplateMatchingModifier(rmsd_cutoff=rmsd_cutoff)
    )
    cna_pipeline = import_file(str(path), multiple_frames=True)
    cna_pipeline.modifiers.append(
        CommonNeighborAnalysisModifier(
            mode=CommonNeighborAnalysisModifier.Mode.AdaptiveCutoff
        )
    )

    for frame in range(ptm_pipeline.source.num_frames):
        ptm_data = ptm_pipeline.compute(frame)
        cna_data = cna_pipeline.compute(frame)
        local_cycle = int(ptm_data.attributes.get("Timestep", frame))
        if skip_initial_frame and local_cycle == 0:
            continue
        positions = np.asarray(ptm_data.particles.positions)
        box = np.diag(np.asarray(ptm_data.cell.matrix)[:, :3])
        ptm_types = np.asarray(ptm_data.particles["Structure Type"])
        cna_types = np.asarray(cna_data.particles["Structure Type"])
        ptm_counts = structure_counts(ptm_types)
        cna_counts = structure_counts(cna_types)
        writer.writerow(
            [
                offset + local_cycle,
                path.parent.name,
                local_cycle,
                *ptm_counts,
                largest_close_packed_cluster(
                    positions, ptm_types, box, cluster_cutoff
                ),
                *cna_counts,
                largest_close_packed_cluster(
                    positions, cna_types, box, cluster_cutoff
                ),
            ]
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("branch_dir")
    parser.add_argument("campaign")
    parser.add_argument("--output", required=True)
    parser.add_argument("--segment-cycles", type=int, default=250000)
    parser.add_argument("--cluster-cutoff", type=float, default=1.45)
    parser.add_argument("--rmsd-cutoff", type=float, default=0.10)
    args = parser.parse_args()

    branch = Path(args.branch_dir)
    segments = sorted(branch.glob(f"{args.campaign}_seg[0-9][0-9][0-9]"))
    if not segments:
        raise SystemExit("No campaign segments found")

    header = [
        "cumulative_cycle", "segment", "local_cycle",
        "ptm_other", "ptm_fcc", "ptm_hcp", "ptm_bcc", "ptm_ico", "ptm_sc",
        "ptm_largest_fcc_hcp_cluster",
        "cna_other", "cna_fcc", "cna_hcp", "cna_bcc", "cna_ico", "cna_sc",
        "cna_largest_fcc_hcp_cluster",
    ]
    with open(args.output, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for index, segment in enumerate(segments):
            trajectory = segment / "traj.lammpstrj"
            if not trajectory.exists():
                raise SystemExit(f"Missing trajectory: {trajectory}")
            analyze_trajectory(
                trajectory,
                index * args.segment_cycles,
                writer,
                args.cluster_cutoff,
                args.rmsd_cutoff,
                skip_initial_frame=(index > 0),
            )


if __name__ == "__main__":
    main()
