"""Pruebas sinteticas de la evaluacion de EXP-012."""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp012_evaluate as ev  # noqa: E402
from test_exp003 import synthetic_panel  # noqa: E402


class Evaluate(unittest.TestCase):
    def test_rank(self):
        test = [{"year": 1}, {"year": 1}, {"year": 1}, {"year": 2}]
        self.assertEqual(ev.rank_in_year(test, [0.1, 0.5, 0.3, 0.9], 2), (2, 3))

    def test_pipeline(self):
        rng = random.Random(7)
        rows = synthetic_panel(years=range(1970, 2015))
        for r in rows:
            r["rev_prev10"], r["mil_lag"], r["mob_lag"] = float(rng.randint(0, 2)), rng.random(), rng.random()
        test, preds, models, episodes = ev.evaluate(rows, reps=20)
        self.assertEqual(set(models), {"B0", "MHr", "MHr_c", "MR", "MR_c"})
        self.assertEqual(len(episodes), sum(r["outcome"] for r in test))


if __name__ == "__main__":
    unittest.main()
