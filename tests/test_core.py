from __future__ import annotations

import unittest

from logisticlab.core import classify_parameter, detect_period, feigenbaum_estimates, histogram_density, invariant_density_r4, iterate, logistic, lyapunov_exponent, orbit_density, sample_tail, scan_superstable_doubling


class LogisticCoreTests(unittest.TestCase):
    def test_logistic_step(self) -> None:
        self.assertAlmostEqual(logistic(3.5, 0.5), 0.875)

    def test_iterate_count(self) -> None:
        self.assertEqual(len(iterate(3.2, 0.2, 12)), 12)

    def test_sample_tail_stays_bounded(self) -> None:
        values = sample_tail(3.7)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in values))

    def test_stable_fixed_point_matches_closed_form(self) -> None:
        r = 2.9
        values = sample_tail(r, warmup=1200, keep=20)
        fixed_point = 1.0 - 1.0 / r
        self.assertAlmostEqual(sum(values) / len(values), fixed_point, places=5)

    def test_lyapunov_signs(self) -> None:
        self.assertLess(lyapunov_exponent(2.9), 0.0)
        self.assertGreater(lyapunov_exponent(3.9), 0.0)

    def test_histogram_density_normalizes_area(self) -> None:
        bins = histogram_density([0.1, 0.2, 0.4, 0.8], bins=4)
        width = 1.0 / 4.0
        area = sum(value for _, value in bins) * width
        self.assertAlmostEqual(area, 1.0, places=8)

    def test_invariant_density_r4_is_symmetric(self) -> None:
        self.assertAlmostEqual(invariant_density_r4(0.2), invariant_density_r4(0.8), places=8)

    def test_orbit_density_at_r4_is_edge_heavier_than_center(self) -> None:
        density = orbit_density(4.0, keep=12000, bins=48)
        center = density[len(density) // 2][1]
        self.assertGreater(density[0][1], center)
        self.assertGreater(density[-1][1], center)

    def test_detect_period_finds_stable_fixed_point(self) -> None:
        tail = sample_tail(2.9, warmup=1500, keep=120)
        self.assertEqual(detect_period(tail, max_period=8), 1)

    def test_detect_period_finds_period_two_window(self) -> None:
        tail = sample_tail(3.2, warmup=1800, keep=160)
        self.assertEqual(detect_period(tail, max_period=8), 2)

    def test_classify_parameter_leaves_chaotic_case_unresolved(self) -> None:
        row = classify_parameter(3.9, warmup=2400, keep=220, max_period=16)
        self.assertIsNone(row.detected_period)
        self.assertGreater(row.lyapunov, 0.0)

    def test_superstable_points_increase_and_delta_is_reasonable(self) -> None:
        points = scan_superstable_doubling(5)
        self.assertEqual([point.period for point in points], [2, 4, 8, 16, 32])
        self.assertEqual(sorted(point.r for point in points), [point.r for point in points])
        estimates = feigenbaum_estimates(points)
        self.assertGreaterEqual(len(estimates), 3)
        self.assertTrue(all(3.0 < estimate.delta < 6.0 for estimate in estimates[-2:]))


if __name__ == '__main__':
    unittest.main()
