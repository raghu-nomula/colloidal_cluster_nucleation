#!/usr/bin/env python3
"""Summarize completed Vmax-search runs without external Python packages."""

import csv
import math
import statistics
import sys
from pathlib import Path


def lag_one_correlation(values):
    if len(values) < 3:
        return math.nan
    mean = statistics.fmean(values)
    denominator = sum((value - mean) ** 2 for value in values)
    if denominator == 0.0:
        return math.nan
    return sum(
        (values[i] - mean) * (values[i - 1] - mean)
        for i in range(1, len(values))
    ) / denominator


def positive_sequence_iact(values):
    """Estimate integrated autocorrelation time; stop at first nonpositive ACF."""
    count = len(values)
    if count < 4:
        return math.nan
    mean = statistics.fmean(values)
    variance_sum = sum((value - mean) ** 2 for value in values)
    if variance_sum == 0.0:
        return math.nan
    total = 1.0
    for lag in range(1, count // 2):
        correlation = sum(
            (values[i] - mean) * (values[i - lag] - mean)
            for i in range(lag, count)
        ) / variance_sum
        if correlation <= 0.0:
            break
        total += 2.0 * correlation
    return max(1.0, total)


if len(sys.argv) != 2:
    raise SystemExit("Usage: analyze.py RUN_STAGE_DIRECTORY")

stage_dir = Path(sys.argv[1]).resolve()
rows = []
for manifest in sorted(stage_dir.glob("*/manifest.txt")):
    values = {}
    for line in manifest.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    if "completed_utc" not in values:
        continue
    metrics_path = manifest.parent / "run_metrics.dat"
    metrics = []
    for line in metrics_path.read_text().splitlines():
        if not line.startswith("#") and line.strip():
            fields = line.split()
            metrics.append([float(value) for value in fields])
    last = metrics[-1]
    latter = metrics[len(metrics) // 2:]
    densities = [record[2] for record in latter]
    iact = positive_sequence_iact(densities)
    vmax = float(values["vmax"])
    volume_acceptance = last[11]
    rows.append({
        "run": manifest.parent.name,
        "vmax": vmax,
        "seed": int(values["seed"]),
        "cycles": int(values["cycles"]),
        "particle_acceptance": last[8],
        "volume_acceptance": volume_acceptance,
        "mean_density_second_half": statistics.fmean(densities),
        "sd_density_second_half": statistics.stdev(densities) if len(densities) > 1 else math.nan,
        "density_lag1_correlation": lag_one_correlation(densities),
        "density_iact_samples": iact,
        "density_effective_samples": len(densities) / iact if math.isfinite(iact) else math.nan,
        "final_eta": last[3],
        "screening_proxy_acceptance_vmax2": volume_acceptance * vmax * vmax,
    })

if not rows:
    raise SystemExit(f"No completed runs found under {stage_dir}")

rows.sort(key=lambda row: row["vmax"])
output = stage_dir / "vmax_summary.csv"
with output.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("vmax       vol_acc   part_acc  mean_rho(2nd half)  rho_sd      lag1     IACT    ESS     acc*vmax^2")
for row in rows:
    print(
        f"{row['vmax']:<10.6g} {row['volume_acceptance']:<9.4f} "
        f"{row['particle_acceptance']:<9.4f} "
        f"{row['mean_density_second_half']:<19.8f} "
        f"{row['sd_density_second_half']:<11.4g} "
        f"{row['density_lag1_correlation']:<8.3f} "
        f"{row['density_iact_samples']:<7.2f} "
        f"{row['density_effective_samples']:<7.1f} "
        f"{row['screening_proxy_acceptance_vmax2']:.4e}"
    )
print(f"\nWrote {output}")

grouped = {}
for row in rows:
    grouped.setdefault(row["vmax"], []).append(row)

aggregate_rows = []
for vmax, group in sorted(grouped.items()):
    def mean(field):
        return statistics.fmean(row[field] for row in group)

    aggregate_rows.append({
        "vmax": vmax,
        "replicates": len(group),
        "mean_volume_acceptance": mean("volume_acceptance"),
        "sd_volume_acceptance": statistics.stdev(
            row["volume_acceptance"] for row in group
        ) if len(group) > 1 else math.nan,
        "mean_particle_acceptance": mean("particle_acceptance"),
        "mean_density_iact_samples": mean("density_iact_samples"),
        "median_density_iact_samples": statistics.median(
            row["density_iact_samples"] for row in group
        ),
        "mean_density_effective_samples": mean("density_effective_samples"),
        "mean_screening_proxy": mean("screening_proxy_acceptance_vmax2"),
    })

aggregate_output = stage_dir / "vmax_aggregate_summary.csv"
with aggregate_output.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=aggregate_rows[0].keys())
    writer.writeheader()
    writer.writerows(aggregate_rows)

if any(row["replicates"] > 1 for row in aggregate_rows):
    print("\nReplicate aggregate:")
    print("vmax       n   vol_acc(mean+-sd)  IACT_mean IACT_median ESS_mean")
    for row in aggregate_rows:
        print(
            f"{row['vmax']:<10.6g} {row['replicates']:<3d} "
            f"{row['mean_volume_acceptance']:.4f}+-{row['sd_volume_acceptance']:.4f}    "
            f"{row['mean_density_iact_samples']:<9.2f} "
            f"{row['median_density_iact_samples']:<11.2f} "
            f"{row['mean_density_effective_samples']:.2f}"
        )
    print(f"Wrote {aggregate_output}")
