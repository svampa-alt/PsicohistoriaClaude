"""EXP-005: control de calidad del panel nuevo contra el panel de EXP-003.

Une ambos paneles por codigo Polity y anio (el panel de EXP-003 se traduce con
polity_annual de AuthoritarianismBook) y mide coincidencias. Requiere pyreadr.
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    sy = math.sqrt(sum((b - my) ** 2 for b in ys))
    return sxy / (sx * sy)


def main():
    import pyreadr

    pa = pyreadr.read_r(str(ROOT / "_fuentes/AuthoritarianismBook/data/polity_annual.rda"))["polity_annual"]
    code = {(c, int(y)): int(p) for c, y, p in zip(pa.country_name, pa.year, pa.polity_ccode) if p == p}
    old = {}
    for r in read(ROOT / "data/exp003_panel.csv"):
        k = code.get((r["country"], int(r["year"])))
        if k is not None:
            old[(k, int(r["year"]))] = r
    new = {(int(r["ccode"]), int(r["year"])): r for r in read(ROOT / "data/exp005_panel.csv")}
    both = sorted(set(old) & set(new))
    f = lambda rs, c: [float(r[c]) for r in rs]  # noqa: E731
    o, n = [old[k] for k in both], [new[k] for k in both]
    disagree = [list(k) for k in both if old[k]["outcome"] != new[k]["outcome"]]
    out = {
        "filas_exp003": len(old), "filas_exp005_1960_2011": sum(1 for k in new if k[1] <= 2011),
        "filas_comunes": len(both),
        "outcome_coincide": sum(a["outcome"] == b["outcome"] for a, b in zip(o, n)),
        "outcome_distinto": disagree,
        "polity2_coincide": sum(a["polity2_lag"] == b["polity2_lag"] or float(a["polity2_lag"]) == float(b["polity2_lag"])
                                for a, b in zip(o, n)),
        "factional_coincide": sum(a["factional_lag"] == b["factional_lag"] for a, b in zip(o, n)),
        "corr_growth_lag": corr(f(o, "growth_lag"), f(n, "growth_lag")),
        "corr_loggdp_lag": corr(f(o, "loggdp_lag"), f(n, "loggdp_lag")),
        "corr_T": corr(f(o, "T"), f(n, "T")),
        "nota": "El PIB cambia de unidad (1990 GK a 2011 PPP) y de revision; se espera correlacion alta, no igualdad.",
    }
    (ROOT / "data/exp005_control.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "outcome_distinto"}, indent=1), "\ndistintos:", disagree[:20])


if __name__ == "__main__":
    main()
