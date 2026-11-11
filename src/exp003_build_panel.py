"""EXP-003: construye el panel pais-anio (golpes, PIB, Polity, V-Dem).

Requiere pyreadr (ver requirements-data.txt) y la fuente clonada en
_fuentes/AuthoritarianismBook, fijada en el commit SOURCE_COMMIT:

    git clone https://github.com/xmarquez/AuthoritarianismBook.git _fuentes/AuthoritarianismBook
    git -C _fuentes/AuthoritarianismBook checkout 51716224a08674b956a6434b0d18cd761311efde
    python src/exp003_build_panel.py

Todas las variables explicativas de la fila (pais, t) se miden en t-1 o antes.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_model import tension_e, tension_i, tension_p, tension_t  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://github.com/xmarquez/AuthoritarianismBook.git"
SOURCE_COMMIT = "51716224a08674b956a6434b0d18cd761311efde"
YEAR_MIN, YEAR_MAX = 1960, 2014
MADDISON_PREFIX = "Maddison 2013"
# Maddison trae 2-3 filas para algunos pais-anio (series superpuestas de
# Estados sucesores). Regla fija y documentada: se conserva la ULTIMA fila en
# el orden original del archivo. Ver research/EXP-003-golpes-indice-T.md.
DUPLICATE_RULE = "last"
COLUMNS = ["country", "year", "outcome", "growth_lag", "loggdp_lag", "polity2_lag",
           "factional_lag", "polyarchy_lag", "execorr_lag", "coups_prev10",
           "E", "P", "I", "T", "gdp_lag_duplicado"]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fmt(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    if isinstance(value, float):
        return format(value, ".10g")
    return str(value)


def build(source_dir):
    import pyreadr  # dependencia solo de este paso

    data = source_dir / "data"
    files = {name: data / f"{name}.rda"
             for name in ("powell_thyne", "polity_annual", "economic_data", "vdem")}
    coups = pyreadr.read_r(str(files["powell_thyne"]))["powell_thyne"]
    polity = pyreadr.read_r(str(files["polity_annual"]))["polity_annual"]
    econ = pyreadr.read_r(str(files["economic_data"]), encoding="latin1")["economic_data"]
    vdem = pyreadr.read_r(str(files["vdem"]))["vdem"]

    attempts = Counter((c, int(y)) for c, y in zip(coups["country_name"], coups["year"]))

    maddison = econ[econ["variable"].astype(str).str.startswith(MADDISON_PREFIX)]
    gdp, gdp_count = {}, Counter()
    for c, y, level, growth in zip(maddison["country_name"], maddison["year"],
                                   maddison["per_capita"], maddison["per_capita_growth"]):
        key = (c, int(y))
        gdp_count[key] += 1
        gdp[key] = (float(level), float(growth))  # la ultima fila prevalece

    pol = {}
    for c, y, p2, comp in zip(polity["country_name"], polity["year"],
                              polity["polity2"], polity["polcomp"]):
        key = (c, int(y))
        if key in pol:
            raise ValueError(f"polity_annual duplicado: {key}")
        pol[key] = (float(p2), None if comp != comp or comp is None else str(comp))

    vd = {}
    for c, y, poly, corr in zip(vdem["country_name"], vdem["year"],
                                vdem["v2x_polyarchy"], vdem["v2x_execorr"]):
        key = (c, int(y))
        # Duplicados solo en Corea 1900-1910 (fuera del universo); se conserva la fila con datos.
        if key not in vd or not math.isnan(float(poly)):
            vd[key] = (float(poly), float(corr))

    universe = sorted((str(c), int(y)) for c, y, ok in
                      zip(polity["country_name"], polity["year"], polity["in_system"])
                      if ok and YEAR_MIN <= int(y) <= YEAR_MAX)
    dropped = defaultdict(int)
    rows = []
    for country, year in universe:
        lag = (country, year - 1)
        level, growth = gdp.get(lag, (math.nan, math.nan))
        p2, comp = pol.get(lag, (math.nan, None))
        no_gdp = math.isnan(level) or math.isnan(growth) or level <= 0
        no_pol = math.isnan(p2)
        if no_gdp or no_pol:
            dropped["sin_pib_y_sin_polity2" if no_gdp and no_pol
                    else "sin_pib_t-1" if no_gdp else "sin_polity2_t-1"] += 1
            if attempts.get((country, year)):
                dropped["eventos_en_filas_descartadas"] += 1
            continue
        poly, corr = vd.get(lag, (math.nan, math.nan))
        e, p, i = tension_e(growth), tension_p(comp), tension_i(p2)
        rows.append({
            "country": country, "year": year,
            "outcome": int(attempts.get((country, year), 0) > 0),
            "growth_lag": growth, "loggdp_lag": math.log(level), "polity2_lag": p2,
            "factional_lag": int(p), "polyarchy_lag": poly, "execorr_lag": corr,
            # anios con >=1 intento en t-10..t-1 (misma unidad que el outcome)
            "coups_prev10": sum(attempts.get((country, y), 0) > 0 for y in range(year - 10, year)),
            "E": e, "P": p, "I": i, "T": tension_t(e, p, i),
            "gdp_lag_duplicado": int(gdp_count[lag] > 1),
        })
    stats = {
        "universo_polity_in_system": len(universe),
        "filas_panel": len(rows),
        "eventos_panel": sum(r["outcome"] for r in rows),
        "paises": len({r["country"] for r in rows}),
        "filas_descartadas": dict(sorted(dropped.items())),
        "filas_descartadas_total": len(universe) - len(rows),
        "filas_con_pib_t-1_duplicado_en_fuente": sum(r["gdp_lag_duplicado"] for r in rows),
        "paises_con_pib_duplicado": sorted({r["country"] for r in rows if r["gdp_lag_duplicado"]}),
        "filas_sin_vdem_t-1": sum(math.isnan(r["polyarchy_lag"]) for r in rows),
    }
    return rows, stats, files


def main():
    parser = argparse.ArgumentParser(description="EXP-003: construir panel")
    parser.add_argument("--source", type=Path, default=ROOT / "_fuentes" / "AuthoritarianismBook")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp003_panel.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "exp003_manifest.json")
    args = parser.parse_args()

    head = subprocess.run(["git", "-C", str(args.source), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    if head != SOURCE_COMMIT:
        raise SystemExit(f"La fuente esta en {head}; se exige {SOURCE_COMMIT}")

    rows, stats, files = build(args.source)
    args.panel.parent.mkdir(parents=True, exist_ok=True)
    with open(args.panel, "w", encoding="utf-8", newline="") as handle:
        handle.write(",".join(COLUMNS) + "\n")
        for r in rows:
            cells = [fmt(r[c]) for c in COLUMNS]
            cells[0] = '"' + cells[0].replace('"', '""') + '"' if "," in cells[0] else cells[0]
            handle.write(",".join(cells) + "\n")
    manifest = {
        "experimento": "EXP-003",
        "fuente": {"url": SOURCE_URL, "commit": SOURCE_COMMIT, "licencia_paquete": "GPL-3",
                   "nota": "Los datos originales pertenecen a sus autores (Powell & Thyne, Polity IV, Maddison Project 2013, V-Dem)."},
        "sha256_fuentes": {f"data/{p.name}": sha256(p) for p in files.values()},
        "sha256_panel": sha256(args.panel),
        "panel": str(args.panel.relative_to(ROOT)) if args.panel.is_relative_to(ROOT) else args.panel.name,
        "universo": f"polity_annual in_system=True, {YEAR_MIN}-{YEAR_MAX}",
        "clave_de_union": ["country_name", "year"],
        "rezago": "todas las explicativas en t-1; coups_prev10 = anios con al menos un intento en t-10..t-1",
        "regla_duplicados_maddison": DUPLICATE_RULE,
        "columnas": COLUMNS,
        **stats,
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                             encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
