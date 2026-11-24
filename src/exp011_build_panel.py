"""EXP-011: agrega poder militar (v2x_ex_military) y movilizacion masiva (v2cagenmob)
de V-Dem v16 al panel de EXP-006. Preregistro: research/EXP-011-preregistro.md.
La union es pura (biblioteca estandar); la lectura de V-Dem requiere pyreadr.
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp005_build_panel as p5  # noqa: E402
import exp006_build_panel as p6  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TRAIN_END = 1989


def add_vdem(rows, vdem):
    """vdem: {(cow, year): (military, mobilization)}. Agrega t-1; descarta si falta alguno."""
    kept, dropped = [], []
    for r in rows:
        v = vdem.get((int(r["cow"]), int(r["year"]) - 1))
        if v is None or any(x is None or math.isnan(x) for x in v):
            dropped.append(r)
            continue
        kept.append({**r, "mil_lag": v[0], "mob_raw_lag": v[1]})
    return kept, dropped


def rescale_mobilization(rows):
    train = [r["mob_raw_lag"] for r in rows if int(r["year"]) <= TRAIN_END]
    q05, q95 = p6.quantile(train, 0.05), p6.quantile(train, 0.95)
    for r in rows:
        r["mob_lag"] = p6.clip((r["mob_raw_lag"] - q05) / (q95 - q05))
    return q05, q95


def main():
    parser = argparse.ArgumentParser(description="EXP-011: panel con poder militar y movilizacion")
    parser.add_argument("--base", type=Path, default=ROOT / "data" / "exp006_panel.csv")
    parser.add_argument("--vdem", type=Path, default=ROOT / "_fuentes" / "vdem16" / "vdem.RData")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp011_panel.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "exp011_manifest.json")
    args = parser.parse_args()
    import pyreadr

    with open(args.base, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns, rows = reader.fieldnames, list(reader)
    v = pyreadr.read_r(str(args.vdem))["vdem"]
    v = v[(v.year >= 1958) & v.COWcode.notna()]
    vdem = {(int(c), int(y)): (None if a != a else float(a), None if b != b else float(b))
            for c, y, a, b in zip(v.COWcode, v.year, v.v2x_ex_military, v.v2cagenmob)}
    kept, dropped = add_vdem(rows, vdem)
    q05, q95 = rescale_mobilization(kept)
    cols = columns + ["mil_lag", "mob_raw_lag", "mob_lag"]
    with open(args.panel, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for r in kept:
            w.writerow([p5.fmt(r[c]) if isinstance(r[c], float) else r[c] for c in cols])
    by = lambda lo, hi: {"filas": sum(lo <= int(r["year"]) <= hi for r in kept),  # noqa: E731
                         "eventos": sum(int(r["outcome"]) for r in kept if lo <= int(r["year"]) <= hi)}
    manifest = {"experimento": "EXP-011", "preregistro": "research/EXP-011-preregistro.md",
                "base": "data/exp006_panel.csv", "sha256_base": p5.sha256(args.base),
                "sha256_vdem": p5.sha256(args.vdem), "sha256_panel": p5.sha256(args.panel),
                "filas_panel": len(kept), "eventos_panel": sum(int(r["outcome"]) for r in kept),
                "filas_descartadas": len(dropped), "eventos_descartados": sum(int(r["outcome"]) for r in dropped),
                "paises_con_filas_descartadas": sorted({r["country"] for r in dropped}),
                "cuantiles_v2cagenmob_entrenamiento": {"q05": q05, "q95": q95},
                "por_periodo": {"1960-1989": by(1960, 1989), "1990-2019": by(1990, 2019), "2020-2025": by(2020, 2025)}}
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
