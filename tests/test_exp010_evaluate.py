"""Pruebas sinteticas de la evaluacion de EXP-010."""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp010_evaluate as ev  # noqa: E402
from test_exp003 import synthetic_panel  # noqa: E402


class Evaluate(unittest.TestCase):
    def test_structure_and_specs(self):
        self.assertEqual(set(ev.SPECS["MXd"]) - set(ev.SPECS["MXs"]), {"lpop_lag", "urb_lag"})
        rng = random.Random(3)
        rows = synthetic_panel(years=range(1970, 2026))
        for r in rows:
            r["lpop_lag"], r["urb_lag"] = rng.uniform(13, 20), rng.uniform(0.1, 0.9)
        out = ev.evaluate(rows, 1990, 2025, reps=20)
        self.assertEqual(out["n"], 12 * 36)
        self.assertEqual(set(out["modelos"]), {"B0", "MH", "MXs_c", "MXd_c", "MXs", "MXd"})
        self.assertEqual(len(out["ic95_dAUC"]), 2)


if __name__ == "__main__":
    unittest.main()
