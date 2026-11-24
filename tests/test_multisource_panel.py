"""Prueba de integración local con entradas mínimas; sin red."""
import unittest
from src.multisource_panel import make_panel

class MultiSourceTests(unittest.TestCase):
    def test_lag_and_interaction(self):
        pop = [{"Country Code": "USA", "Year": "1979", "Value": "100"},
               {"Country Code": "USA", "Year": "1980", "Value": "110"}]
        gdp = [{"Country Code": "USA", "Year": "1979", "Value": "1000"},
               {"Country Code": "USA", "Year": "1980", "Value": "1210"}]
        carbon = [{"Country": "UNITED STATES OF AMERICA", "Year": "1980", "Total": "22"}]
        rows = make_panel(pop, gdp, carbon, 1980, 1980)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertAlmostEqual(r["pop_growth_pct"], 10)
        self.assertAlmostEqual(r["gdp_growth_nominal_pct"], 21)
        self.assertAlmostEqual(r["gdp_per_capita_usd"], 11)
        self.assertAlmostEqual(r["carbon_tons_per_capita"], 200)
        self.assertAlmostEqual(r["gdp_pc_x_carbon_pc"], 2200)
    def test_missing_lag_does_not_impute(self):
        pop = [{"Country Code": "USA", "Year": "1980", "Value": "110"}]
        gdp = [{"Country Code": "USA", "Year": "1980", "Value": "1210"}]
        carbon = [{"Country": "UNITED STATES OF AMERICA", "Year": "1980", "Total": "22"}]
        self.assertEqual(make_panel(pop, gdp, carbon, 1980, 1980), [])

if __name__ == "__main__":
    unittest.main()
