"""EXP-005: panel pais-anio con fuentes originales actualizadas.

Fuentes (ver research/EXP-005-preregistro.md):
- Powell & Thyne V2026.08.29: data/fuentes/powell_thyne_V2026.08.29.csv (en el repo).
- Maddison Project Database 2023: _fuentes/maddison2023/mpd2023_web.xlsx
  (https://dataverse.nl/api/access/datafile/421302, doi:10.34894/INZBF2).
- Polity5 p5v2018: _fuentes/polity5/p5v2018.xls
  (https://www.systemicpeace.org/inscr/p5v2018.xls).

La logica de union (build_rows y auxiliares) usa solo la biblioteca estandar y
tiene pruebas sinteticas; la lectura de Excel requiere pandas, openpyxl, xlrd y
countrycode (requirements-data.txt).
"""
import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_model import tension_e, tension_i, tension_t  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
YEAR_MIN, YEAR_MAX = 1960, 2019
FACTIONAL_CODES = {6, 7, 8}  # Factional/Restricted, Factional, Electoral Transition: Persistent Conflict
# Codigos Polity cuyo ISO3 no sale de countrycode (iso3c -> cown) o difiere.
# Solo se mapean territorios equivalentes; los no mapeados se listan en el manifiesto.
POLITY_TO_ISO_OVERRIDES = {
    315: "CSK",  # Checoslovaquia (hasta 1992)
    345: "YUG",  # Yugoslavia socialista (hasta 1991)
    342: "SRB",  # Serbia (desde 2006)
    348: "MNE",  # Montenegro (desde 2006)
    364: "SUN",  # URSS (hasta 1991)
    529: "ETH",  # Etiopia (codigo Polity desde 1993)
    626: "SDN",  # Sudan del Norte (codigo Polity desde 2011)
    818: "VNM",  # Vietnam unificado (desde 1976)
}
NOT_MAPPED_REASON = {
    260: "Alemania Occidental: Maddison DEU no corresponde al mismo territorio",
    265: "Alemania Oriental: sin serie propia",
    347: "Yugoslavia/Serbia y Montenegro 1991-2006: Maddison YUG es el agregado de toda la ex Yugoslavia",
    678: "Yemen del Norte: Maddison YEM es el pais unificado",
    680: "Yemen del Sur: sin serie propia",
    769: "Pakistan con Bangladesh (hasta 1971): Maddison PAK es el territorio actual",
    817: "Vietnam del Sur: sin serie propia",
}
COLUMNS = ["country", "ccode", "year", "outcome", "growth_lag", "loggdp_lag", "polity2_lag",
           "factional_lag", "coups_prev10", "E", "P", "I", "T", "gdp_lag_duplicado"]


def factional(polcomp):
    try:
        return 1.0 if int(polcomp) in FACTIONAL_CODES else 0.0
    except (TypeError, ValueError):
        return 0.0


def growth(gdp, code, year):
    """Crecimiento del PIBpc de year-1 a year; None si falta alguno."""
    a, b = gdp.get((code, year - 1)), gdp.get((code, year))
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return b / a - 1.0


def coup_code(row):
    """Codigo Polity de un registro de Powell & Thyne."""
    cp = (row.get("ccode_polity") or "").strip()
    return int(cp) if cp else int(row["ccode"])


def universe_keys(polity):
    """Pais-anios del universo: filas de Polity5 entre YEAR_MIN y YEAR_MAX. Para el
    ultimo anio (2019, que Polity5 no cubre) un pais pertenece si existe en t-1."""
    keys = {(k, v[0]) for k, v in polity.items() if YEAR_MIN <= k[1] <= YEAR_MAX}
    have_last = {k[0] for k in polity if k[1] == YEAR_MAX}
    for (code, year), v in polity.items():
        if year == YEAR_MAX - 1 and code not in have_last:
            keys.add(((code, YEAR_MAX), v[0]))
    return sorted(keys, key=lambda kv: (kv[0][1], kv[0][0]))


def build_rows(polity, gdp, coup_years):
    """polity: {(code, year): (country, polity2, polcomp)}
    gdp: {(code, year): PIBpc} ya traducido a codigo Polity
    coup_years: set de (code, year) con >=1 intento.
    Todas las explicativas de la fila t son de t-1 o antes."""
    dropped = Counter()
    rows = []
    for (code, year), country in universe_keys(polity):
        lag = polity.get((code, year - 1))
        p2 = None if lag is None else lag[1]
        g = growth(gdp, code, year - 1)
        level = gdp.get((code, year - 1))
        no_gdp, no_pol = g is None or level is None, p2 is None or (isinstance(p2, float) and math.isnan(p2))
        if no_gdp or no_pol:
            dropped["sin_pib_y_sin_polity2" if no_gdp and no_pol
                    else "sin_pib_t-1" if no_gdp else "sin_polity2_t-1"] += 1
            if (code, year) in coup_years:
                dropped["eventos_en_filas_descartadas"] += 1
            continue
        e, p, i = tension_e(g), factional(lag[2]), tension_i(p2)
        rows.append({"country": country, "ccode": code, "year": year,
                     "outcome": int((code, year) in coup_years),
                     "growth_lag": g, "loggdp_lag": math.log(level), "polity2_lag": p2,
                     "factional_lag": int(p),
                     "coups_prev10": sum((code, y) in coup_years for y in range(year - 10, year)),
                     "E": e, "P": p, "I": i, "T": tension_t(e, p, i), "gdp_lag_duplicado": 0})
    return rows, dropped


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmt(v):
    if isinstance(v, float):
        return format(v, ".10g")
    return str(v)


