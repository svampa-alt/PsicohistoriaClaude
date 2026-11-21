"""Pruebas sinteticas de EXP-009."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp009_recalibracion as r  # noqa: E402
from test_exp003 import synthetic_panel  # noqa: E402


class Offset(unittest.TestCase):
    def test_zero_when_calibrated(self):
        self.assertAlmostEqual(r.fit_offset([0.0] * 100, [0, 1] * 50, ridge=1e-9), 0.0, places=6)

    def test_direction(self):
        self.assertLess(r.fit_offset([0.0] * 100, [0] * 90 + [1] * 10), 0)
        self.assertGreater(r.fit_offset([-3.0] * 100, [0] * 50 + [1] * 50), 0)

    def test_ridge_shrinks(self):
        logits, ys = [0.0] * 20, [0] * 18 + [1] * 2
        self.assertLess(abs(r.fit_offset(logits, ys, ridge=10)), abs(r.fit_offset(logits, ys, ridge=0.01)))


class Run(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_panel(years=range(1970, 2005))

    def test_models_and_no_leak(self):
        test, preds, offsets = r.run(self.rows, test_start=1990)
        self.assertEqual(set(preds), {"B0", "MH", "MXs", "MXs_c10", "MXs_c5", "MXs_r5"})
        flipped = [dict(x, outcome=1 - x["outcome"]) if x["year"] >= 1996 else dict(x) for x in self.rows]
        test2, preds2, offsets2 = r.run(flipped, test_start=1990)
        for year in range(1990, 1997):
            self.assertEqual(offsets[year], offsets2[year])
        self.assertNotEqual(offsets[2000], offsets2[2000])

    def test_window_stats(self):
        test, preds, _ = r.run(self.rows, test_start=1990)
        w = r.window_stats(test, preds, 1990, 2004, reps=20)
        self.assertIn("ic95_vs_MXs_c10", w["modelos"]["MXs_r5"])


if __name__ == "__main__":
    unittest.main()
