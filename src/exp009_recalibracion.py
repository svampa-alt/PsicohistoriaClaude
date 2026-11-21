"""EXP-009: recalibracion rapida del nivel (preregistro: research/EXP-009-preregistro.md).

MXs (sin interacciones) entrenado en 1960-1989 sobre el panel V-Dem. Para cada
anio t se ajusta un desplazamiento del intercepto con los errores del modelo en
t-5..t-1. Solo biblioteca estandar.
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp003_model as m  # noqa: E402
import exp004_tendencia as t  # noqa: E402
import exp007_interacciones as x  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WINDOW = 5
RIDGE_A = 1.0


def fit_offset(logits, ys, ridge=RIDGE_A, iters=200):
    """Desplazamiento a que maximiza la verosimilitud de sigma(z + a), con penalizacion ridge/2·a²."""
    a = 0.0
    for _ in range(iters):
        ps = [m._sigmoid(z + a) for z in logits]
        grad = sum(p - y for p, y in zip(ps, ys)) + ridge * a
        hess = sum(p * (1 - p) for p in ps) + ridge
        step = max(-1.0, min(1.0, grad / hess))  # Newton amortiguado: evita saltos lejos del optimo
        a -= step
        if abs(step) < 1e-12:
            break
    return a


def logit(p):
    return math.log(p / (1 - p))


def run(rows, test_start=m.TEST_START, window=WINDOW):
    rows = sorted(rows, key=lambda r: (r["year"], r["entity"]))
    feats = x.SPECS["MXs"]
    train = [r for r in rows if r["year"] < test_start]
    model = m.fit_logistic([[r[f] for f in feats] for r in train], [r["outcome"] for r in train], m.RIDGE)
    raw = {(r["year"], r["entity"]): m.predict_logistic(model, [r[f] for f in feats]) for r in rows}
    by_year = defaultdict(list)
    for r in rows:
        by_year[r["year"]].append(r)
    test = [r for r in rows if r["year"] >= test_start]
    r_0 = t.smoothed_rate(sum(r["outcome"] for r in train), len(train))
    rate10, rate5 = t.recent_rates(rows, 10), t.recent_rates(rows, 5)
    offsets = {}
    for year in sorted({r["year"] for r in test}):
        past = [r for y in range(year - window, year) for r in by_year.get(y, [])]
        offsets[year] = fit_offset([logit(raw[(r["year"], r["entity"])]) for r in past],
                                   [r["outcome"] for r in past])
    preds = {"B0": None, "MH": None}
    base = m.run_models(rows, test_start=test_start, exploratory=False)
    preds["B0"], preds["MH"] = base["predictions"]["B0"], base["predictions"]["MH"]
    p_raw = [raw[(r["year"], r["entity"])] for r in test]
    preds["MXs"] = p_raw
    preds["MXs_c10"] = [t.shift(p, rate10[r["year"]], r_0) for p, r in zip(p_raw, test)]
    preds["MXs_c5"] = [t.shift(p, rate5[r["year"]], r_0) for p, r in zip(p_raw, test)]
    preds["MXs_r5"] = [m._sigmoid(logit(p) + offsets[r["year"]]) for p, r in zip(p_raw, test)]
    return test, preds, offsets


def window_stats(test, preds, lo, hi, reps=m.BOOT_REPS):
    idx = [i for i, r in enumerate(test) if lo <= r["year"] <= hi]
    ys = [test[i]["outcome"] for i in idx]
    years = [test[i]["year"] for i in idx]
    p = {k: [v[i] for i in idx] for k, v in preds.items()}
    out = {"n": len(ys), "eventos": sum(ys), "tasa": sum(ys) / len(ys), "modelos": {}}
    for k, v in p.items():
        e = {"brier": m.brier_score(v, ys), "auc": m.auc(v, ys), "p_media": sum(v) / len(v),
             "brecha_nivel": abs(sum(v) / len(v) - sum(ys) / len(ys))}
        for ref in ("B0", "MH", "MXs_c10"):
            if ref != k:
                e[f"delta_vs_{ref}"] = e["brier"] - m.brier_score(p[ref], ys)
                e[f"ic95_vs_{ref}"] = m.block_bootstrap_delta(v, p[ref], ys, years, reps)
        out["modelos"][k] = e
    return out


def main():
    parser = argparse.ArgumentParser(description="EXP-009: recalibracion rapida")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp006_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-009-results.json")
    args = parser.parse_args()
    rows = m.read_exp003_panel(args.panel)
    test, preds, offsets = run(rows)
    full = window_stats(test, preds, 1990, 2025)
    recent = window_stats(test, preds, 2020, 2025)
    r5, c10 = full["modelos"]["MXs_r5"], full["modelos"]["MXs_c10"]
    hyp = {
        "K1_r5_mejor_que_c10": {"delta": r5["delta_vs_MXs_c10"], "ic95": r5["ic95_vs_MXs_c10"],
                                "cumplida": r5["ic95_vs_MXs_c10"][1] < 0},
        "K2_r5_mejor_que_B0_y_MH": {"ic95_vs_B0": r5["ic95_vs_B0"], "ic95_vs_MH": r5["ic95_vs_MH"],
                                    "cumplida": r5["ic95_vs_B0"][1] < 0 and r5["ic95_vs_MH"][1] < 0},
        "K3_brecha_2020_2025": {"r5": recent["modelos"]["MXs_r5"]["brecha_nivel"],
                                "c10": recent["modelos"]["MXs_c10"]["brecha_nivel"],
                                "cumplida": recent["modelos"]["MXs_r5"]["brecha_nivel"]
                                < recent["modelos"]["MXs_c10"]["brecha_nivel"]}}
    per_year = {}
    for i, r in enumerate(test):
        d = per_year.setdefault(r["year"], {"n": 0, "eventos": 0, "r5": 0.0, "c10": 0.0})
        d["n"] += 1
        d["eventos"] += r["outcome"]
        d["r5"] += preds["MXs_r5"][i]
        d["c10"] += preds["MXs_c10"][i]
    per_year = {y: {"tasa": d["eventos"] / d["n"], "p_r5": d["r5"] / d["n"], "p_c10": d["c10"] / d["n"],
                    "offset": offsets[y]} for y, d in sorted(per_year.items())}
    out = {"experimento": "EXP-009", "preregistro": "research/EXP-009-preregistro.md",
           "panel": "data/exp006_panel.csv", "hipotesis": hyp, "1990_2025": full, "2020_2025": recent,
           "por_anio": per_year}
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    f = lambda ci: f"[{ci[0]:+.5f}, {ci[1]:+.5f}]"  # noqa: E731
    for name, w in (("1990-2025", full), ("2020-2025", recent)):
        print(f"\n== {name}: {w['n']} obs, {w['eventos']} eventos, tasa {w['tasa']:.4f}")
        for k, e in w["modelos"].items():
            extra = "  ".join(f"vs{ref} {f(e['ic95_vs_' + ref])}" for ref in ("B0", "MH", "MXs_c10") if "ic95_vs_" + ref in e)
            print(f"  {k:<8} Brier {e['brier']:.5f} AUC {e['auc']:.3f} p̄ {e['p_media']:.4f}  {extra}")
    print("\n", json.dumps(hyp, indent=1))
    for y in range(2016, 2026):
        d = per_year[y]
        print(y, f"tasa {d['tasa']:.4f} r5 {d['p_r5']:.4f} c10 {d['p_c10']:.4f} a {d['offset']:+.2f}")


if __name__ == "__main__":
    main()