def load(sources):
    import countrycode as cc  # dependencias solo de este paso
    import pandas as pd

    pol = pd.read_excel(sources["polity5"])
    polity = {}
    for code, year, country, p2, comp in zip(pol.ccode, pol.year, pol.country, pol.polity2, pol.polcomp):
        key = (int(code), int(year))
        if key in polity:
            raise ValueError(f"Polity5 duplicado: {key}")
        polity[key] = (str(country).strip(), float(p2), comp)

    mad = pd.read_excel(sources["maddison2023"], sheet_name="Full data")
    mad = mad[mad.gdppc.notna() & (mad.year >= YEAR_MIN - 3)]
    codes = sorted({c for c, _ in polity})
    iso_of = {}
    auto = cc.countrycode(codes, origin="cown", destination="iso3c")
    for code, iso in zip(codes, auto):
        if iso:
            iso_of[code] = iso
    iso_of.update(POLITY_TO_ISO_OVERRIDES)
    for code in NOT_MAPPED_REASON:
        iso_of.pop(code, None)
    by_iso = defaultdict(list)
    for code, iso in iso_of.items():
        by_iso[iso].append(code)
    gdp = {}
    for iso, year, value in zip(mad.countrycode, mad.year, mad.gdppc):
        for code in by_iso.get(iso, ()):
            gdp[(code, int(year))] = float(value)
    have_iso = set(mad.countrycode)
    unmatched = sorted({(c, polity[(c, y)][0]) for (c, y) in polity
                        if YEAR_MIN - 1 <= y <= YEAR_MAX - 1 and iso_of.get(c) not in have_iso})

    with open(sources["powell_thyne"], encoding="utf-8-sig", newline="") as f:
        pt = list(csv.DictReader(f))
    coup_years = {(coup_code(r), int(r["year"])) for r in pt}
    return polity, gdp, coup_years, pt, iso_of, unmatched


def main():
    parser = argparse.ArgumentParser(description="EXP-005: construir panel actualizado")
    parser.add_argument("--powell-thyne", type=Path, default=ROOT / "data" / "fuentes" / "powell_thyne_V2026.08.29.csv")
    parser.add_argument("--maddison", type=Path, default=ROOT / "_fuentes" / "maddison2023" / "mpd2023_web.xlsx")
    parser.add_argument("--polity", type=Path, default=ROOT / "_fuentes" / "polity5" / "p5v2018.xls")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp005_panel.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "exp005_manifest.json")
    args = parser.parse_args()
    sources = {"powell_thyne": args.powell_thyne, "maddison2023": args.maddison, "polity5": args.polity}
    polity, gdp, coup_years, pt, iso_of, unmatched = load(sources)
    rows, dropped = build_rows(polity, gdp, coup_years)

    universe = {k for k, _ in universe_keys(polity)}
    pt_in_window = {(coup_code(r), int(r["year"])) for r in pt if YEAR_MIN <= int(r["year"]) <= YEAR_MAX}
    outside = sorted(k for k in pt_in_window if k not in universe)

    args.panel.parent.mkdir(parents=True, exist_ok=True)
    with open(args.panel, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([fmt(r[c]) for c in COLUMNS])
    by_period = {}
    for name, lo, hi in (("1960-1989", 1960, 1989), ("1990-2011", 1990, 2011), ("2012-2019", 2012, 2019)):
        sel = [r for r in rows if lo <= r["year"] <= hi]
        by_period[name] = {"filas": len(sel), "eventos": sum(r["outcome"] for r in sel)}
    manifest = {
        "experimento": "EXP-005",
        "preregistro": "research/EXP-005-preregistro.md",
        "sha256_fuentes": {
            "data/fuentes/powell_thyne_V2026.08.29.csv": sha256(args.powell_thyne),
            "maddison2023/mpd2023_web.xlsx": sha256(args.maddison),
            "polity5/p5v2018.xls": sha256(args.polity)},
        "url_fuentes": {
            "powell_thyne": "https://www.uky.edu/~clthyn2/coup_data/home.htm (aportado por el usuario)",
            "maddison2023": "https://dataverse.nl/api/access/datafile/421302 (doi:10.34894/INZBF2)",
            "polity5": "https://www.systemicpeace.org/inscr/p5v2018.xls"},
        "sha256_panel": sha256(args.panel),
        "universo": f"Polity5, {YEAR_MIN}-{YEAR_MAX} (2019: paises presentes en Polity5 en 2018)",
        "universo_filas": len(universe),
        "filas_panel": len(rows),
        "eventos_panel": sum(r["outcome"] for r in rows),
        "paises": len({r["ccode"] for r in rows}),
        "por_periodo": by_period,
        "filas_descartadas": dict(sorted(dropped.items())),
        "intentos_pt_fuera_del_universo_polity": [list(k) for k in outside],
        "codigos_polity_sin_pib": [{"ccode": c, "pais": n, "motivo": NOT_MAPPED_REASON.get(c, "sin serie en Maddison 2023")}
                                   for c, n in unmatched],
        "equivalencias_manuales": {str(k): v for k, v in POLITY_TO_ISO_OVERRIDES.items()},
        "factional_polcomp": sorted(FACTIONAL_CODES),
        "columnas": COLUMNS,
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("filas_panel", "eventos_panel", "paises", "por_periodo",
                                                "filas_descartadas")}, ensure_ascii=False, indent=1))
    print("P&T fuera del universo:", len(outside), "| codigos sin PIB:", len(unmatched))


if __name__ == "__main__":
    main()
