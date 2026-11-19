"""Pruebas sinteticas de EXP-007."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp007_interacciones as x  # noqa: E402
from test_exp003 import synthetic_panel  # noqa: E402


class Interacciones(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_panel(years=range(1970, 2010))

    def test_specs_differ_only_in_interactions(self):
        self.assertEqual(set(x.SPECS["MX"]) - set(x.SPECS["MXs"]), {"ExI", "PxI"})

    def test_predictions_aligned(self):
        test, preds = x.fit_predict(self.rows, test_start=1990)
        for name in ("MX", "MXs", "MX_c", "MXs_c", "MX_soloExI_c", "MX_soloPxI_c"):
            self.assertEqual(len(preds[name]), len(test))
            self.assertTrue(all(0 < p < 1 for p in preds[name]))

    def test_auc_bootstrap_zero_for_identical(self):
        ps, ys, yr = [0.1, 0.2, 0.8, 0.9, 0.3, 0.7], [0, 0, 1, 1, 0, 1], [1, 1, 2, 2, 3, 3]
        self.assertEqual(x.block_bootstrap_auc_delta(ps, ps, ys, yr, reps=50), [0.0, 0.0])
        lo, hi = x.block_bootstrap_auc_delta(ps, [0.5] * 6, ys, yr, reps=200)
        self.assertGreaterEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)

    def test_compare_structure_and_no_leak(self):
        test, preds = x.fit_predict(self.rows, test_start=1990)
        out = x.compare(test, preds, 1990, 1999, reps=20)
        self.assertIn("MX_c_vs_MXs_c", out)
        flipped = [dict(r, outcome=1 - r["outcome"]) if r["year"] >= 1995 else dict(r) for r in self.rows]
        test2, preds2 = x.fit_predict(flipped, test_start=1990)
        idx = [i for i, r in enumerate(test) if r["year"] <= 1995]
        self.assertEqual([preds["MX_c"][i] for i in idx], [preds2["MX_c"][i] for i in idx])


if __name__ == "__main__":
    unittest.main()
