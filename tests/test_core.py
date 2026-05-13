from __future__ import annotations

import unittest

from logisticlab.core import histogram_density, invariant_density_r4, iterate, logistic, lyapunov_exponent, orbit_density, sample_tail


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


if __name__ == '__main__':
    unittest.main()
