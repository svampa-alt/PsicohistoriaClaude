"""Prueba de unión y rezago Polity5 con archivos sintéticos, sin acceso a internet."""
import csv
import tempfile
import unittest
from pathlib import Path
from src.polity_panel import build

def write(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)

class PolityPanelTest(unittest.TestCase):
    def test_lag_and_ussr_separation(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            b,p,q=[d/x for x in ("base.csv","polity.csv","durable.csv")]
            write(b,["country_iso3","year","gdp_current_usd"],[["USA",1980,100]])
            write(p,["country","year","polity2"],[["usa",1979,10],["usr",1979,-7]])
            write(q,["country","year","durable"],[["usa",1979,5],["usr",1979,2]])
            fields, rows=build(b,p,q,1980,1980)
            self.assertEqual(len(rows),2)
            self.assertEqual(rows[0]["polity2_lag1"],"10")
            self.assertEqual(rows[1]["country_iso3"],"USR")
            self.assertEqual(rows[1]["gdp_current_usd"],"")
            self.assertEqual(rows[1]["polity2_lag1"],"-7")
            self.assertEqual(rows[1]["political_data_year"],1979)
    def test_missing_lag_is_not_imputed(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp); b,p,q=[d/x for x in ("b.csv","p.csv","q.csv")]
            write(b,["country_iso3","year"],[["USA",1980]])
            write(p,["country","year","polity2"],[["usa",1980,10]])
            write(q,["country","year","durable"],[["usa",1979,5]])
            with self.assertRaises(ValueError):
                build(b,p,q,1980,1980)

if __name__=="__main__":
    unittest.main()
