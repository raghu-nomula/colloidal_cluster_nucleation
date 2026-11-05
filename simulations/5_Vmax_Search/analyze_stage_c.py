#!/usr/bin/env python3
"""Stage C Vmax refinement analysis and plots."""

import csv
import math
import re
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / "runs" / "stage_c"
PLOTS = ROOT / "plots" / "stage_c"
NOTE = ROOT / "notes" / "STAGE_C_ANALYSIS_AND_DECISION.md"


def read_csv(path):
    with path.open(newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            rows.append({key: try_float(value) for key, value in row.items()})
        return rows


def try_float(value):
    try:
        return float(value)
    except ValueError:
        return value


def grouped(rows, key):
    groups = {}
    for row in rows:
        groups.setdefault(row[key], []).append(row)
    return dict(sorted(groups.items()))


def mean(values):
    return statistics.fmean(values)


def sd(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def sem(values):
    return sd(values) / math.sqrt(len(values)) if values else math.nan


def label_vmax(value):
    return f"{value:.5f}".rstrip("0").rstrip(".")


def positive_sequence_iact(values):
    count = len(values)
    if count < 4:
        return math.nan
    m = mean(values)
    variance_sum = sum((value - m) ** 2 for value in values)
    if variance_sum == 0.0:
        return math.nan
    total = 1.0
    for lag in range(1, count // 2):
        corr = sum(
            (values[i] - m) * (values[i - lag] - m)
            for i in range(lag, count)
        ) / variance_sum
        if corr <= 0.0:
            break
        total += 2.0 * corr
    return max(1.0, total)


def lag_one(values):
    if len(values) < 3:
        return math.nan
    m = mean(values)
    den = sum((value - m) ** 2 for value in values)
    if den == 0.0:
        return math.nan
    return sum((values[i] - m) * (values[i - 1] - m) for i in range(1, len(values))) / den


def load_metrics(run_dir):
    records = []
    with (run_dir / "run_metrics.dat").open() as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            records.append({
                "cycle": float(parts[0]),
                "energy_per_particle": float(parts[1]),
                "density": float(parts[2]),
                "eta": float(parts[3]),
                "p_continuous": float(parts[5]),
                "particle_acceptance": float(parts[8]),
                "volume_acceptance": float(parts[11]),
            })
    return records


def parse_bookkeeping(out_path):
    text = out_path.read_text()
    diffs = re.findall(r"difference\s*:\s*([+-]?\d+(?:\.\d*)?(?:[Ee][+-]?\d+)?)", text)
    energy_diff = float(diffs[-2]) if len(diffs) >= 2 else math.nan
    virial_diff = float(diffs[-1]) if len(diffs) >= 1 else math.nan
    return energy_diff, virial_diff


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save(fig, name):
    PLOTS.mkdir(parents=True, exist_ok=True)
    path = PLOTS / name
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    print(path)


def error_plot(ax, groups, field, scale, color, ylabel, title):
    vmax_values = list(groups)
    xlabels = [label_vmax(value) for value in vmax_values]
    means = [scale * mean([row[field] for row in groups[value]]) for value in vmax_values]
    errors = [scale * sem([row[field] for row in groups[value]]) for value in vmax_values]
    ax.errorbar(xlabels, means, yerr=errors, color=color, marker="o", capsize=4, linewidth=1.5)
    for i, value in enumerate(vmax_values):
        ax.scatter(
            [xlabels[i]] * len(groups[value]),
            [scale * row[field] for row in groups[value]],
            color=color,
            alpha=0.45,
            s=28,
            zorder=3,
        )
    ax.set_xlabel("vmax")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.25)


def make_block_rows(rows):
    block_rows = []
    windows = [(0, 5000), (5000, 10000), (10000, 15000), (15000, 20000), (10000, 20000)]
    for row in rows:
        records = load_metrics(STAGE / row["run"])
        for start, end in windows:
            values = [record["density"] for record in records if start <= record["cycle"] <= end]
            iact = positive_sequence_iact(values)
            block_rows.append({
                "run": row["run"],
                "vmax": row["vmax"],
                "seed": int(row["seed"]),
                "block_start": start,
                "block_end": end,
                "saved_density_samples": len(values),
                "mean_density": mean(values),
                "sd_density": sd(values),
                "lag1": lag_one(values),
                "iact_samples": iact,
                "iact_cycles": iact * 25.0 if math.isfinite(iact) else math.nan,
                "ess": len(values) / iact if math.isfinite(iact) else math.nan,
            })
    write_csv(
        STAGE / "stage_c_block_iact.csv",
        block_rows,
        ["run", "vmax", "seed", "block_start", "block_end", "saved_density_samples", "mean_density", "sd_density", "lag1", "iact_samples", "iact_cycles", "ess"],
    )
    return block_rows


def make_bookkeeping_rows(rows):
    book_rows = []
    for row in rows:
        energy_diff, virial_diff = parse_bookkeeping(STAGE / row["run"] / "out")
        book_rows.append({
            "run": row["run"],
            "vmax": row["vmax"],
            "seed": int(row["seed"]),
            "energy_difference": energy_diff,
            "abs_energy_difference": abs(energy_diff),
            "virial_difference": virial_diff,
            "abs_virial_difference": abs(virial_diff),
        })
    write_csv(
        STAGE / "stage_c_bookkeeping.csv",
        book_rows,
        ["run", "vmax", "seed", "energy_difference", "abs_energy_difference", "virial_difference", "abs_virial_difference"],
    )
    return book_rows


def plot_summary(rows):
    groups = grouped(rows, "vmax")
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.2))
    error_plot(axes[0, 0], groups, "volume_acceptance", 100.0, "#1f77b4", "Volume acceptance (%)", "Volume acceptance")
    error_plot(axes[0, 1], groups, "density_iact_samples", 1.0, "#d62728", "IACT (saved density samples)", "Density IACT")
    error_plot(axes[1, 0], groups, "density_effective_samples", 1.0, "#9467bd", "Effective density samples", "ESS")
    error_plot(axes[1, 1], groups, "mean_density_second_half", 1.0, "#2ca02c", "Mean density, second half", "Actual density")
    save(fig, "stage_c_summary_acceptance_iact_ess_density.png")


