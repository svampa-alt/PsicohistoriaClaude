"""EXP-010: evaluacion preregistrada de poblacion y urbanizacion (research/EXP-010-preregistro.md).

Todos los modelos sobre las mismas filas de data/exp010_panel.csv. Solo biblioteca estandar.
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
SPECS = {"MXs": x.SPECS["MXs"], "MXd": x.SPECS["MXs"] + ("lpop_lag", "urb_lag")}


def read_panel(path):
    rows = m.read_exp003_panel(path)
    with open(path, encoding="utf-8", newline="") as f:
        extra = {(r["country"], int(r["year"])): r for r in csv.DictReader(f)}
    for r in rows:
        e = extra[(r["entity"], r["year"])]
        r["lpop_lag"], r["urb_lag"] = float(e["lpop_lag"]), float(e["urb_lag"])
    return rows


def evaluate(rows, lo, hi, reps=m.BOOT_REPS):
    test, preds = x.fit_predict(rows, specs=SPECS)
    base = m.run_models(rows, exploratory=False)["predictions"]
    preds["B0"], preds["MH"] = base["B0"], base["MH"]
    idx = [i for i, r in enumerate(test) if lo <= r["year"] <= hi]
    ys = [test[i]["outcome"] for i in idx]
    years = [test[i]["year"] for i in idx]
    p = {k: [v[i] for i in idx] for k, v in preds.items()}
    out = {"n": len(ys), "eventos": sum(ys), "modelos": {}}
    for k in ("B0", "MH", "MXs_c", "MXd_c", "MXs", "MXd"):
        e = {"brier": m.brier_score(p[k], ys), "auc": m.auc(p[k], ys), "p_media": sum(p[k]) / len(ys)}
        for ref in ("B0", "MH", "MXs_c"):
            if ref != k:
                e[f"ic95_vs_{ref}"] = m.block_bootstrap_delta(p[k], p[ref], ys, years, reps)
        out["modelos"][k] = e
    out["dAUC_MXd_c_vs_MXs_c"] = m.auc(p["MXd_c"], ys) - m.auc(p["MXs_c"], ys)
    out["ic95_dAUC"] = x.block_bootstrap_auc_delta(p["MXd_c"], p["MXs_c"], ys, years, reps)
    return out


def coefficients(rows):
    train = [r for r in rows if r["year"] < m.TEST_START]
    model = m.fit_logistic([[r[f] for f in SPECS["MXd"]] for r in train], [r["outcome"] for r in train], m.RIDGE)
    return dict(zip(("intercepto",) + SPECS["MXd"], model["beta"]))


def main():
    parser = argparse.ArgumentParser(description="EXP-010: evaluacion demografica")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp010_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-010-results.json")
    args = parser.parse_args()
    rows = read_panel(args.panel)
    full, recent = evaluate(rows, 1990, 2025), evaluate(rows, 2020, 2025)
    d, s = full["modelos"]["MXd_c"], full["modelos"]["MXs_c"]
    hyp = {"G1_brier_MXd_c_menor": {"delta": d["brier"] - s["brier"], "ic95": d["ic95_vs_MXs_c"],
                                    "cumplida": d["ic95_vs_MXs_c"][1] < 0},
           "G2_auc_MXd_c_mayor": {"delta": full["dAUC_MXd_c_vs_MXs_c"], "ic95": full["ic95_dAUC"],
                                  "cumplida": full["ic95_dAUC"][0] > 0},
           "G3_MXd_c_mejor_que_B0_y_MH": {"ic95_vs_B0": d["ic95_vs_B0"], "ic95_vs_MH": d["ic95_vs_MH"],
                                          "cumplida": d["ic95_vs_B0"][1] < 0 and d["ic95_vs_MH"][1] < 0}}
    out = {"experimento": "EXP-010", "preregistro": "research/EXP-010-preregistro.md",
           "panel": "data/exp010_panel.csv", "coeficientes_MXd_estandarizados": coefficients(rows),
           "hipotesis": hyp, "1990_2025": full, "2020_2025": recent}
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    f = lambda ci: f"[{ci[0]:+.5f}, {ci[1]:+.5f}]"  # noqa: E731
    for name, w in (("1990-2025", full), ("2020-2025", recent)):
        print(f"\n== {name}: {w['n']} obs, {w['eventos']} eventos")
        for k, e in w["modelos"].items():
            ics = "  ".join(f"vs{r} {f(e['ic95_vs_' + r])}" for r in ("B0", "MH", "MXs_c") if "ic95_vs_" + r in e)
            print(f"  {k:<6} Brier {e['brier']:.5f} AUC {e['auc']:.3f} p̄ {e['p_media']:.4f}  {ics}")
        print(f"  dAUC MXd_c-MXs_c {w['dAUC_MXd_c_vs_MXs_c']:+.3f} {[round(v, 3) for v in w['ic95_dAUC']]}")
    print(json.dumps(hyp, indent=1)); print(json.dumps(out["coeficientes_MXd_estandarizados"], indent=1))


if __name__ == "__main__":
    main()
