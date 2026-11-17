"""EXP-006: panel 1960-2025 con V-Dem v16 en lugar de Polity (issue #5).

Preregistro: research/EXP-006-preregistro.md. Reutiliza la carga de EXP-005
(Polity5 para el universo, Maddison 2023, Powell & Thyne) y agrega:
- V-Dem v16 (_fuentes/vdem16/vdem.RData, paquete oficial vdemdata);
- Banco Mundial NY.GDP.PCAP.KD 2020-2024 (_fuentes/worldbank/...json) para
  extender el PIB a 2023 y 2024.
La logica de construccion (funciones puras) usa solo la biblioteca estandar.
"""
import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp005_build_panel as p5  # noqa: E402
from exp003_model import clip, tension_e, tension_t  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
YEAR_MIN, YEAR_MAX = 1960, 2025
POLITY_LAST = 2018
TRAIN_END = 1989
# Codigo Polity -> codigo COW usado por V-Dem, cuando difieren.
POLITY_TO_COW = {364: 365, 529: 530, 626: 625, 525: 626, 769: 770, 818: 816,
                 342: 345, 347: 345, 348: 341}
COLUMNS = ["country", "ccode", "cow", "year", "outcome", "growth_lag", "loggdp_lag", "gdp_fuente",
           "cacamps_lag", "polyarchy_lag", "coups_prev10", "E", "P", "I", "T", "gdp_lag_duplicado"]


def cow_of(polity_code):
    return POLITY_TO_COW.get(polity_code, polity_code)


def tension_i_v(polyarchy):
    """Fragilidad institucional con V-Dem: 1 en regimenes intermedios, 0 en los extremos."""
    return clip(1.0 - abs(2.0 * polyarchy - 1.0))


def tension_p_v(cacamps, q05, q95):
    """Polarizacion continua reescalada con cuantiles del entrenamiento."""
    return clip((cacamps - q05) / (q95 - q05))


def quantile(values, q):
    xs = sorted(values)
    pos = q * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def universe(polity):
    """Paises-anio de Polity5 1960-2018; 2019-2025 con los paises presentes en 2018."""
    keys = {(k, v[0]) for k, v in polity.items() if YEAR_MIN <= k[1] <= POLITY_LAST}
    last = {(c, v[0]) for (c, y), v in polity.items() if y == POLITY_LAST}
    for year in range(POLITY_LAST + 1, YEAR_MAX + 1):
        keys |= {((c, year), name) for c, name in last}
    return sorted(keys, key=lambda kv: (kv[0][1], kv[0][0]))


def extend_gdp(gdp, wb_level, iso_of, years=(2023, 2024)):
    """Encadena Maddison (ultimo anio 2022) con el crecimiento del Banco Mundial.
    gdp: {(polity_code, year): nivel}; wb_level: {(iso, year): nivel}. Devuelve
    el diccionario ampliado y el conjunto de claves agregadas."""
    out, added = dict(gdp), set()
    for code, iso in iso_of.items():
        for year in years:
            prev = out.get((code, year - 1))
            a, b = wb_level.get((iso, year - 1)), wb_level.get((iso, year))
            if (code, year) in out or prev is None or not a or not b:
                continue
            out[(code, year)] = prev * b / a
            added.add((code, year))
    return out, added


def build_rows(units, gdp, gdp_added, vdem, coup_years):
    """units: lista de ((code, year), nombre); vdem: {(cow, year): (cacamps, polyarchy)}.
    Devuelve filas sin P/T (P necesita cuantiles del entrenamiento) y descartes."""
    rows, dropped = [], Counter()
    for (code, year), name in units:
        g = p5.growth(gdp, code, year - 1)
        level = gdp.get((code, year - 1))
        vd = vdem.get((cow_of(code), year - 1))
        reason = None
        if g is None or level is None:
            reason = "sin_pib_t-1"
        elif vd is None or any(x is None or math.isnan(x) for x in vd):
            reason = "sin_vdem_t-1"
        if reason:
            dropped[reason] += 1
            if (code, year) in coup_years:
                dropped["eventos_en_filas_descartadas"] += 1
            continue
        src = "banco_mundial" if {(code, year - 1), (code, year - 2)} & gdp_added else "maddison2023"
        e, i = tension_e(g), tension_i_v(vd[1])
        rows.append({"country": name, "ccode": code, "cow": cow_of(code), "year": year,
                     "outcome": int((code, year) in coup_years), "growth_lag": g,
                     "loggdp_lag": math.log(level), "gdp_fuente": src,
                     "cacamps_lag": vd[0], "polyarchy_lag": vd[1],
                     "coups_prev10": sum((code, y) in coup_years for y in range(year - 10, year)),
                     "E": e, "I": i, "gdp_lag_duplicado": 0})
    return rows, dropped


