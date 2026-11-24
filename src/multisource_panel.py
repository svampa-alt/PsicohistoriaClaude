"""EXP-002-J: reproducir un panel multifuente con datos públicos y sin dependencias externas.

Fuentes: World Bank (población, PIB corriente) vía DataHub; CDIAC carbono fósil.
No usa resultados futuros para calcular variables rezagadas.
NO es una validación de pronóstico histórico.
"""
import argparse
import csv
import io
import urllib.request
from pathlib import Path

SOURCES = {
    "population": "https://raw.githubusercontent.com/datasets/population/d4b1a4a9a17e2123baf0ef119de05bceced1ab1b/data/population.csv",
    "gdp": "https://raw.githubusercontent.com/datasets/gdp/36d761dc5617982d3e50b213e02b9a1b47c4e958/data/gdp.csv",
    "carbon": "https://raw.githubusercontent.com/datasets/co2-fossil-by-nation/a0d67befcba0666850085281dae48a4e81dcd979/data/fossil-fuel-co2-emissions-by-nation.csv",
}
COUNTRIES = {"UNITED STATES OF AMERICA": "USA", "UNITED KINGDOM": "GBR", "JAPAN": "JPN"}
FIELDS = ["country_iso3", "year", "population", "gdp_current_usd",
          "carbon_thousand_metric_tons", "gdp_per_capita_usd", "pop_growth_pct",
          "gdp_growth_nominal_pct", "carbon_tons_per_capita", "gdp_pc_x_carbon_pc"]

def load(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return list(csv.DictReader(io.StringIO(response.read().decode("utf-8-sig"))))

def make_panel(pop, gdp, carbon, start=1980, end=1990):
    def wb(rows):
        return {(r["Country Code"], int(r["Year"])): float(r["Value"])
                for r in rows if r.get("Value")}
    p, g = wb(pop), wb(gdp)
    c = {(COUNTRIES[r["Country"]], int(r["Year"])): float(r["Total"])
         for r in carbon if r["Country"] in COUNTRIES and r.get("Total")}
    output = []
    for code in sorted(COUNTRIES.values()):
        for year in range(start, end + 1):
            key, prior = (code, year), (code, year - 1)
            if any(k not in table for table, k in
                   [(p, key), (g, key), (c, key), (p, prior), (g, prior)]):
                continue
            pop_now, gdp_now, carb = p[key], g[key], c[key]
            if min(pop_now, gdp_now, p[prior], g[prior]) <= 0:
                continue
            pc = gdp_now / pop_now
            carbon_pc = 1000 * carb / pop_now
            output.append(dict(zip(FIELDS, [
                code, year, pop_now, gdp_now, carb, pc,
                100 * (pop_now / p[prior] - 1),
                100 * (gdp_now / g[prior] - 1),
                carbon_pc, pc * carbon_pc,
            ])))
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/EXP-002-J-three-source-panel-1980-1990.csv"))
    args = parser.parse_args()
    rows = make_panel(*(load(SOURCES[name]) for name in ("population", "gdp", "carbon")))
    if len(rows) != 33:
        raise ValueError(f"Cobertura inesperada: {len(rows)} filas; no sobrescribir")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Filas: {len(rows)}; países: 3; años: 1980-1990")

if __name__ == "__main__":
    main()
