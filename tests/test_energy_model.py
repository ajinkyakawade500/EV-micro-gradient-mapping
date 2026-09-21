"""Analytical and conservation checks, not claims of empirical validation."""

from dataclasses import replace
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from energy_model import GRAVITY_M_S2, Vehicle, energy_for_profile, sample_profile


class EnergyModelTests(unittest.TestCase):
    def setUp(self):
        self.ideal = Vehicle(crr=0, drag_area_m2=0, drive_efficiency=1,
                             regen_efficiency=1, auxiliary_w=0, regen_limit_w=1e9)

    def test_flat_road_matches_analytical_solution(self):
        vehicle, speed, length = Vehicle(), 12.0, 1000.0
        force = (vehicle.mass_kg * GRAVITY_M_S2 * vehicle.crr
                 + 0.5 * vehicle.air_density_kg_m3 * vehicle.drag_area_m2 * speed**2)
        expected = (force * length / vehicle.drive_efficiency
                    + vehicle.auxiliary_w * length / speed) / 3600
        result = energy_for_profile([0, length], [0, 0], speed, vehicle)
        self.assertAlmostEqual(result["battery_wh"], expected, places=10)

    def test_lossless_hill_with_equal_endpoints_has_zero_net_energy(self):
        result = energy_for_profile([0, 100, 200], [0, 10, 0], 10, self.ideal)
        self.assertAlmostEqual(result["battery_wh"], 0, places=10)
        self.assertGreater(result["peak_wheel_power_w"], 0)

    def test_gravity_depends_on_endpoint_heights_not_profile_shape(self):
        x, z = [0, 100, 200, 300], [4, 12, -2, 9]
        result = energy_for_profile(x, z, 8, self.ideal)
        expected = self.ideal.mass_kg * GRAVITY_M_S2 * (z[-1]-z[0]) / 3600
        self.assertAlmostEqual(result["battery_wh"], expected, places=10)

    def test_conversion_losses_are_positive_on_a_closed_hill(self):
        vehicle = replace(self.ideal, drive_efficiency=0.9, regen_efficiency=0.6)
        result = energy_for_profile([0, 100, 200], [0, 10, 0], 10, vehicle)
        expected = vehicle.mass_kg * GRAVITY_M_S2 * 10 * (1/0.9-0.6) / 3600
        self.assertAlmostEqual(result["battery_wh"], expected, places=10)

    def test_regeneration_cap_respects_power_and_lost_energy(self):
        x, z, speed = [0, 100], [20, 0], 10
        uncapped = energy_for_profile(x, z, speed, self.ideal)
        capped = energy_for_profile(x, z, speed, replace(self.ideal, regen_limit_w=1000))
        expected_recovered = 1000 * math.hypot(100, 20) / speed / 3600
        self.assertAlmostEqual(capped["recovered_wh"], expected_recovered, places=10)
        self.assertGreater(capped["battery_wh"], uncapped["battery_wh"])
        self.assertGreater(capped["friction_brake_wh"], 0)

    def test_zero_regeneration_has_no_recovery_and_no_division_by_zero(self):
        result = energy_for_profile([0, 100], [10, 0], 8,
                                    replace(self.ideal, regen_efficiency=0))
        self.assertEqual(result["recovered_wh"], 0)
        self.assertGreater(result["friction_brake_wh"], 0)

    def test_complete_energy_balance_with_losses_and_auxiliaries(self):
        x, z = sample_profile(1200, 0.5, 0.75)
        result = energy_for_profile(x, z, 15, Vehicle())
        self.assertLess(abs(result["energy_balance_residual_wh"]), 1e-8)

    def test_linear_grade_is_invariant_to_spacing_and_offset(self):
        x, z = sample_profile(1200, 0.5, 0.0)
        reference = energy_for_profile(x, z, 15, Vehicle())["battery_wh"]
        for spacing in (5, 10, 30):
            for offset in (0, 0.25, 0.5, 0.75):
                cx, cz = sample_profile(1200, spacing, 0.0, offset)
                value = energy_for_profile(cx, cz, 15, Vehicle())["battery_wh"]
                self.assertAlmostEqual(value, reference, places=8)

    def test_invalid_inputs_fail_explicitly(self):
        cases = [([0, 0], [0, 1], 10), ([0, 1], [0], 10),
                 ([0, 1], [0, float("nan")], 10), ([0, 1], [0, 1], 0)]
        for x, z, speed in cases:
            with self.assertRaises(ValueError):
                energy_for_profile(x, z, speed, Vehicle())
        with self.assertRaises(ValueError):
            Vehicle(drive_efficiency=1.1)


if __name__ == "__main__":
    unittest.main()
