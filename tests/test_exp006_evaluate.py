"""Pruebas sinteticas de la evaluacion de EXP-006."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import exp006_evaluate as ev  # noqa: E402
from test_exp003 import synthetic_panel  # noqa: E402


class Evaluate(unittest.TestCase):
    def test_blocks_and_hypotheses(self):
        rows = synthetic_panel(years=range(1970, 2026))
        _, blocks = ev.evaluate(rows, reps=20)
        self.assertEqual(blocks["confirmatorio_2020_2025"]["n"], 12 * 6)
        self.assertEqual(blocks["secundario_A_2012_2019"]["n"], 12 * 8)
        self.assertEqual(blocks["secundario_B_2020_2023"]["n"], 12 * 4)
        self.assertEqual(set(blocks["confirmatorio_2020_2025"]["hipotesis"]), set(ev.RENAME.values()))
        years = blocks["confirmatorio_2020_2025"]["por_anio"]
        self.assertEqual(sorted(years), list(range(2020, 2026)))
        self.assertTrue(all(0 < d["p_MX_c"] < 1 for d in years.values()))


if __name__ == "__main__":
    unittest.main()
