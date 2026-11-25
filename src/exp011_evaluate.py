"""EXP-011: evaluacion preregistrada de poder militar y movilizacion (research/EXP-011-preregistro.md).

Misma logica que EXP-010 (todos los modelos sobre las mismas filas). Solo biblioteca estandar.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp003_model as m  # noqa: E402
import exp007_interacciones as x  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EXTRA = ("mil_lag", "mob_lag")
SPECS = {"MXs": x.SPECS["MXs"], "MXm": x.SPECS["MXs"] + EXTRA}
EXPLORATORY = {"MX_mil": x.SPECS["MXs"] + ("mil_lag",), "MX_mob": x.SPECS["MXs"] + ("mob_lag",)}
REPORT = ("B0", "MH", "MXs_c", "MXm_c", "MX_mil_c", "MX_mob_c", "MXs", "MXm")


def read_panel(path, extra=EXTRA):
    rows = m.read_exp003_panel(path)
    with open(path, encoding="utf-8", newline="") as f:
        raw = {(r["country"], int(r["year"])): r for r in csv.DictReader(f)}
    for r in rows:
        for c in extra:
            r[c] = float(raw[(r["entity"], r["year"])][c])
    return rows


def evaluate(rows, lo, hi, reps=m.BOOT_REPS):
    test, preds = x.fit_predict(rows, specs={**SPECS, **EXPLORATORY})
    base = m.run_models(rows, exploratory=False)["predictions"]
    preds["B0"], preds["MH"] = base["B0"], base["MH"]
    idx = [i for i, r in enumerate(test) if lo <= r["year"] <= hi]
    ys = [test[i]["outcome"] for i in idx]
    years = [test[i]["year"] for i in idx]
    p = {k: [v[i] for i in idx] for k, v in preds.items()}
    out = {"n": len(ys), "eventos": sum(ys), "modelos": {}}
    for k in REPORT:
        e = {"brier": m.brier_score(p[k], ys), "auc": m.auc(p[k], ys), "p_media": sum(p[k]) / len(ys),
             "tipo": "exploratorio" if k.startswith(("MX_mil", "MX_mob")) else "preespecificado"}
        for ref in ("B0", "MH", "MXs_c"):
            if ref != k:
                e[f"ic95_vs_{ref}"] = m.block_bootstrap_delta(p[k], p[ref], ys, years, reps)
        out["modelos"][k] = e
    out["dAUC_MXm_c_vs_MXs_c"] = m.auc(p["MXm_c"], ys) - m.auc(p["MXs_c"], ys)
    out["ic95_dAUC"] = x.block_bootstrap_auc_delta(p["MXm_c"], p["MXs_c"], ys, years, reps)
    return out


def coefficients(rows):
    train = [r for r in rows if r["year"] < m.TEST_START]
    model = m.fit_logistic([[r[f] for f in SPECS["MXm"]] for r in train], [r["outcome"] for r in train], m.RIDGE)
    return dict(zip(("intercepto",) + SPECS["MXm"], model["beta"]))


def main():
    parser = argparse.ArgumentParser(description="EXP-011: evaluacion")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp011_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-011-results.json")
    args = parser.parse_args()
    rows = read_panel(args.panel)
    full, recent = evaluate(rows, 1990, 2025), evaluate(rows, 2020, 2025)
    d, s = full["modelos"]["MXm_c"], full["modelos"]["MXs_c"]
    hyp = {"M1_brier_MXm_c_menor": {"delta": d["brier"] - s["brier"], "ic95": d["ic95_vs_MXs_c"],
                                    "cumplida": d["ic95_vs_MXs_c"][1] < 0},
           "M2_auc_MXm_c_mayor": {"delta": full["dAUC_MXm_c_vs_MXs_c"], "ic95": full["ic95_dAUC"],
                                  "cumplida": full["ic95_dAUC"][0] > 0},
           "M3_MXm_c_mejor_que_B0_y_MH": {"ic95_vs_B0": d["ic95_vs_B0"], "ic95_vs_MH": d["ic95_vs_MH"],
                                          "cumplida": d["ic95_vs_B0"][1] < 0 and d["ic95_vs_MH"][1] < 0}}
    out = {"experimento": "EXP-011", "preregistro": "research/EXP-011-preregistro.md",
           "panel": "data/exp011_panel.csv", "coeficientes_MXm_estandarizados": coefficients(rows),
           "hipotesis": hyp, "1990_2025": full, "2020_2025": recent}
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    f = lambda ci: f"[{ci[0]:+.5f}, {ci[1]:+.5f}]"  # noqa: E731
    for name, w in (("1990-2025", full), ("2020-2025", recent)):
        print(f"\n== {name}: {w['n']} obs, {w['eventos']} eventos")
        for k, e in w["modelos"].items():
            ics = "  ".join(f"vs{r} {f(e['ic95_vs_' + r])}" for r in ("B0", "MH", "MXs_c") if "ic95_vs_" + r in e)
            print(f"  {k:<9} Brier {e['brier']:.5f} AUC {e['auc']:.3f} p̄ {e['p_media']:.4f}  {ics}")
        print(f"  dAUC MXm_c-MXs_c {w['dAUC_MXm_c_vs_MXs_c']:+.3f} {[round(v, 3) for v in w['ic95_dAUC']]}")
    print(json.dumps(hyp, indent=1)); print(json.dumps(out["coeficientes_MXm_estandarizados"], indent=1))


if __name__ == "__main__":
    main()
