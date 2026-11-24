"""Pruebas sinteticas de la union de EXP-011."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import exp011_build_panel as b  # noqa: E402


class Union(unittest.TestCase):
    def test_lag_and_drop(self):
        rows = [{"cow": "1", "year": "1980"}, {"cow": "1", "year": "1981"}, {"cow": "1", "year": "1995"}]
        vdem = {(1, 1979): (0.2, -1.0), (1, 1980): (0.9, None), (1, 1994): (0.5, 2.0)}
        kept, dropped = b.add_vdem(rows, vdem)
        self.assertEqual([r["year"] for r in kept], ["1980", "1995"])
        self.assertEqual(kept[0]["mil_lag"], 0.2)
        self.assertEqual(len(dropped), 1)

    def test_rescale_uses_training_only(self):
        rows = [{"year": str(1960 + i), "mob_raw_lag": float(i)} for i in range(30)]
        rows += [{"year": "2000", "mob_raw_lag": 100.0}]
        q05, q95 = b.rescale_mobilization(rows)
        self.assertLess(q95, 30)
        self.assertEqual(rows[-1]["mob_lag"], 1.0)
        self.assertTrue(all(0.0 <= r["mob_lag"] <= 1.0 for r in rows))


if __name__ == "__main__":
    unittest.main()