def finish(rows):
    """Calcula P y T con cuantiles de v2cacamps de las filas de entrenamiento."""
    train = [r["cacamps_lag"] for r in rows if r["year"] <= TRAIN_END]
    q05, q95 = quantile(train, 0.05), quantile(train, 0.95)
    for r in rows:
        r["P"] = tension_p_v(r["cacamps_lag"], q05, q95)
        r["T"] = tension_t(r["E"], r["P"], r["I"])
    return q05, q95


def main():
    parser = argparse.ArgumentParser(description="EXP-006: panel con V-Dem")
    parser.add_argument("--vdem", type=Path, default=ROOT / "_fuentes" / "vdem16" / "vdem.RData")
    parser.add_argument("--wb", type=Path, default=ROOT / "_fuentes" / "worldbank" / "NY.GDP.PCAP.KD_2020_2024.json")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp006_panel.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "exp006_manifest.json")
    args = parser.parse_args()
    import pyreadr  # dependencia de datos

    sources = {"powell_thyne": ROOT / "data" / "fuentes" / "powell_thyne_V2026.08.29.csv",
               "maddison2023": ROOT / "_fuentes" / "maddison2023" / "mpd2023_web.xlsx",
               "polity5": ROOT / "_fuentes" / "polity5" / "p5v2018.xls"}
    polity, gdp, coup_years, pt, iso_of, _ = p5.load(sources)
    wb_raw = json.loads(args.wb.read_text(encoding="utf-8"))[1]
    wb = {(x["countryiso3code"], int(x["date"])): float(x["value"]) for x in wb_raw if x["value"] is not None}
    gdp2, added = extend_gdp(gdp, wb, iso_of)
    v = pyreadr.read_r(str(args.vdem))["vdem"]
    v = v[(v.year >= YEAR_MIN - 2) & v.COWcode.notna()]
    vdem = {}
    for cow, year, cac, poly in zip(v.COWcode, v.year, v.v2cacamps, v.v2x_polyarchy):
        key = (int(cow), int(year))
        if key in vdem:
            raise ValueError(f"V-Dem duplicado: {key}")
        vdem[key] = (None if cac != cac else float(cac), None if poly != poly else float(poly))
    units = universe(polity)
    rows, dropped = build_rows(units, gdp2, added, vdem, coup_years)
    q05, q95 = finish(rows)
    with open(args.panel, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([p5.fmt(r[c]) for c in COLUMNS])
    periods = {}
    for name, lo, hi in (("1960-1989", 1960, 1989), ("1990-2011", 1990, 2011), ("2012-2019", 2012, 2019),
                         ("2020-2023", 2020, 2023), ("2024-2025", 2024, 2025)):
        sel = [r for r in rows if lo <= r["year"] <= hi]
        periods[name] = {"filas": len(sel), "eventos": sum(r["outcome"] for r in sel)}
    manifest = {
        "experimento": "EXP-006", "preregistro": "research/EXP-006-preregistro.md",
        "sha256_fuentes": {"vdem16/vdem.RData": p5.sha256(args.vdem),
                           "worldbank/NY.GDP.PCAP.KD_2020_2024.json": p5.sha256(args.wb),
                           **{k: p5.sha256(path) for k, path in sources.items()}},
        "url_fuentes": {"vdem16": "https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/data/vdem.RData (vdemdata 16.0, GPL-3)",
                        "worldbank": "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.KD?format=json&date=2020:2024&per_page=20000"},
        "sha256_panel": p5.sha256(args.panel),
        "universo": "Polity5 1960-2018; 2019-2025 con los paises presentes en Polity5 en 2018",
        "filas_universo": len(units), "filas_panel": len(rows),
        "eventos_panel": sum(r["outcome"] for r in rows), "paises": len({r["ccode"] for r in rows}),
        "por_periodo": periods, "filas_descartadas": dict(sorted(dropped.items())),
        "cuantiles_v2cacamps_entrenamiento": {"q05": q05, "q95": q95},
        "pib_extendido_con_banco_mundial": len(added),
        "polity_a_cow": {str(k): v for k, v in POLITY_TO_COW.items()},
        "columnas": COLUMNS,
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("filas_panel", "eventos_panel", "paises", "por_periodo",
                                                "filas_descartadas", "cuantiles_v2cacamps_entrenamiento",
                                                "pib_extendido_con_banco_mundial")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
