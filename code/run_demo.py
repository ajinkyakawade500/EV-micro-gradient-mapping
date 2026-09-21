"""Regenerate all numerical outputs with the Python standard library."""

import argparse
import csv
from dataclasses import asdict
import json
import math
from pathlib import Path
import statistics

from energy_model import Vehicle, energy_for_profile, grade_at, interpolate, sample_profile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = dict(
    evidence_status="synthetic demonstration; no measured road or sensor data",
    version="0.2.0", horizontal_length_m=1200.0, mean_grade_ratio=0.005,
    reference_spacing_m=0.5, coarse_spacings_m=[5.0, 10.0, 30.0],
    grid_offset_fractions=[0.0, 0.25, 0.5, 0.75],
    amplitudes_m=[0.0, 0.25, 0.75], speeds_m_s=[8.0, 15.0, 25.0],
    regen_limits_w=[0.0, 5000.0, 20000.0],
    elevation_formula="0.005*x + A*(sin(2*pi*x/40) + 0.35*sin(2*pi*x/75))",
    vehicle=asdict(Vehicle()),
    endpoints="All reconstructions retain the exact synthetic endpoint heights",
    discretization="Point sampling and linear interpolation; not a satellite DEM model",
)


def profile(spacing, amplitude, offset=0.0):
    return sample_profile(CONFIG["horizontal_length_m"], spacing, amplitude, offset,
                          CONFIG["mean_grade_ratio"])


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: f"{v:.9f}" if isinstance(v, float) else v
                             for k, v in row.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, convergence, groups = [], [], {}
    for amplitude in CONFIG["amplitudes_m"]:
        fine_x, fine_z = profile(CONFIG["reference_spacing_m"], amplitude)
        midpoint_x = [(a + b) / 2 for a, b in zip(fine_x, fine_x[1:])]
        fine_grades = grade_at(midpoint_x, fine_x, fine_z)
        for speed in CONFIG["speeds_m_s"]:
            for limit in CONFIG["regen_limits_w"]:
                vehicle = Vehicle(regen_limit_w=limit)
                reference = energy_for_profile(fine_x, fine_z, speed, vehicle)
                check_x, check_z = profile(CONFIG["reference_spacing_m"] / 2, amplitude)
                check = energy_for_profile(check_x, check_z, speed, vehicle)
                convergence.append(dict(amplitude_m=amplitude, speed_m_s=speed,
                    regen_limit_w=limit, reference_0_5m_wh=reference["battery_wh"],
                    finer_0_25m_wh=check["battery_wh"],
                    absolute_difference_wh=abs(reference["battery_wh"]-check["battery_wh"])))
                for spacing in CONFIG["coarse_spacings_m"]:
                    for offset in CONFIG["grid_offset_fractions"]:
                        xs, zs = profile(spacing, amplitude, offset)
                        predicted = energy_for_profile(xs, zs, speed, vehicle)
                        coarse_grades = grade_at(midpoint_x, xs, zs)
                        grade_rmse = math.sqrt(statistics.mean(
                            (100 * (a - b))**2 for a, b in zip(coarse_grades, fine_grades)))
                        difference = predicted["battery_wh"] - reference["battery_wh"]
                        row = dict(evidence_status="synthetic", amplitude_m=amplitude,
                            speed_m_s=speed, regen_limit_w=limit, spacing_m=spacing,
                            offset_fraction=offset, reference_battery_wh=reference["battery_wh"],
                            coarse_battery_wh=predicted["battery_wh"],
                            signed_difference_wh=difference,
                            signed_difference_pct=100*difference/reference["battery_wh"],
                            grade_rmse_percentage_points=grade_rmse,
                            reference_peak_wheel_w=reference["peak_wheel_power_w"],
                            coarse_peak_wheel_w=predicted["peak_wheel_power_w"],
                            reference_gravity_wh=reference["gravity_wh"],
                            coarse_gravity_wh=predicted["gravity_wh"],
                            reference_recovered_wh=reference["recovered_wh"],
                            coarse_recovered_wh=predicted["recovered_wh"],
                            reference_road_length_m=reference["road_length_m"],
                            coarse_road_length_m=predicted["road_length_m"],
                            reference_duration_s=reference["duration_s"],
                            coarse_duration_s=predicted["duration_s"],
                            reference_balance_residual_wh=reference["energy_balance_residual_wh"],
                            coarse_balance_residual_wh=predicted["energy_balance_residual_wh"])
                        rows.append(row)
                        groups.setdefault((amplitude, speed, limit, spacing), []).append(row)

    summaries = []
    for (amplitude, speed, limit, spacing), group in groups.items():
        differences = [r["signed_difference_wh"] for r in group]
        summaries.append(dict(amplitude_m=amplitude, speed_m_s=speed,
            regen_limit_w=limit, spacing_m=spacing,
            reference_battery_wh=group[0]["reference_battery_wh"],
            mean_signed_difference_wh=statistics.mean(differences),
            min_signed_difference_wh=min(differences), max_signed_difference_wh=max(differences),
            mean_absolute_difference_wh=statistics.mean(map(abs, differences))))
    write_csv(args.output_dir / "sensitivity.csv", rows)
    write_csv(args.output_dir / "summary.csv", summaries)
    write_csv(args.output_dir / "convergence.csv", convergence)
    (args.output_dir / "parameters.json").write_text(
        json.dumps(CONFIG, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    # One disclosed example for plotting, with full sensitivity results above.
    xs, zs = profile(CONFIG["reference_spacing_m"], 0.75)
    points = [dict(x_m=x, reference_z_m=z) for x, z in zip(xs, zs)]
    for spacing in CONFIG["coarse_spacings_m"]:
        cx, cz = profile(spacing, 0.75)
        for row, height in zip(points, interpolate(xs, cx, cz)):
            row[f"sampled_{int(spacing)}m_z_m"] = height
    write_csv(args.output_dir / "example_profile.csv", points)

    selected = [r for r in summaries if r["amplitude_m"] == 0.75
                and r["speed_m_s"] == 15.0 and r["regen_limit_w"] == 5000.0]
    text = ["# Synthetic experiment results", "",
        "Generated by `python code/run_demo.py`. These are simulated differences, not field accuracy or range improvements.", "",
        "## Disclosed example", "",
        "A 1.2-km horizontal profile, amplitude parameter 0.75 m, road-path speed 15 m/s (54 km/h), and battery-side regeneration cap 5 kW. Other assumptions are in [parameters.json](parameters.json).", "",
        "| Sample spacing | Reference energy (Wh) | Mean coarse minus reference (Wh) | Range across four grid offsets (Wh) |",
        "|---|---:|---:|---:|"]
    for row in selected:
        text.append(f"| {row['spacing_m']:g} m | {row['reference_battery_wh']:.3f} | "
                    f"{row['mean_signed_difference_wh']:+.3f} | "
                    f"{row['min_signed_difference_wh']:+.3f} to {row['max_signed_difference_wh']:+.3f} |")
    largest = max(r["absolute_difference_wh"] for r in convergence)
    text += ["", "Negative values mean the coarse representation predicts less energy than the 0.5-m numerical reference. The ranges describe four deterministic grid alignments; they are not confidence intervals.", "",
        "## Reproduction and interpretation", "",
        f"- The full sweep contains {len(rows)} combinations; [sensitivity.csv](sensitivity.csv) includes every one.",
        "- [summary.csv](summary.csv) groups the four grid offsets without discarding any scenarios.",
        "- Amplitude zero is a constant-grade control, not a level road; its endpoint rise is 6 m.",
        "- Both endpoints are anchored, so net gravitational work is identical for every sampling resolution.",
        "- Curved-path length and travel time vary slightly with reconstruction; their effects on aerodynamic and auxiliary energy are retained and reported.",
        f"- Refining the reference from 0.5 m to 0.25 m changes energy by at most {largest:.6f} Wh in this sweep; see [convergence.csv](convergence.csv).",
        "- A finer noise-free profile is not a demonstrated sensor product. Real observations may introduce noise, bias, incorrect road matching and missing data.",
        "- No measured DEM, EV, battery, acoustic model, road, or mapping fleet is represented by these results.", ""]
    (args.output_dir / "README.md").write_text("\n".join(text), encoding="utf-8")
    print(f"Generated {len(rows)} synthetic scenarios; max reference refinement change {largest:.6f} Wh")


if __name__ == "__main__":
    main()
