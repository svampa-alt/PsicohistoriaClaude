"""Pruebas sinteticas de la union demografica de EXP-010."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import exp010_build_panel as b  # noqa: E402


class Demography(unittest.TestCase):
    def test_uses_previous_year_and_drops_missing(self):
        rows = [{"ccode": "1", "year": "2001"}, {"ccode": "1", "year": "2002"}, {"ccode": "2", "year": "2001"}]
        pop = {("AAA", 2000): 1000.0, ("AAA", 2001): 2000.0}
        urb = {("AAA", 2000): 50.0}
        kept, dropped = b.add_demography(rows, {1: "AAA"}, pop, urb)
        self.assertEqual(len(kept), 1)
        self.assertAlmostEqual(kept[0]["lpop_lag"], math.log(1000.0))
        self.assertAlmostEqual(kept[0]["urb_lag"], 0.5)
        self.assertEqual(len(dropped), 2)   # 2002 sin urbanizacion 2001; codigo 2 sin ISO

    def test_nonpositive_population_dropped(self):
        kept, dropped = b.add_demography([{"ccode": "1", "year": "2001"}], {1: "AAA"},
                                         {("AAA", 2000): 0.0}, {("AAA", 2000): 10.0})
        self.assertEqual((len(kept), len(dropped)), (0, 1))


if __name__ == "__main__":
    unittest.main()
