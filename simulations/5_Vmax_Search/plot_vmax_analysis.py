#!/usr/bin/env python3
"""Create diagnostic plots for the Vmax search."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
STAGE_A = ROOT / "runs" / "stage_a"
STAGE_B = ROOT / "runs" / "stage_b"
PLOTS = ROOT / "plots"


def read_csv(path):
    with path.open(newline="") as handle:
        return [
            {
                key: try_float(value)
                for key, value in row.items()
            }
            for row in csv.DictReader(handle)
        ]


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
    return sum(values) / len(values)


def sd(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return (sum((value - m) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def sem(values):
    return sd(values) / (len(values) ** 0.5)


def label_vmax(value):
    return f"{value:.5f}".rstrip("0").rstrip(".")


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
                "volume_acceptance": float(parts[11]),
            })
    return records


def save(fig, name):
    path = PLOTS / name
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    print(path)


def plot_stage_a_acceptance(stage_a):
    fig, ax1 = plt.subplots(figsize=(7.0, 4.4))
    x = [row["vmax"] for row in stage_a]
    vol = [100.0 * row["volume_acceptance"] for row in stage_a]
    part = [100.0 * row["particle_acceptance"] for row in stage_a]

    ax1.plot(x, vol, marker="o", color="#1f77b4", label="Volume acceptance")
    ax1.set_xscale("log")
    ax1.set_xlabel("vmax")
    ax1.set_ylabel("Volume acceptance (%)", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax1.grid(True, alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(x, part, marker="s", color="#444444", label="Particle acceptance")
    ax2.set_ylabel("Particle acceptance (%)", color="#444444")
    ax2.tick_params(axis="y", labelcolor="#444444")
    ax2.set_ylim(84.0, 89.0)

    ax1.set_title("Stage A: increasing vmax lowers volume acceptance")
    save(fig, "stage_a_acceptance_vs_vmax.png")


def plot_stage_b_acceptance_and_density(stage_b):
    groups = grouped(stage_b, "vmax")
    x = list(groups)
    xlabels = [label_vmax(value) for value in x]
    vol_means = [100.0 * mean([row["volume_acceptance"] for row in groups[value]]) for value in x]
    vol_errs = [100.0 * sem([row["volume_acceptance"] for row in groups[value]]) for value in x]
    rho_means = [mean([row["mean_density_second_half"] for row in groups[value]]) for value in x]
    rho_errs = [sem([row["mean_density_second_half"] for row in groups[value]]) for value in x]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 4.0))
    ax1.errorbar(xlabels, vol_means, yerr=vol_errs, marker="o", capsize=4, color="#1f77b4")
    ax1.set_xlabel("vmax")
    ax1.set_ylabel("Volume acceptance (%)")
    ax1.set_title("Acceptance from 3 seeds")
    ax1.grid(True, axis="y", alpha=0.25)

    ax2.errorbar(xlabels, rho_means, yerr=rho_errs, marker="o", capsize=4, color="#2ca02c")
    for i, value in enumerate(x):
        ax2.scatter(
            [xlabels[i]] * len(groups[value]),
            [row["mean_density_second_half"] for row in groups[value]],
            color="#2ca02c",
            alpha=0.45,
            s=28,
        )
    ax2.set_xlabel("vmax")
    ax2.set_ylabel("Mean density, second half")
    ax2.set_title("Actual density is not largest at 0.0005")
    ax2.grid(True, axis="y", alpha=0.25)

    save(fig, "stage_b_acceptance_and_density.png")


def plot_stage_b_correlation_efficiency(stage_b):
    groups = grouped(stage_b, "vmax")
    x = list(groups)
    xlabels = [label_vmax(value) for value in x]
    iact_means = [mean([row["density_iact_samples"] for row in groups[value]]) for value in x]
    iact_errs = [sem([row["density_iact_samples"] for row in groups[value]]) for value in x]
    ess_means = [mean([row["density_effective_samples"] for row in groups[value]]) for value in x]
    ess_errs = [sem([row["density_effective_samples"] for row in groups[value]]) for value in x]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 4.0))
    ax1.errorbar(xlabels, iact_means, yerr=iact_errs, marker="o", capsize=4, color="#d62728")
    ax1.set_xlabel("vmax")
    ax1.set_ylabel("Density IACT (saved samples)")
    ax1.set_title("Lower IACT means faster decorrelation")
    ax1.grid(True, axis="y", alpha=0.25)

    ax2.errorbar(xlabels, ess_means, yerr=ess_errs, marker="o", capsize=4, color="#9467bd")
    ax2.set_xlabel("vmax")
    ax2.set_ylabel("Effective independent density samples")
    ax2.set_title("Higher ESS means better sampling efficiency")
    ax2.grid(True, axis="y", alpha=0.25)

    save(fig, "stage_b_iact_and_effective_samples.png")


def plot_stage_b_density_traces(stage_b):
    groups = grouped(stage_b, "vmax")
    colors = {
        0.0002: "#1f77b4",
        0.0003: "#ff7f0e",
        0.0005: "#2ca02c",
    }

    fig, axes = plt.subplots(len(groups), 1, figsize=(8.5, 7.5), sharex=True, sharey=True)
    if len(groups) == 1:
        axes = [axes]

    for ax, (vmax, rows) in zip(axes, groups.items()):
        for row in rows:
            run_dir = STAGE_B / row["run"]
            records = load_metrics(run_dir)
            ax.plot(
                [record["cycle"] for record in records],
                [record["density"] for record in records],
                color=colors.get(vmax, "#444444"),
                alpha=0.65,
                linewidth=1.0,
                label=f"seed {int(row['seed'])}",
            )
        ax.axvline(5000, color="#777777", linestyle="--", linewidth=0.9, alpha=0.7)
        ax.set_ylabel("density")
        ax.set_title(f"vmax={label_vmax(vmax)}")
        ax.grid(True, alpha=0.2)
        ax.legend(loc="upper right", fontsize=8, frameon=False)

    axes[-1].set_xlabel("MC cycle")
    fig.suptitle("Stage B density traces; dashed line marks second-half analysis window", y=0.995)
    save(fig, "stage_b_density_traces.png")


def main():
    PLOTS.mkdir(exist_ok=True)
    stage_a = read_csv(STAGE_A / "vmax_summary.csv")
    stage_b = read_csv(STAGE_B / "vmax_summary.csv")

    plot_stage_a_acceptance(stage_a)
    plot_stage_b_acceptance_and_density(stage_b)
    plot_stage_b_correlation_efficiency(stage_b)
    plot_stage_b_density_traces(stage_b)


if __name__ == "__main__":
    main()