def plot_seed_consistency(rows):
    groups_by_seed = grouped(rows, "seed")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2))
    for seed, seed_rows in groups_by_seed.items():
        seed_rows = sorted(seed_rows, key=lambda row: row["vmax"])
        labels = [label_vmax(row["vmax"]) for row in seed_rows]
        ax1.plot(labels, [row["density_iact_samples"] for row in seed_rows], marker="o", label=f"seed {int(seed)}")
        ax2.plot(labels, [row["density_effective_samples"] for row in seed_rows], marker="o", label=f"seed {int(seed)}")
    ax1.set_xlabel("vmax")
    ax1.set_ylabel("IACT (saved samples)")
    ax1.set_title("Seed consistency: IACT")
    ax1.grid(True, axis="y", alpha=0.25)
    ax2.set_xlabel("vmax")
    ax2.set_ylabel("ESS")
    ax2.set_title("Seed consistency: ESS")
    ax2.grid(True, axis="y", alpha=0.25)
    ax2.legend(frameon=False, fontsize=8)
    save(fig, "stage_c_seed_consistency.png")


def plot_density_traces(rows):
    groups = grouped(rows, "vmax")
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    fig, axes = plt.subplots(len(groups), 1, figsize=(9.0, 10.0), sharex=True, sharey=True)
    for ax, (color, (vmax, group)) in zip(axes, zip(colors, groups.items())):
        for row in sorted(group, key=lambda item: item["seed"]):
            records = load_metrics(STAGE / row["run"])
            ax.plot(
                [record["cycle"] for record in records],
                [record["density"] for record in records],
                color=color,
                alpha=0.68,
                linewidth=0.9,
                label=f"seed {int(row['seed'])}",
            )
        ax.axvline(10000, color="#666666", linestyle="--", linewidth=0.9, alpha=0.75)
        ax.set_ylabel("density")
        ax.set_title(f"vmax={label_vmax(vmax)}")
        ax.grid(True, alpha=0.18)
        ax.legend(loc="upper right", frameon=False, fontsize=8)
    axes[-1].set_xlabel("MC cycle")
    fig.suptitle("Stage C density traces; dashed line marks second-half analysis window", y=0.995)
    save(fig, "stage_c_density_traces.png")


def plot_block_iact(block_rows):
    four_blocks = [row for row in block_rows if row["block_end"] - row["block_start"] == 5000]
    groups = grouped(four_blocks, "vmax")
    block_labels = ["0-5k", "5-10k", "10-15k", "15-20k"]
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4))
    for vmax, rows in groups.items():
        means = []
        errs = []
        for start in [0, 5000, 10000, 15000]:
            vals = [row["iact_samples"] for row in rows if row["block_start"] == start]
            means.append(mean(vals))
            errs.append(sem(vals))
        axes[0].errorbar(block_labels, means, yerr=errs, marker="o", capsize=3, label=label_vmax(vmax))
    axes[0].set_xlabel("Cycle block")
    axes[0].set_ylabel("IACT (saved samples)")
    axes[0].set_title("Block-wise IACT mean across seeds")
    axes[0].grid(True, axis="y", alpha=0.25)
    axes[0].legend(title="vmax", frameon=False, fontsize=8)

    late = [row for row in block_rows if row["block_start"] == 10000 and row["block_end"] == 20000]
    late_groups = grouped(late, "vmax")
    xlabels = [label_vmax(value) for value in late_groups]
    means = [mean([row["iact_samples"] for row in late_groups[value]]) for value in late_groups]
    errs = [sem([row["iact_samples"] for row in late_groups[value]]) for value in late_groups]
    axes[1].errorbar(xlabels, means, yerr=errs, marker="o", capsize=4, color="#d62728")
    for i, value in enumerate(late_groups):
        axes[1].scatter([xlabels[i]] * len(late_groups[value]), [row["iact_samples"] for row in late_groups[value]], color="#d62728", alpha=0.45)
    axes[1].set_xlabel("vmax")
    axes[1].set_ylabel("IACT (saved samples)")
    axes[1].set_title("Second-half IACT used for decision")
    axes[1].grid(True, axis="y", alpha=0.25)
    save(fig, "stage_c_block_iact.png")


