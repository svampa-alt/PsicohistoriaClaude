"""Pruebas sinteticas de la evaluacion de EXP-005."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp005_evaluate as ev  # noqa: E402
from test_exp003 import synthetic_panel  # noqa: E402


class Evaluate(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_panel(years=range(1970, 2020))

    def test_blocks_partition_years(self):
        _, blocks = ev.evaluate(self.rows, reps=30)
        c, s = blocks["confirmatorio_2012_2019"], blocks["secundario_1990_2011"]
        self.assertEqual(c["n"], 12 * 8)
        self.assertEqual(s["n"], 12 * 22)
        self.assertEqual(set(c["modelos"]), set(ev.MODELS))
        self.assertEqual(set(c["hipotesis"]), {"C1_MXc_mejor_que_B0", "C2_MXc_mejor_que_MH", "C3_MXc_mejor_que_MHc"})

    def test_restrict_keeps_alignment(self):
        full, _ = ev.evaluate(self.rows, reps=10)
        sub = ev.restrict(full, 2012, 2019)
        self.assertTrue(all(2012 <= r["year"] <= 2019 for r in sub["test"]))
        first = next(i for i, r in enumerate(full["test"]) if r["year"] == 2012)
        self.assertEqual(sub["predictions"]["MX_c"][0], full["predictions"]["MX_c"][first])

    def test_confirmatory_labels_do_not_change_their_own_forecasts(self):
        flipped = [dict(r, outcome=1 - r["outcome"]) if r["year"] >= 2012 else dict(r) for r in self.rows]
        a, _ = ev.evaluate(self.rows, reps=10)
        b, _ = ev.evaluate(flipped, reps=10)
        idx = [i for i, r in enumerate(a["test"]) if r["year"] == 2012]
        for name in ev.MODELS:
            self.assertEqual([a["predictions"][name][i] for i in idx], [b["predictions"][name][i] for i in idx])


if __name__ == "__main__":
    unittest.main()
