"""Pruebas sinteticas de EXP-008."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import exp008_disoluciones as d  # noqa: E402


class Percentiles(unittest.TestCase):
    def test_percentile(self):
        self.assertEqual(d.percentile(5, [1, 2, 3, 4, 5]), 0.9)
        self.assertEqual(d.percentile(1, [1, 2, 3, 4, 5]), 0.1)
        self.assertEqual(d.percentile(2, [2, 2, 2, 2]), 0.5)

    def test_year_percentiles_mean_half(self):
        p = d.year_percentiles([3.0, 1.0, 2.0, 5.0])
        self.assertAlmostEqual(sum(p) / len(p), 0.5)

    def test_permutation(self):
        pools = [[0.1, 0.3, 0.5, 0.7, 0.9]] * 3
        self.assertAlmostEqual(d.permutation_p(0.9, pools, draws=20000, seed=1), (1 / 5) ** 3, delta=0.004)
        self.assertEqual(d.permutation_p(0.0, pools, draws=100), 1.0)


class Analyse(unittest.TestCase):
    def test_cases_on_synthetic_rows(self):
        rows = []
        for year in (1991, 1992):
            for i in range(20):
                rows.append({"year": str(year), "ccode": str(900 + i), "country": f"C{i}",
                             "T": str(i / 20), "E": "0.5", "P": "0.5", "I": "0.5"})
            rows += [{"year": str(year), "ccode": c, "country": n, "T": str(0.99 - 0.01 * k),
                      "E": "1", "P": "1", "I": "1"}
                     for k, (n, c, y) in enumerate(d.CASES) if y == year]
        cases, mean_pct, p = d.analyse(rows)
        self.assertEqual([c["T_puesto"] for c in cases], [1, 2, 1])
        self.assertGreater(mean_pct, 0.9)
        self.assertLess(p, 0.05)


if __name__ == "__main__":
    unittest.main()
