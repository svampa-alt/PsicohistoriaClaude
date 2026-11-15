"""Pruebas sinteticas del constructor de panel de EXP-005 (sin archivos reales)."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import exp005_build_panel as b  # noqa: E402


def toy():
    polity = {}
    for y in range(1955, 2019):
        polity[(100, y)] = ("Alfa", 5.0 if y < 1990 else -2.0, 7 if y % 2 else 2)
        polity[(200, y)] = ("Beta", -8.0, 1)
    gdp = {(c, y): 1000.0 * (1.02 ** (y - 1950)) for c in (100, 200) for y in range(1950, 2019)}
    gdp[(200, 1999)] = None
    del gdp[(200, 1999)]
    coups = {(100, 1965), (100, 1970), (200, 2005), (100, 2019)}
    return polity, gdp, coups


class Helpers(unittest.TestCase):
    def test_factional_codes(self):
        for code in (6, 7, 8, 6.0):
            self.assertEqual(b.factional(code), 1.0)
        for code in (1, 2, 9, 10, -66, -88, None, float("nan"), "x"):
            self.assertEqual(b.factional(code), 0.0)

    def test_growth(self):
        gdp = {(1, 2000): 100.0, (1, 2001): 110.0}
        self.assertAlmostEqual(b.growth(gdp, 1, 2001), 0.10)
        self.assertIsNone(b.growth(gdp, 1, 2002))
        self.assertIsNone(b.growth({(1, 2000): 0.0, (1, 2001): 5.0}, 1, 2001))

    def test_coup_code_prefers_polity_code(self):
        self.assertEqual(b.coup_code({"ccode": "365", "ccode_polity": "364"}), 364)
        self.assertEqual(b.coup_code({"ccode": "160", "ccode_polity": ""}), 160)

    def test_overrides_do_not_map_excluded_codes(self):
        self.assertFalse(set(b.POLITY_TO_ISO_OVERRIDES) & set(b.NOT_MAPPED_REASON))


class Build(unittest.TestCase):
    def setUp(self):
        self.rows, self.dropped = b.build_rows(*toy())
        self.by = {(r["ccode"], r["year"]): r for r in self.rows}

    def test_years_and_last_year_from_previous_membership(self):
        years = {r["year"] for r in self.rows}
        self.assertEqual(min(years), 1960)
        self.assertEqual(max(years), 2019)
        self.assertEqual(self.by[(100, 2019)]["outcome"], 1)

    def test_everything_is_lagged(self):
        r = self.by[(100, 1990)]
        self.assertEqual(r["polity2_lag"], 5.0)          # 1989, no 1990
        self.assertEqual(r["factional_lag"], 1)          # polcomp 1989 = 7
        self.assertAlmostEqual(r["growth_lag"], 0.02)
        self.assertAlmostEqual(r["loggdp_lag"], math.log(1000.0 * 1.02 ** 39))

    def test_missing_gdp_drops_row_and_neighbours(self):
        self.assertNotIn((200, 2000), self.by)           # falta PIB 1999
        self.assertNotIn((200, 2001), self.by)           # crecimiento 2000 necesita 1999
        self.assertIn((200, 2002), self.by)
        self.assertEqual(self.dropped["sin_pib_t-1"], 2)

    def test_outcome_and_history(self):
        self.assertEqual(self.by[(100, 1965)]["outcome"], 1)
        self.assertEqual(self.by[(100, 1966)]["coups_prev10"], 1)
        self.assertEqual(self.by[(100, 1971)]["coups_prev10"], 2)
        self.assertEqual(self.by[(100, 1976)]["coups_prev10"], 1)
        self.assertEqual(self.by[(200, 2005)]["coups_prev10"], 0)

    def test_future_coups_do_not_leak_into_features(self):
        polity, gdp, coups = toy()
        base, _ = b.build_rows(polity, gdp, coups)
        more, _ = b.build_rows(polity, gdp, coups | {(200, 2010), (200, 2011)})
        for x, y in zip(base, more):
            if x["year"] <= 2010:
                for col in ("E", "P", "I", "T", "coups_prev10", "loggdp_lag"):
                    self.assertEqual(x[col], y[col])

    def test_index_bounds(self):
        for r in self.rows:
            for col in ("E", "P", "I", "T"):
                self.assertTrue(0.0 <= r[col] <= 1.0)


if __name__ == "__main__":
    unittest.main()
