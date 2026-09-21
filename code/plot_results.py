"""Regenerate the publication's synthetic-data figure from saved results."""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from energy_model import grade_at, sample_profile

ROOT = Path(__file__).resolve().parents[1]


def read_rows(name):
    with (ROOT / "results" / name).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", type=Path, help="Optional PNG path for visual inspection")
    args = parser.parse_args()
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.labelcolor": "#26364a", "text.color": "#15263c",
        "xtick.color": "#465569", "ytick.color": "#465569",
        "svg.fonttype": "none", "svg.hashsalt": "ev-micro-gradient-v0.2.0",
    })
    navy, teal, orange = "#17324d", "#007f82", "#cf662b"
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 10.5),
                             gridspec_kw={"height_ratios": [1.15, 1, 1.05]})
    fig.subplots_adjust(left=0.12, right=0.96, top=0.84, bottom=0.13, hspace=0.70)
    fig.text(0.12, 0.964, "SYNTHETIC EXPERIMENT  /  NO FIELD DATA", color=teal,
             fontsize=10, weight="bold")
    fig.text(0.12, 0.923, "Sampling changes an energy model's prediction", fontsize=19, weight="bold")
    fig.text(0.12, 0.886, "One disclosed stress case: 1,500 kg vehicle · 54 km/h · 5 kW regeneration cap",
             fontsize=10, color="#465569")

    rows = [row for row in read_rows("example_profile.csv") if float(row["x_m"]) <= 240]
    xs = [float(row["x_m"]) for row in rows]
    for key, label, color, style in [
        ("reference_z_m", "0.5 m numerical reference", navy, "-"),
        ("sampled_5m_z_m", "5 m samples", teal, "--"),
        ("sampled_30m_z_m", "30 m samples", orange, "-")]:
        axes[0].plot(xs, [float(row[key]) for row in rows], color=color,
                     linewidth=1.6, linestyle=style, label=label)
    axes[0].set(title="A  |  Interior height changes depend on sampling", ylabel="Height (m)",
                xlabel="Horizontal chainage (m); first 240 m shown", xlim=(0, 240))
    axes[0].legend(loc="upper left", frameon=False, fontsize=8, ncol=3,
                   bbox_to_anchor=(0, 1.01))

    midpoints = [(a+b)/2 for a, b in zip(xs, xs[1:])]
    for spacing, color, style in [(0.5, navy, "-"), (5, teal, "--"), (30, orange, "-")]:
        px, pz = sample_profile(1200, spacing, 0.75)
        axes[1].plot(midpoints, [100*g for g in grade_at(midpoints, px, pz)],
                     color=color, linestyle=style, linewidth=1.4)
    axes[1].axhline(0, color="#9aa8b6", linewidth=0.7)
    axes[1].set(title="B  |  Grade is a derivative, not a height", ylabel="Grade (%)",
                xlabel="Horizontal chainage (m)", xlim=(0, 240))

    summaries = [row for row in read_rows("summary.csv")
                 if float(row["amplitude_m"]) == 0.75
                 and float(row["speed_m_s"]) == 15
                 and float(row["regen_limit_w"]) == 5000]
    reference = float(summaries[0]["reference_battery_wh"])
    for position, row in enumerate(summaries):
        mean = reference + float(row["mean_signed_difference_wh"])
        low = reference + float(row["min_signed_difference_wh"])
        high = reference + float(row["max_signed_difference_wh"])
        axes[2].errorbar(mean, position, xerr=[[mean-low], [high-mean]],
                         fmt="o", color=teal, markersize=7, capsize=5, linewidth=1.8)
        axes[2].text(mean-5, position+0.23, f"{mean:.1f} Wh", ha="right", fontsize=9)
    axes[2].axvline(reference, color=navy, linestyle="--", linewidth=1.4)
    axes[2].text(reference+3, 1.15, f"Reference\n{reference:.1f} Wh", fontsize=9, color=navy)
    axes[2].set(yticks=[0, 1, 2], yticklabels=["5 m", "10 m", "30 m"],
                xlabel="Net battery energy over 1.2 km horizontal distance (Wh)",
                ylabel="Sample spacing", xlim=(0, 272), ylim=(2.55, -0.55),
                title="C  |  Mean and range across four grid alignments")
    for ax in axes:
        ax.grid(axis="y" if ax != axes[2] else "x", alpha=0.16)
        ax.set_axisbelow(True)
        ax.title.set_fontsize(11)
        ax.title.set_weight("bold")
        ax.title.set_position((0.5, 1.05))
    fig.text(0.12, 0.075, "Ranges show grid alignment sensitivity, not confidence intervals. All endpoints are exact.",
             fontsize=9, color="#465569")
    fig.text(0.12, 0.052, "Illustrative assumptions and excluded dynamics limit interpretation. Full sweep: 324 combinations.",
             fontsize=9, color="#465569")
    fig.text(0.12, 0.029, "Source: repository simulation · v0.2.0 · No real-world range improvement is established.",
             fontsize=9, color="#465569")
    destination = ROOT / "figures" / "sampling_energy.svg"
    destination.parent.mkdir(exist_ok=True)
    fig.savefig(destination, metadata={"Date": None,
        "Description": "Synthetic profile sensitivity, not measured road data or demonstrated accuracy gains."})
    # Keep generated XML friendly to Git whitespace checks without changing paths.
    destination.write_text("\n".join(line.rstrip() for line in
                           destination.read_text(encoding="utf-8").splitlines()) + "\n",
                           encoding="utf-8")
    if args.preview:
        fig.savefig(args.preview, dpi=140)
    plt.close(fig)
    print(f"Wrote {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
