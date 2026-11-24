"""EXP-002-K: une el panel J con Polity5 y añade la URSS sin confundirla con Rusia.

Usar copias locales de los archivos Polity5 (repositorio open-numbers/ddf--inscr--polity5).
El año de cada predictor político es t-1. No entrena modelos ni valida eventos.
"""
import argparse
import csv
import math
from pathlib import Path

MAP = {"USA": "usa", "GBR": "ukg", "JPN": "jpn", "USR": "usr"}
EXTRA = ["polity2_lag1", "regime_durability_lag1", "polity_x_logdur_lag1", "political_data_year"]

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def political_index(path, variable):
    return {(r["country"], int(r["year"])): float(r[variable])
            for r in read_csv(path) if r.get(variable) not in ("", None)}

def build(base, polity, durability, start=1980, end=1990):
    p = political_index(polity, "polity2")
    d = political_index(durability, "durable")
    def enrich(row):
        code, year = row["country_iso3"], int(row["year"])
        previous = year - 1
        pol, dur = p.get((MAP[code], previous)), d.get((MAP[code], previous))
        if pol is None or dur is None:
            raise ValueError(f"Falta Polity5 para {code} en {previous}")
        if dur < 0:
            raise ValueError(f"Durabilidad negativa para {code} en {previous}")
        row.update(dict(zip(EXTRA, [format(pol, "g"), format(dur, "g"),
                                   format(pol * math.log1p(dur), ".15g"), previous])))
        return row
    rows = [enrich(dict(row)) for row in read_csv(base)]
    fields = list(rows[0].keys())
    for year in range(start, end + 1):
        row = {key: "" for key in fields}
        row.update(country_iso3="USR", year=str(year))
        rows.append(enrich(row))
    return fields, rows

def main():
    a = argparse.ArgumentParser()
    a.add_argument("base", type=Path)
    a.add_argument("polity2", type=Path)
    a.add_argument("durable", type=Path)
    a.add_argument("--output", type=Path, default=Path("data/EXP-002-K-political-panel-1980-1990.csv"))
    x = a.parse_args()
    fields, rows = build(x.base, x.polity2, x.durable)
    x.output.parent.mkdir(parents=True, exist_ok=True)
    with x.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Filas: {len(rows)}; políticas completas: {sum(bool(r['polity2_lag1']) for r in rows)}")

if __name__ == "__main__":
    main()
