"""Pruebas sinteticas del constructor de EXP-006 (sin archivos reales)."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import exp006_build_panel as b  # noqa: E402


class Transforms(unittest.TestCase):
    def test_i_v(self):
        self.assertEqual(b.tension_i_v(0.5), 1.0)
        self.assertEqual(b.tension_i_v(0.0), 0.0)
        self.assertEqual(b.tension_i_v(1.0), 0.0)
        self.assertAlmostEqual(b.tension_i_v(0.25), 0.5)

    def test_p_v(self):
        self.assertEqual(b.tension_p_v(-5, -2, 2), 0.0)
        self.assertEqual(b.tension_p_v(5, -2, 2), 1.0)
        self.assertAlmostEqual(b.tension_p_v(0, -2, 2), 0.5)

    def test_quantile(self):
        self.assertEqual(b.quantile([1, 2, 3, 4, 5], 0.5), 3)
        self.assertAlmostEqual(b.quantile([0, 10], 0.05), 0.5)

    def test_cow_mapping(self):
        self.assertEqual(b.cow_of(364), 365)
        self.assertEqual(b.cow_of(626), 625)   # Sudan del Norte -> Sudan
        self.assertEqual(b.cow_of(525), 626)   # Sudan del Sur -> 626 en V-Dem
        self.assertEqual(b.cow_of(160), 160)


class Universe(unittest.TestCase):
    def test_extends_2018_membership(self):
        polity = {(1, y): ("A", 0.0, 1) for y in range(1958, 2019)}
        polity.update({(2, y): ("B", 0.0, 1) for y in range(1958, 2000)})
        keys = {k for k, _ in b.universe(polity)}
        self.assertIn((1, 2025), keys)
        self.assertNotIn((2, 2020), keys)
        self.assertNotIn((1, 1959), keys)


class Gdp(unittest.TestCase):
    def test_chain_world_bank_growth(self):
        gdp = {(1, 2021): 90.0, (1, 2022): 100.0}
        wb = {("AAA", 2022): 50.0, ("AAA", 2023): 55.0, ("AAA", 2024): 60.5}
        out, added = b.extend_gdp(gdp, wb, {1: "AAA"})
        self.assertAlmostEqual(out[(1, 2023)], 110.0)
        self.assertAlmostEqual(out[(1, 2024)], 121.0)
        self.assertEqual(added, {(1, 2023), (1, 2024)})

    def test_no_chain_without_base(self):
        out, added = b.extend_gdp({}, {("AAA", 2022): 1.0, ("AAA", 2023): 2.0}, {1: "AAA"})
        self.assertEqual(added, set())


class Build(unittest.TestCase):
    def setUp(self):
        polity = {(1, y): ("A", 0.0, 1) for y in range(1955, 2019)}
        self.units = b.universe(polity)
        self.gdp = {(1, y): 100.0 * 1.01 ** (y - 1950) for y in range(1950, 2025)}
        self.vdem = {(1, y): (float(y % 5) - 2.0, 0.3) for y in range(1950, 2026)}
        self.vdem[(1, 2000)] = (None, 0.3)
        self.coups = {(1, 1970), (1, 2021)}
        self.rows, self.dropped = b.build_rows(self.units, self.gdp, {(1, 2023), (1, 2024)}, self.vdem, self.coups)
        b.finish(self.rows)
        self.by = {r["year"]: r for r in self.rows}

    def test_lags_and_drops(self):
        self.assertNotIn(2001, self.by)                 # V-Dem 2000 incompleto
        self.assertEqual(self.dropped["sin_vdem_t-1"], 1)
        self.assertAlmostEqual(self.by[1990]["polyarchy_lag"], 0.3)
        self.assertEqual(self.by[1990]["cacamps_lag"], float(1989 % 5) - 2.0)

    def test_sources_and_outcome(self):
        self.assertEqual(self.by[2025]["gdp_fuente"], "banco_mundial")
        self.assertEqual(self.by[2023]["gdp_fuente"], "maddison2023")
        self.assertEqual(self.by[2021]["outcome"], 1)
        self.assertEqual(self.by[2022]["coups_prev10"], 1)

    def test_bounds(self):
        for r in self.rows:
            for c in ("E", "P", "I", "T"):
                self.assertTrue(0.0 <= r[c] <= 1.0)
            self.assertTrue(math.isfinite(r["loggdp_lag"]))


if __name__ == "__main__":
    unittest.main()
