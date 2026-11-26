"""Pruebas sinteticas del panel de EXP-012."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import exp012_build_panel as b  # noqa: E402


class Panel(unittest.TestCase):
    def test_family(self):
        self.assertTrue(b.is_family("Popular Protest, without Foreign Support"))
        self.assertTrue(b.is_family("Removed by Rebels, with Foreign Support"))
        self.assertFalse(b.is_family("Removed by Military, without Foreign Support"))
        self.assertFalse(b.is_family("Regular"))

    def test_gw_mapping(self):
        self.assertEqual(b.event_years([(340, 2000), (160, 1990)]), {(345, 2000), (160, 1990)})

    def test_build_outcome_history_and_cutoff(self):
        rows = [{"cow": "1", "year": str(y), "outcome": "0"} for y in range(1980, 2020)]
        out = b.build(rows, {(1, 1985), (1, 1990)})
        by = {int(r["year"]): r for r in out}
        self.assertEqual(max(by), 2014)
        self.assertEqual(by[1985]["outcome"], "1")
        self.assertEqual(by[1985]["rev_prev10"], "0")      # el evento del mismo anio no cuenta
        self.assertEqual(by[1991]["rev_prev10"], "2")
        self.assertEqual(by[1996]["rev_prev10"], "1")
        self.assertEqual(by[1985]["coup_outcome"], "0")


if __name__ == "__main__":
    unittest.main()
