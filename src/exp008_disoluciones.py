"""EXP-008: caso URSS 1991 y disoluciones comparables (research/EXP-008-preregistro.md).

Percentiles del indice T_v y sus componentes dentro del anio del evento, sobre
el panel V-Dem de EXP-006. Solo biblioteca estandar.
"""
import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp003_model as m  # noqa: E402
import exp007_interacciones as x  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CASES = (("URSS", "364", 1991), ("Yugoslavia", "345", 1991), ("Checoslovaquia", "315", 1992))
MEASURES = ("T", "E", "P", "I")
PERM_DRAWS = 100_000
PERM_SEED = 20261120


def percentile(value, others):
    """Proporcion de valores estrictamente menores mas la mitad de los empates (incluye al propio)."""
    below = sum(v < value for v in others)
    ties = sum(v == value for v in others)
    return (below + 0.5 * ties) / len(others)


def year_percentiles(values):
    """Percentil de cada elemento de una lista dentro de esa misma lista."""
    return [percentile(v, values) for v in values]


def permutation_p(observed_mean, pools, draws=PERM_DRAWS, seed=PERM_SEED):
    """P(media de percentiles de un Estado al azar por pool >= observada)."""
    rng = random.Random(seed)
    hits = 0
    for _ in range(draws):
        mean = sum(rng.choice(pool) for pool in pools) / len(pools)
        hits += mean >= observed_mean - 1e-12
    return hits / draws


def analyse(rows, coup_risk=None):
    by_year = defaultdict(list)
    for r in rows:
        by_year[int(r["year"])].append(r)
    cases, pools = [], []
    for name, code, year in CASES:
        group = by_year[year]
        case = next(r for r in group if r["ccode"] == code)
        out = {"caso": name, "ccode": int(code), "anio_evento": year, "datos_de": year - 1,
               "estados_en_el_anio": len(group)}
        for meas in MEASURES:
            vals = [float(r[meas]) for r in group]
            out[f"{meas}_valor"] = float(case[meas])
            out[f"{meas}_percentil"] = percentile(float(case[meas]), vals)
        ranking = sorted(group, key=lambda r: -float(r["T"]))
        out["T_puesto"] = 1 + next(i for i, r in enumerate(ranking) if r["ccode"] == code)
        out["top5_T_del_anio"] = [(r["country"], round(float(r["T"]), 3)) for r in ranking[:5]]
        if coup_risk is not None:
            risks = {(r["ccode"], int(r["year"])): p for r, p in coup_risk}
            yr = [p for (c, y), p in risks.items() if y == year]
            p = risks.get((code, year))
            out["riesgo_golpe_MXs_c"] = p
            out["riesgo_golpe_percentil"] = None if p is None else percentile(p, yr)
        cases.append(out)
        pools.append(year_percentiles([float(r["T"]) for r in group]))
    mean_pct = sum(c["T_percentil"] for c in cases) / len(cases)
    return cases, mean_pct, permutation_p(mean_pct, pools)


def coup_risk_rows(path):
    """Riesgo de golpe MXs_c (EXP-007) para cada fila >= 1990, como informacion adicional."""
    rows = m.read_exp003_panel(path)
    test, preds = x.fit_predict(rows, specs={"MXs": x.SPECS["MXs"]})
    with open(path, encoding="utf-8", newline="") as f:
        code = {(r["country"], int(r["year"])): r["ccode"] for r in csv.DictReader(f)}
    return [({"ccode": code[(r["entity"], r["year"])], "year": r["year"]}, p)
            for r, p in zip(test, preds["MXs_c"])]


def main():
    parser = argparse.ArgumentParser(description="EXP-008: disoluciones")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp006_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-008-results.json")
    args = parser.parse_args()
    with open(args.panel, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    cases, mean_pct, p_perm = analyse(rows, coup_risk_rows(args.panel))
    urss = cases[0]
    out = {"experimento": "EXP-008", "preregistro": "research/EXP-008-preregistro.md",
           "panel": "data/exp006_panel.csv", "casos": cases,
           "hipotesis": {
               "U1_URSS_percentil_T_ge_75": {"percentil": urss["T_percentil"], "cumplida": urss["T_percentil"] >= 0.75},
               "U2_media_percentiles_ge_75": {"media": mean_pct, "cumplida": mean_pct >= 0.75},
               "U3_permutacion_p_lt_005": {"p": p_perm, "sorteos": PERM_DRAWS, "semilla": PERM_SEED,
                                           "cumplida": p_perm < 0.05}}}
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for c in cases:
        print(f"\n{c['caso']} {c['anio_evento']} (datos {c['datos_de']}, {c['estados_en_el_anio']} Estados): "
              f"T puesto {c['T_puesto']}")
        for meas in MEASURES:
            print(f"  {meas}: valor {c[meas + '_valor']:.3f}  percentil {c[meas + '_percentil']:.2f}")
        print("  riesgo golpe MXs_c", c.get("riesgo_golpe_MXs_c"), "pct", c.get("riesgo_golpe_percentil"))
        print("  top5", c["top5_T_del_anio"])
    print("\n", json.dumps(out["hipotesis"], indent=1))


if __name__ == "__main__":
    main()
