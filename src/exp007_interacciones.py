"""EXP-007: aporte de las interacciones E×I y P×I (preregistro: research/EXP-007-preregistro.md).

Compara MX (con interacciones) contra MXs (sin interacciones) sobre el panel
V-Dem de EXP-006, con y sin correccion de tasa base. Solo biblioteca estandar.
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp003_model as m  # noqa: E402
import exp004_tendencia as t  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE = ("E", "P", "I", "loggdp_lag", "coups_prev10")
SPECS = {"MX": BASE + ("ExI", "PxI"), "MXs": BASE}
EXPLORATORY = {"MX_soloExI": BASE + ("ExI",), "MX_soloPxI": BASE + ("PxI",)}
WINDOWS = (("1990_2025", 1990, 2025), ("1990_2011", 1990, 2011),
           ("2012_2019", 2012, 2019), ("2020_2025", 2020, 2025))
PAIRS = (("MX_c", "MXs_c"), ("MX", "MXs"))


def fit_predict(rows, test_start=m.TEST_START, k=t.K_PRE, specs=None):
    specs = specs or {**SPECS, **EXPLORATORY}
    rows = sorted(rows, key=lambda r: (r["year"], r["entity"]))
    train = [r for r in rows if r["year"] < test_start]
    test = [r for r in rows if r["year"] >= test_start]
    r_0 = t.smoothed_rate(sum(r["outcome"] for r in train), len(train))
    rates = t.recent_rates(rows, k)
    ys = [r["outcome"] for r in train]
    preds = {}
    for name, feats in specs.items():
        model = m.fit_logistic([[r[f] for f in feats] for r in train], ys, m.RIDGE)
        raw = [m.predict_logistic(model, [r[f] for f in feats]) for r in test]
        preds[name] = raw
        preds[name + "_c"] = [t.shift(p, rates[r["year"]], r_0) for p, r in zip(raw, test)]
    return test, preds


def block_bootstrap_auc_delta(pa, pb, ys, years, reps=m.BOOT_REPS, seed=m.SEED):
    """IC95 de AUC(a) - AUC(b) remuestreando anios completos."""
    blocks = defaultdict(list)
    for i, year in enumerate(years):
        blocks[year].append(i)
    keys = sorted(blocks)
    rng = random.Random(seed)
    deltas = []
    for _ in range(reps):
        idx = [i for _ in keys for i in blocks[keys[rng.randrange(len(keys))]]]
        y = [ys[i] for i in idx]
        a, b = m.auc([pa[i] for i in idx], y), m.auc([pb[i] for i in idx], y)
        if a is not None and b is not None:
            deltas.append(a - b)
    deltas.sort()
    q = lambda f: deltas[min(len(deltas) - 1, int(round(f * (len(deltas) - 1))))]  # noqa: E731
    return [q(0.025), q(0.975)]


def compare(test, preds, lo, hi, reps=m.BOOT_REPS):
    idx = [i for i, r in enumerate(test) if lo <= r["year"] <= hi]
    ys = [test[i]["outcome"] for i in idx]
    years = [test[i]["year"] for i in idx]
    p = {k: [v[i] for i in idx] for k, v in preds.items()}
    out = {"n": len(idx), "eventos": sum(ys),
           "modelos": {k: {"brier": m.brier_score(v, ys), "auc": m.auc(v, ys)} for k, v in p.items()}}
    for a, b in PAIRS:
        out[f"{a}_vs_{b}"] = {
            "delta_brier": m.brier_score(p[a], ys) - m.brier_score(p[b], ys),
            "ic95_brier": m.block_bootstrap_delta(p[a], p[b], ys, years, reps),
            "delta_auc": m.auc(p[a], ys) - m.auc(p[b], ys),
            "ic95_auc": block_bootstrap_auc_delta(p[a], p[b], ys, years, reps)}
    return out


def main():
    parser = argparse.ArgumentParser(description="EXP-007: aporte de las interacciones")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp006_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-007-results.json")
    args = parser.parse_args()
    rows = m.read_exp003_panel(args.panel)
    test, preds = fit_predict(rows)
    windows = {name: compare(test, preds, lo, hi) for name, lo, hi in WINDOWS}
    main_cmp = windows["1990_2025"]["MX_c_vs_MXs_c"]
    out = {"experimento": "EXP-007", "preregistro": "research/EXP-007-preregistro.md",
           "panel": "data/exp006_panel.csv", "especificaciones": {k: list(v) for k, v in SPECS.items()},
           "exploratorio": {k: list(v) for k, v in EXPLORATORY.items()},
           "hipotesis": {
               "I1_brier_MXc_menor_que_MXsc": {**{k: main_cmp[k] for k in ("delta_brier", "ic95_brier")},
                                                "cumplida": main_cmp["ic95_brier"][1] < 0,
                                                "interacciones_empeoran": main_cmp["ic95_brier"][0] > 0},
               "I2_auc_MXc_mayor_que_MXsc": {**{k: main_cmp[k] for k in ("delta_auc", "ic95_auc")},
                                             "cumplida": main_cmp["ic95_auc"][0] > 0}},
           "ventanas": windows}
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    for name, w in windows.items():
        print(f"\n== {name}: {w['n']} obs, {w['eventos']} eventos")
        for k in ("MX", "MXs", "MX_c", "MXs_c", "MX_soloExI_c", "MX_soloPxI_c"):
            print(f"  {k:<14} Brier {w['modelos'][k]['brier']:.5f}  AUC {w['modelos'][k]['auc']:.3f}")
        for a, b in PAIRS:
            c = w[f"{a}_vs_{b}"]
            print(f"  {a} - {b}: dBrier {c['delta_brier']:+.5f} {[round(x, 5) for x in c['ic95_brier']]}"
                  f"  dAUC {c['delta_auc']:+.3f} {[round(x, 3) for x in c['ic95_auc']]}")
    print("\n", json.dumps(out["hipotesis"], indent=1))


if __name__ == "__main__":
    main()