def plot_bookkeeping(book_rows):
    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    labels = [row["run"].replace("vmax_", "v").replace("_seed_", " s") for row in book_rows]
    values = [max(row["abs_virial_difference"], 1e-18) for row in book_rows]
    ax.bar(range(len(values)), values, color="#4c78a8")
    ax.set_yscale("log")
    ax.set_ylabel("abs(final virial bookkeeping difference)")
    ax.set_title("Stage C virial bookkeeping is roundoff-level")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    ax.grid(True, axis="y", alpha=0.25)
    save(fig, "stage_c_bookkeeping.png")


def summarize(rows, block_rows, book_rows):
    groups = grouped(rows, "vmax")
    lines = []
    lines.append("# Stage C analysis and Vmax decision\n")
    lines.append("## Data used\n")
    lines.append("Stage C contains 15 completed runs: five `vmax` values, three seeds each, `20000` cycles, and `nsamp=25`. IACT is calculated from the saved density series in the second half of each run, so one IACT unit is one saved sample, i.e. 25 MC cycles.\n")
    lines.append("## Aggregate summary\n")
    lines.append("| vmax | volume acceptance | mean IACT | median IACT | mean ESS | mean density |\n")
    lines.append("|---:|---:|---:|---:|---:|---:|\n")
    for vmax, group in groups.items():
        lines.append(
            f"| {vmax:.5f} | {100.0 * mean([r['volume_acceptance'] for r in group]):.2f}% | "
            f"{mean([r['density_iact_samples'] for r in group]):.2f} | "
            f"{statistics.median([r['density_iact_samples'] for r in group]):.2f} | "
            f"{mean([r['density_effective_samples'] for r in group]):.2f} | "
            f"{mean([r['mean_density_second_half'] for r in group]):.5f} |\n"
        )
    lines.append("\n## Interpretation\n")
    lines.append("The refined scan does not support moving above `vmax=0.0005`. The higher values reduce volume acceptance and do not give a robust IACT or ESS improvement. `vmax=0.0006` is better than `0.0005` by the mean IACT/ESS numbers, but it is not a stable minimum and it costs acceptance. `0.00065` and `0.00070` are worse by the sampling-efficiency criteria.\n")
    lines.append("The strongest Stage C candidate is `vmax=0.0004`: it has the lowest mean and median IACT, the highest mean ESS, and still has healthy volume acceptance near 26%. Its high ESS is not caused by one single lucky seed; two of the three seeds have low IACT/high ESS, while one seed is slower.\n")
    lines.append("## Recommended decision\n")
    lines.append("Use `vmax=0.0004` for the next `dr=0.01` NpT production branch, unless there is a separate reason to preserve exact continuity with older `vmax=0.0005` campaigns. The old `0.0005` value remains acceptable, but Stage C gives a better data-driven choice: `0.0004`.\n")
    lines.append("This decision should be described as an algorithmic sampling choice, not as a physical densification or nucleation mechanism.\n")
    lines.append("## Files generated\n")
    for name in [
        "stage_c_summary_acceptance_iact_ess_density.png",
        "stage_c_seed_consistency.png",
        "stage_c_density_traces.png",
        "stage_c_block_iact.png",
        "stage_c_bookkeeping.png",
    ]:
        lines.append(f"- `plots/stage_c/{name}`\n")
    lines.append("- `runs/stage_c/stage_c_block_iact.csv`\n")
    lines.append("- `runs/stage_c/stage_c_bookkeeping.csv`\n")
    max_energy = max(row["abs_energy_difference"] for row in book_rows)
    max_virial = max(row["abs_virial_difference"] for row in book_rows)
    lines.append("\n## Bookkeeping\n")
    lines.append(f"Maximum absolute final energy bookkeeping difference: `{max_energy:.3e}`.\n")
    lines.append(f"Maximum absolute final virial bookkeeping difference: `{max_virial:.3e}`. These are roundoff-level values.\n")
    NOTE.write_text("".join(lines))
    print(NOTE)


def main():
    rows = read_csv(STAGE / "vmax_summary.csv")
    rows.sort(key=lambda row: (row["vmax"], row["seed"]))
    block_rows = make_block_rows(rows)
    book_rows = make_bookkeeping_rows(rows)
    plot_summary(rows)
    plot_seed_consistency(rows)
    plot_density_traces(rows)
    plot_block_iact(block_rows)
    plot_bookkeeping(book_rows)
    summarize(rows, block_rows, book_rows)


if __name__ == "__main__":
    main()
