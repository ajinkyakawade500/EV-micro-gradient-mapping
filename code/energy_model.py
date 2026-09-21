"""Small, auditable energy model for a SYNTHETIC road-profile experiment.

No sensor fusion, measured road data, SOC dynamics, or routing is implemented.
Units are SI internally; positive battery energy means discharge. See the paper
for the distinction between horizontal chainage x and road-path distance s.
"""

from dataclasses import dataclass
import math

GRAVITY_M_S2 = 9.80665


@dataclass(frozen=True)
class Vehicle:
    mass_kg: float = 1500.0
    crr: float = 0.010
    drag_area_m2: float = 0.65
    air_density_kg_m3: float = 1.225
    drive_efficiency: float = 0.90
    regen_efficiency: float = 0.65
    auxiliary_w: float = 300.0
    # Battery-side recovered-power limit, before subtracting auxiliary demand.
    regen_limit_w: float = 5000.0

    def __post_init__(self):
        for name, value in vars(self).items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.mass_kg <= 0 or not 0 < self.drive_efficiency <= 1:
            raise ValueError("Positive mass and 0 < drive efficiency <= 1 required")
        if not 0 <= self.regen_efficiency <= 1:
            raise ValueError("Regeneration efficiency must be in [0, 1]")
        for name in ("crr", "drag_area_m2", "air_density_kg_m3",
                     "auxiliary_w", "regen_limit_w"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")


def validate_profile(x_m, z_m):
    if len(x_m) != len(z_m) or len(x_m) < 2:
        raise ValueError("A profile needs at least two paired x/z coordinates")
    if not all(math.isfinite(v) for v in (*x_m, *z_m)):
        raise ValueError("Profile coordinates must be finite")
    if any(b <= a for a, b in zip(x_m, x_m[1:])):
        raise ValueError("Horizontal chainage must be strictly increasing")


def synthetic_height(x_m, amplitude_m, mean_grade=0.005):
    """Invented profile, not a sample from SRTM, Copernicus, or any road."""
    return mean_grade * x_m + amplitude_m * (
        math.sin(2 * math.pi * x_m / 40.0)
        + 0.35 * math.sin(2 * math.pi * x_m / 75.0)
    )


def sample_profile(length_m, spacing_m, amplitude_m, offset_fraction=0.0,
                   mean_grade=0.005):
    """Point-sample a synthetic height function; keep both endpoints exact.

    Offset is a fraction of spacing. Endpoint anchoring isolates interior
    profile loss and deliberately excludes endpoint elevation uncertainty.
    """
    parameters = (length_m, spacing_m, amplitude_m, offset_fraction, mean_grade)
    if not all(math.isfinite(v) for v in parameters):
        raise ValueError("Sampling parameters must be finite")
    if length_m <= 0 or spacing_m <= 0 or amplitude_m < 0:
        raise ValueError("Positive length/spacing and non-negative amplitude required")
    if not 0 <= offset_fraction < 1:
        raise ValueError("Grid offset fraction must be in [0, 1)")
    xs = [0.0]
    first = spacing_m * offset_fraction
    if first == 0.0:
        first = spacing_m
    count = max(0, math.ceil((length_m - first) / spacing_m))
    xs.extend(first + i * spacing_m for i in range(count)
              if first + i * spacing_m < length_m)
    xs.append(float(length_m))
    return xs, [synthetic_height(x, amplitude_m, mean_grade) for x in xs]


def interpolate(query_x, sample_x, sample_z):
    """Piecewise-linear interpolation without extrapolation."""
    validate_profile(sample_x, sample_z)
    if any(b < a for a, b in zip(query_x, query_x[1:])):
        raise ValueError("Interpolation queries must be ordered")
    if not all(math.isfinite(x) and sample_x[0] <= x <= sample_x[-1]
               for x in query_x):
        raise ValueError("Interpolation queries must lie within the profile")
    out, index = [], 0
    for x in query_x:
        while index < len(sample_x) - 2 and sample_x[index + 1] < x:
            index += 1
        fraction = (x - sample_x[index]) / (sample_x[index + 1] - sample_x[index])
        out.append(sample_z[index] + fraction * (sample_z[index + 1] - sample_z[index]))
    return out


def grade_at(query_x, sample_x, sample_z):
    """Grade ratio dz/dx of each interpolated straight segment."""
    validate_profile(sample_x, sample_z)
    if not all(math.isfinite(x) and sample_x[0] <= x <= sample_x[-1]
               for x in query_x):
        raise ValueError("Grade queries must lie within the profile")
    if any(b < a for a, b in zip(query_x, query_x[1:])):
        raise ValueError("Grade queries must be ordered")
    result, index = [], 0
    for x in query_x:
        while index < len(sample_x) - 2 and sample_x[index + 1] < x:
            index += 1
        result.append((sample_z[index + 1] - sample_z[index]) /
                      (sample_x[index + 1] - sample_x[index]))
    return result


def energy_for_profile(x_m, z_m, speed_m_s, vehicle):
    """Integrate exact segment work along a piecewise-linear profile.

    Speed is constant along the 3-D road path. Acceleration, wind, rotational
    inertia, banking, tyre changes, motor power limits and SOC limits are absent.
    Positive/negative wheel work is converted with separate efficiencies.
    Braking beyond the recovered-power cap becomes friction-brake heat.
    """
    validate_profile(x_m, z_m)
    if not math.isfinite(speed_m_s) or speed_m_s <= 0:
        raise ValueError("A finite positive road-path speed is required")
    totals = dict(battery_wh=0.0, traction_draw_wh=0.0, recovered_wh=0.0,
                  auxiliary_wh=0.0, gravity_wh=0.0, rolling_wh=0.0,
                  aerodynamic_wh=0.0, drive_loss_wh=0.0, regen_loss_wh=0.0,
                  friction_brake_wh=0.0, road_length_m=0.0, duration_s=0.0,
                  peak_wheel_power_w=0.0, peak_braking_power_w=0.0)
    mg = vehicle.mass_kg * GRAVITY_M_S2
    drag_n = 0.5 * vehicle.air_density_kg_m3 * vehicle.drag_area_m2 * speed_m_s**2
    for x0, x1, z0, z1 in zip(x_m, x_m[1:], z_m, z_m[1:]):
        dx, dz = x1 - x0, z1 - z0
        ds = math.hypot(dx, dz)
        dt = ds / speed_m_s
        gravity_j = mg * dz
        # N = mg*cos(theta), and cos(theta)*ds = dx in this unbanked model.
        rolling_j = mg * vehicle.crr * dx
        aero_j = drag_n * ds
        wheel_j = gravity_j + rolling_j + aero_j
        wheel_w = wheel_j / dt
        draw_j = max(wheel_j, 0.0) / vehicle.drive_efficiency
        braking_j = max(-wheel_j, 0.0)
        recovered_j = min(vehicle.regen_efficiency * braking_j,
                          vehicle.regen_limit_w * dt)
        regen_input_j = (recovered_j / vehicle.regen_efficiency
                         if vehicle.regen_efficiency > 0 else 0.0)
        auxiliary_j = vehicle.auxiliary_w * dt
        values_j = dict(
            battery_wh=draw_j - recovered_j + auxiliary_j,
            traction_draw_wh=draw_j, recovered_wh=recovered_j,
            auxiliary_wh=auxiliary_j, gravity_wh=gravity_j,
            rolling_wh=rolling_j, aerodynamic_wh=aero_j,
            drive_loss_wh=draw_j - max(wheel_j, 0.0),
            regen_loss_wh=regen_input_j - recovered_j,
            friction_brake_wh=max(0.0, braking_j - regen_input_j),
        )
        for name, value in values_j.items():
            totals[name] += value / 3600.0
        totals["road_length_m"] += ds
        totals["duration_s"] += dt
        totals["peak_wheel_power_w"] = max(totals["peak_wheel_power_w"], wheel_w)
        totals["peak_braking_power_w"] = max(totals["peak_braking_power_w"], -wheel_w)
    # Conservation check includes change in gravitational potential energy.
    loss_terms = ("gravity_wh", "rolling_wh", "aerodynamic_wh", "drive_loss_wh",
                  "regen_loss_wh", "friction_brake_wh", "auxiliary_wh")
    totals["energy_balance_residual_wh"] = totals["battery_wh"] - sum(
        totals[name] for name in loss_terms)
    return totals
