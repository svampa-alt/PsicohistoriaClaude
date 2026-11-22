"""EXP-010: agrega poblacion y urbanizacion (Banco Mundial) al panel V-Dem de EXP-006.

Preregistro: research/EXP-010-preregistro.md. Requiere countrycode (traduccion
de codigos); la union es pura y tiene pruebas sinteticas.
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp005_build_panel as p5  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INDICATORS = {"SP.POP.TOTL": "pop", "SP.URB.TOTL.IN.ZS": "urb"}


def load_wb(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))[1]
    return {(r["countryiso3code"], int(r["date"])): float(r["value"]) for r in rows if r["value"] is not None}


def polity_iso(codes):
    import countrycode as cc
    auto = cc.countrycode(sorted(codes), origin="cown", destination="iso3c")
    iso = {c: i for c, i in zip(sorted(codes), auto) if i}
    iso.update(p5.POLITY_TO_ISO_OVERRIDES)
    for code in p5.NOT_MAPPED_REASON:
        iso.pop(code, None)
    return iso


def add_demography(rows, iso_of, pop, urb):
    """Agrega lpop_lag y urb_lag (anio t-1). Devuelve (filas completas, descartadas)."""
    kept, dropped = [], []
    for r in rows:
        code, year = int(r["ccode"]), int(r["year"])
        iso = iso_of.get(code)
        p, u = pop.get((iso, year - 1)), urb.get((iso, year - 1))
        if iso is None or p is None or u is None or p <= 0:
            dropped.append(r)
            continue
        kept.append({**r, "lpop_lag": math.log(p), "urb_lag": u / 100.0})
    return kept, dropped


def main():
    parser = argparse.ArgumentParser(description="EXP-010: panel con demografia")
    parser.add_argument("--base", type=Path, default=ROOT / "data" / "exp006_panel.csv")
    parser.add_argument("--wb-dir", type=Path, default=ROOT / "_fuentes" / "worldbank")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp010_panel.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "exp010_manifest.json")
    args = parser.parse_args()
    with open(args.base, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)
    pop = load_wb(args.wb_dir / "SP.POP.TOTL.json")
    urb = load_wb(args.wb_dir / "SP.URB.TOTL.IN.ZS.json")
    iso_of = polity_iso({int(r["ccode"]) for r in rows})
    kept, dropped = add_demography(rows, iso_of, pop, urb)
    cols = columns + ["lpop_lag", "urb_lag"]
    with open(args.panel, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for r in kept:
            w.writerow([p5.fmt(r[c]) if isinstance(r[c], float) else r[c] for c in cols])
    by = lambda rs, lo, hi: {"filas": sum(lo <= int(r["year"]) <= hi for r in rs),  # noqa: E731
                             "eventos": sum(int(r["outcome"]) for r in rs if lo <= int(r["year"]) <= hi)}
    dropped_countries = sorted({r["country"] for r in dropped})
    manifest = {
        "experimento": "EXP-010", "preregistro": "research/EXP-010-preregistro.md",
        "base": "data/exp006_panel.csv", "sha256_base": p5.sha256(args.base),
        "sha256_fuentes": {f"worldbank/{k}.json": p5.sha256(args.wb_dir / f"{k}.json") for k in INDICATORS},
        "url_fuentes": {k: f"https://api.worldbank.org/v2/country/all/indicator/{k}?format=json&date=1958:2024&per_page=20000"
                        for k in INDICATORS},
        "sha256_panel": p5.sha256(args.panel),
        "filas_panel": len(kept), "eventos_panel": sum(int(r["outcome"]) for r in kept),
        "filas_descartadas_sin_demografia": len(dropped),
        "eventos_descartados": sum(int(r["outcome"]) for r in dropped),
        "paises_con_filas_descartadas": dropped_countries,
        "por_periodo": {"1960-1989": by(kept, 1960, 1989), "1990-2019": by(kept, 1990, 2019),
                        "2020-2025": by(kept, 2020, 2025)},
        "columnas_nuevas": {"lpop_lag": "log poblacion total en t-1", "urb_lag": "poblacion urbana (%)/100 en t-1"},
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k not in ("sha256_fuentes", "url_fuentes", "columnas_nuevas")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
