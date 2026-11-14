"""Pruebas sinteticas de EXP-004 (sin datos reales)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp004_tendencia as t  # noqa: E402
from test_exp003 import synthetic_panel  # noqa: E402


class Shift(unittest.TestCase):
    def test_identity_when_rates_equal(self):
        for p in (0.01, 0.3, 0.9):
            self.assertAlmostEqual(t.shift(p, 0.05, 0.05), p)

    def test_direction_and_bounds(self):
        self.assertLess(t.shift(0.2, 0.02, 0.06), 0.2)
        self.assertGreater(t.shift(0.2, 0.10, 0.06), 0.2)
        for p in (1e-6, 0.5, 1 - 1e-6):
            self.assertTrue(0.0 < t.shift(p, 0.01, 0.2) < 1.0)

    def test_preserves_order(self):
        ps = [0.01, 0.05, 0.2, 0.7]
        out = [t.shift(p, 0.02, 0.06) for p in ps]
        self.assertEqual(out, sorted(out))

    def test_base_rate_maps_to_recent_rate(self):
        self.assertAlmostEqual(t.shift(0.06, 0.02, 0.06), 0.02)


class Rates(unittest.TestCase):
    def test_window_uses_only_previous_years(self):
        rows = [{"year": y, "outcome": o} for y, o in
                [(2000, 1), (2000, 0), (2001, 0), (2001, 0), (2002, 1), (2002, 1)]]
        r = t.recent_rates(rows, k=1)
        self.assertIsNone(r[2000])
        self.assertAlmostEqual(r[2001], (1 + 0.5) / (2 + 1))
        self.assertAlmostEqual(r[2002], (0 + 0.5) / (2 + 1))
        r2 = t.recent_rates(rows, k=10)
        self.assertAlmostEqual(r2[2002], (1 + 0.5) / (4 + 1))


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_panel()

    def test_same_rows_and_models(self):
        res = t.run(self.rows, test_start=1990)
        self.assertEqual(set(res["predictions"]),
                         {"B0", "MH", "MT", "MX", "MX_c", "MT_c", "MH_c", "MX_tend"})
        for ps in res["predictions"].values():
            self.assertEqual(len(ps), len(res["test"]))
            self.assertTrue(all(0.0 < p < 1.0 for p in ps))

    def test_deterministic(self):
        a = t.summarize(t.run(self.rows, test_start=1990), reps=50)
        b = t.summarize(t.run(list(reversed(self.rows)), test_start=1990), reps=50)
        self.assertEqual(a, b)

    def test_no_leak_from_current_or_future_labels(self):
        base = t.run(self.rows, test_start=1990)
        flipped = [dict(r, outcome=1 - r["outcome"]) if r["year"] >= 1994 else dict(r)
                   for r in self.rows]
        other = t.run(flipped, test_start=1990)
        upto = [i for i, r in enumerate(base["test"]) if r["year"] <= 1994]
        after = [i for i, r in enumerate(base["test"]) if r["year"] > 1994]
        for name in base["predictions"]:
            self.assertEqual([base["predictions"][name][i] for i in upto],
                             [other["predictions"][name][i] for i in upto], name)
        # la correccion SI debe reaccionar a etiquetas pasadas en anios posteriores
        self.assertNotEqual([base["predictions"]["MX_c"][i] for i in after],
                            [other["predictions"]["MX_c"][i] for i in after])

    def test_slopes_are_those_of_exp003(self):
        import exp003_model as m
        base = m.run_models(self.rows, test_start=1990, exploratory=False)
        res = t.run(self.rows, test_start=1990)
        self.assertEqual(res["predictions"]["MX"], base["predictions"]["MX"])


if __name__ == "__main__":
    unittest.main()
