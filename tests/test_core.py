from __future__ import annotations

import math
import unittest

from logisticlab.core import iterate, logistic, lyapunov_exponent, sample_tail


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


if __name__ == '__main__':
    unittest.main()
