"""Pruebas sinteticas de la evaluacion de EXP-011."""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp011_evaluate as ev  # noqa: E402
from test_exp003 import synthetic_panel  # noqa: E402


class Evaluate(unittest.TestCase):
    def test_structure(self):
        self.assertEqual(set(ev.SPECS["MXm"]) - set(ev.SPECS["MXs"]), {"mil_lag", "mob_lag"})
        rng = random.Random(5)
        rows = synthetic_panel(years=range(1970, 2026))
        for r in rows:
            r["mil_lag"], r["mob_lag"] = rng.random(), rng.random()
        out = ev.evaluate(rows, 1990, 2025, reps=20)
        self.assertEqual(set(out["modelos"]), set(ev.REPORT))
        self.assertEqual(out["modelos"]["MX_mil_c"]["tipo"], "exploratorio")
        self.assertEqual(out["modelos"]["MXm_c"]["tipo"], "preespecificado")


if __name__ == "__main__":
    unittest.main()
