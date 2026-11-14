"""EXP-004: correccion de tasa base (tendencia temporal) sobre los modelos de EXP-003.

Preregistro: research/EXP-004-preregistro.md (commit previo a la ejecucion).
Solo biblioteca estandar. No modifica resultados ni demo de EXP-003.
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp003_model as m  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
K_PRE = 10                 # preespecificado
K_EXPLORATORY = (5, 20)    # exploratorio
BASES = ("MX", "MT", "MH")


def logit(p):
    return math.log(p / (1.0 - p))


def smoothed_rate(events, n):
    return (events + 0.5) / (n + 1.0)


def recent_rates(rows, k):
    """r_t para cada anio t: tasa suavizada en [t-k, t-1]. None si no hay anios previos."""
    ev, n = defaultdict(int), defaultdict(int)
    for r in rows:
        ev[r["year"]] += r["outcome"]
        n[r["year"]] += 1
    out = {}
    for t in sorted(n):
        past = [y for y in n if t - k <= y < t]
        out[t] = smoothed_rate(sum(ev[y] for y in past), sum(n[y] for y in past)) if past else None
    return out


def shift(p, r_t, r_0):
    """Desplaza el nivel en escala logit sin tocar las pendientes."""
    return m._sigmoid(logit(p) + logit(r_t) - logit(r_0))


def run(rows, test_start=m.TEST_START, k=K_PRE, with_tend=True):
    base = m.run_models(rows, test_start=test_start, exploratory=False)
    train, test = base["train"], base["test"]
    r_0 = smoothed_rate(sum(r["outcome"] for r in train), len(train))
    rates = recent_rates(rows, k)
    preds = {name: base["predictions"][name] for name in ("B0", "MH", "MT", "MX")}
    for name in BASES:
        preds[name + "_c"] = [shift(p, rates[r["year"]], r_0)
                              for p, r in zip(base["predictions"][name], test)]
    models = {}
    if with_tend:
        feats = m.FEATURES["MX"]
        fit_rows = [r for r in train if rates[r["year"]] is not None]
        xs = [[r[f] for f in feats] + [rates[r["year"]]] for r in fit_rows]
        model = m.fit_logistic(xs, [r["outcome"] for r in fit_rows], m.RIDGE)
        models["MX_tend"] = model
        preds["MX_tend"] = [m.predict_logistic(model, [r[f] for f in feats] + [rates[r["year"]]])
                            for r in test]
    return {"test": test, "predictions": preds, "models": models, "r_0": r_0,
            "rates": {y: v for y, v in rates.items() if y >= test_start}}


def summarize(result, reps=m.BOOT_REPS, seed=m.SEED):
    test, preds = result["test"], result["predictions"]
    ys = [r["outcome"] for r in test]
    years = [r["year"] for r in test]
    b0 = m.brier_score(preds["B0"], ys)
    out = {}
    for name, ps in preds.items():
        bs = m.brier_score(ps, ys)
        entry = {"brier": bs, "skill_vs_B0": 1.0 - bs / b0, "auc": m.auc(ps, ys),
                 "p_media": sum(ps) / len(ps), "calibracion_quintiles": m.calibration(ps, ys)}
        for ref in ("B0", "MH", "MH_c"):
            if ref in preds and ref != name:
                entry[f"delta_brier_vs_{ref}"] = bs - m.brier_score(preds[ref], ys)
                entry[f"ic95_vs_{ref}"] = m.block_bootstrap_delta(ps, preds[ref], ys, years, reps, seed)
        out[name] = entry
    return out


def excludes_zero_below(ci):
    return ci[1] < 0


def main():
    parser = argparse.ArgumentParser(description="EXP-004: correccion de tasa base")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp003_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-004-results.json")
    args = parser.parse_args()
    rows = m.read_exp003_panel(args.panel)
    result = run(rows)
    summary = summarize(result)
    mx = summary["MX_c"]
    verdict = {
        "H1_MXc_mejor_que_B0": {"delta": mx["delta_brier_vs_B0"], "ic95": mx["ic95_vs_B0"],
                                "cumplida": excludes_zero_below(mx["ic95_vs_B0"])},
        "H2_MXc_mejor_que_MH": {"delta": mx["delta_brier_vs_MH"], "ic95": mx["ic95_vs_MH"],
                                "cumplida": excludes_zero_below(mx["ic95_vs_MH"])},
        "H3_MXc_mejor_que_MHc": {"delta": mx["delta_brier_vs_MH_c"], "ic95": mx["ic95_vs_MH_c"],
                                 "cumplida": excludes_zero_below(mx["ic95_vs_MH_c"])},
    }
    exploratory = {}
    for k in K_EXPLORATORY:
        s = summarize(run(rows, k=k, with_tend=False))
        exploratory[f"k={k}"] = {n: {"brier": s[n]["brier"], "auc": s[n]["auc"],
                                     "ic95_vs_B0": s[n]["ic95_vs_B0"], "ic95_vs_MH": s[n].get("ic95_vs_MH")}
                                 for n in ("MX_c", "MT_c", "MH_c")}
    out = {
        "experimento": "EXP-004", "preregistro": "research/EXP-004-preregistro.md",
        "advertencia": "La ventana de prueba ya era conocida por EXP-003; evidencia mas debil que una confirmacion sobre anios nuevos.",
        "preespecificado": {"k": K_PRE, "modelos": ["MX_c", "MT_c", "MH_c", "MX_tend"],
                            "bootstrap": {"bloques": "anio", "replicas": m.BOOT_REPS, "semilla": m.SEED}},
        "n_prueba": len(result["test"]), "eventos_prueba": sum(r["outcome"] for r in result["test"]),
        "r_0_entrenamiento": result["r_0"], "r_t_por_anio": result["rates"],
        "modelos": summary, "hipotesis": verdict,
        "coeficientes_MX_tend": dict(zip(("intercepto",) + m.FEATURES["MX"] + ("r_t",),
                                         result["models"]["MX_tend"]["beta"])),
        "exploratorio_sensibilidad_k": exploratory,
    }
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"prueba: {out['n_prueba']} obs, {out['eventos_prueba']} eventos | r_0={result['r_0']:.4f}")
    print(f"{'modelo':<9}{'Brier':>9}{'skill':>9}{'AUC':>7}{'p_media':>9}  IC95 vs B0              IC95 vs MH")
    f = lambda ci: f"[{ci[0]:+.5f}, {ci[1]:+.5f}]" if ci else "-".ljust(22)  # noqa: E731
    for name, e in summary.items():
        print(f"{name:<9}{e['brier']:>9.5f}{e['skill_vs_B0']:>+9.4f}{e['auc']:>7.3f}{e['p_media']:>9.4f}  "
              f"{f(e.get('ic95_vs_B0'))}  {f(e.get('ic95_vs_MH'))}")
    for h, v in verdict.items():
        print(h, "CUMPLIDA" if v["cumplida"] else "no cumplida", f(v["ic95"]))
    for k, v in exploratory.items():
        print("exploratorio", k, {n: round(x["brier"], 5) for n, x in v.items()})


if __name__ == "__main__":
    main()
