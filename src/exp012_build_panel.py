"""EXP-012: panel de caidas de gobernantes por protesta popular o rebelion (Archigos).

Preregistro: research/EXP-012-preregistro.md. Toma data/exp011_panel.csv (1960-2014)
y reemplaza el outcome por la nueva familia de eventos. La logica es pura
(biblioteca estandar); leer Archigos (.rda) requiere pyreadr.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp005_build_panel as p5  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
YEAR_MAX = 2014
FAMILY_PREFIXES = ("Popular Protest", "Removed by Rebels")
# Gleditsch-Ward -> COW cuando difieren (Archigos usa GW; el panel, COW).
GW_TO_COW = {340: 345, 678: 679, 260: 255}


def is_family(exitcode):
    return str(exitcode).startswith(FAMILY_PREFIXES)


def event_years(episodes):
    """episodes: lista de (gw, anio). Devuelve set de (cow, anio)."""
    return {(GW_TO_COW.get(gw, gw), year) for gw, year in episodes}


def build(rows, events):
    out = []
    for r in rows:
        year = int(r["year"])
        if year > YEAR_MAX:
            continue
        cow = int(r["cow"])
        out.append({**r, "coup_outcome": r["outcome"],
                    "outcome": str(int((cow, year) in events)),
                    "rev_prev10": str(sum((cow, y) in events for y in range(year - 10, year)))})
    return out


def main():
    parser = argparse.ArgumentParser(description="EXP-012: panel de caidas por protesta o rebelion")
    parser.add_argument("--base", type=Path, default=ROOT / "data" / "exp011_panel.csv")
    parser.add_argument("--archigos", type=Path, default=ROOT / "_fuentes" / "AuthoritarianismBook" / "data" / "archigos.rda")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp012_panel.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "exp012_manifest.json")
    args = parser.parse_args()
    import pyreadr

    a = pyreadr.read_r(str(args.archigos))["archigos"]
    fam = a[a.exitcode.astype(str).str.startswith(FAMILY_PREFIXES)].copy()
    fam["year"] = fam.enddate.dt.year
    fam = fam[(fam.year >= 1950) & (fam.year <= YEAR_MAX)]
    episodes = [(int(g), int(y)) for g, y in zip(fam.GWn, fam.year)]
    events = event_years(episodes)
    with open(args.base, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns, rows = reader.fieldnames, list(reader)
    panel = build(rows, events)
    cols = columns + ["coup_outcome", "rev_prev10"]
    with open(args.panel, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(panel)
    keys = {(int(r["cow"]), int(r["year"])) for r in panel}
    listing = []
    for _, e in fam[fam.year >= 1960].sort_values("year").iterrows():
        cow = GW_TO_COW.get(int(e.GWn), int(e.GWn))
        listing.append({"anio": int(e.year), "pais": str(e.country_name), "gobernante": str(e.leader),
                        "exitcode": str(e.exitcode), "fecha": str(e.enddate.date()), "en_panel": (cow, int(e.year)) in keys})
    by = lambda lo, hi: {"filas": sum(lo <= int(r["year"]) <= hi for r in panel),  # noqa: E731
                         "eventos": sum(int(r["outcome"]) for r in panel if lo <= int(r["year"]) <= hi)}
    manifest = {"experimento": "EXP-012", "preregistro": "research/EXP-012-preregistro.md",
                "fuente": "Archigos via AuthoritarianismBook@51716224a08674b956a6434b0d18cd761311efde",
                "sha256_archigos_rda": p5.sha256(args.archigos), "sha256_base": p5.sha256(args.base),
                "sha256_panel": p5.sha256(args.panel), "familia": list(FAMILY_PREFIXES),
                "gw_a_cow": {str(k): v for k, v in GW_TO_COW.items()},
                "filas_panel": len(panel), "anios_pais_con_evento": sum(int(r["outcome"]) for r in panel),
                "episodios_desde_1960": len(listing), "episodios_en_panel": sum(x["en_panel"] for x in listing),
                "por_periodo": {"1960-1989": by(1960, 1989), "1990-2014": by(1990, 2014)},
                "episodios": listing}
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "episodios"}, ensure_ascii=False, indent=1))
    print("fuera del panel:", [(x["anio"], x["pais"], x["gobernante"]) for x in listing if not x["en_panel"]])


if __name__ == "__main__":
    main()
