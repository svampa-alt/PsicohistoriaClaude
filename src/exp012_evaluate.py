"""EXP-012: evaluacion preregistrada de caidas por protesta o rebelion (research/EXP-012-preregistro.md).

Solo biblioteca estandar.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp003_model as m  # noqa: E402
import exp007_interacciones as x  # noqa: E402
from psicohistoria import evaluate_baseline  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEST_END = 2014
SPECS = {"MHr": ("rev_prev10",),
         "MR": ("E", "P", "I", "loggdp_lag", "rev_prev10", "mil_lag", "mob_lag")}
EXTRA = ("rev_prev10", "mil_lag", "mob_lag")


def read_panel(path):
    rows = m.read_exp003_panel(path)
    with open(path, encoding="utf-8", newline="") as f:
        raw = {(r["country"], int(r["year"])): r for r in csv.DictReader(f)}
    for r in rows:
        for c in EXTRA:
            r[c] = float(raw[(r["entity"], r["year"])][c])
    return rows


def rank_in_year(test, ps, i):
    year = test[i]["year"]
    group = sorted((p for r, p in zip(test, ps) if r["year"] == year), reverse=True)
    pos = 1 + sum(p > ps[i] for p in group)
    return pos, len(group)


def evaluate(rows, reps=m.BOOT_REPS):
    test, preds = x.fit_predict(rows, specs=SPECS)
    b0 = {(p["year"], p["entity"]): p["p"] for p in evaluate_baseline(rows, m.TEST_START)["predictions"]}
    preds["B0"] = [b0[(r["year"], r["entity"])] for r in test]
    ys = [r["outcome"] for r in test]
    years = [r["year"] for r in test]
    models = {}
    for k in ("B0", "MHr", "MHr_c", "MR", "MR_c"):
        e = {"brier": m.brier_score(preds[k], ys), "auc": m.auc(preds[k], ys), "p_media": sum(preds[k]) / len(ys)}
        for ref in ("B0", "MHr"):
            if ref != k:
                e[f"ic95_vs_{ref}"] = m.block_bootstrap_delta(preds[k], preds[ref], ys, years, reps)
        models[k] = e
    episodes = []
    for i, r in enumerate(test):
        if r["outcome"]:
            pos, n = rank_in_year(test, preds["MR_c"], i)
            episodes.append({"anio": r["year"], "pais": r["entity"], "p_MR_c": preds["MR_c"][i],
                             "puesto": pos, "de": n, "percentil": 1 - (pos - 1) / n,
                             "mob_lag": r["mob_lag"], "mil_lag": r["mil_lag"]})
    return test, preds, models, episodes


def in_sample_cases(rows, cases=(("Iran", 1979), ("Romania", 1989), ("Philippines", 1986))):
    """Puesto de riesgo dentro de muestra (modelo ajustado con 1960-1989) para casos historicos."""
    train = [r for r in rows if r["year"] < m.TEST_START]
    feats = SPECS["MR"]
    model = m.fit_logistic([[r[f] for f in feats] for r in train], [r["outcome"] for r in train], m.RIDGE)
    out = []
    for name, year in cases:
        group = [(r["entity"], m.predict_logistic(model, [r[f] for f in feats]), r["outcome"]) for r in train if r["year"] == year]
        match = [g for g in group if g[0].startswith(name)]
        if not match:
            out.append({"caso": f"{name} {year}", "en_panel": False})
            continue
        p = match[0][1]
        pos = 1 + sum(q > p for _, q, _ in group)
        out.append({"caso": f"{name} {year}", "en_panel": True, "p": p, "puesto": pos, "de": len(group),
                    "evento": match[0][2], "nota": "ajuste dentro de muestra, no pronostico"})
    return out


def main():
    parser = argparse.ArgumentParser(description="EXP-012: evaluacion")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp012_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-012-results.json")
    args = parser.parse_args()
    rows = read_panel(args.panel)
    test, preds, models, episodes = evaluate(rows)
    mr = models["MR_c"]
    hyp = {"R1_MRc_mejor_que_B0": {"ic95": mr["ic95_vs_B0"], "cumplida": mr["ic95_vs_B0"][1] < 0},
           "R2_MRc_mejor_que_MHr": {"ic95": mr["ic95_vs_MHr"], "cumplida": mr["ic95_vs_MHr"][1] < 0},
           "R3_AUC_MRc_ge_070": {"auc": mr["auc"], "cumplida": mr["auc"] >= 0.70}}
    train = [r for r in rows if r["year"] < m.TEST_START]
    model = m.fit_logistic([[r[f] for f in SPECS["MR"]] for r in train], [r["outcome"] for r in train], m.RIDGE)
    out = {"experimento": "EXP-012", "preregistro": "research/EXP-012-preregistro.md",
           "panel": "data/exp012_panel.csv", "n_prueba": len(test), "eventos_prueba": sum(r["outcome"] for r in test),
           "coeficientes_MR_estandarizados": dict(zip(("intercepto",) + SPECS["MR"], model["beta"])),
           "modelos": models, "hipotesis": hyp, "episodios_prueba": episodes,
           "casos_dentro_de_muestra": in_sample_cases(rows)}
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"prueba {len(test)} obs, {out['eventos_prueba']} eventos")
    for k, e in models.items():
        ics = "  ".join(f"vs{r} [{e['ic95_vs_' + r][0]:+.5f}, {e['ic95_vs_' + r][1]:+.5f}]" for r in ("B0", "MHr") if "ic95_vs_" + r in e)
        print(f"  {k:<6} Brier {e['brier']:.5f} AUC {e['auc']:.3f} p̄ {e['p_media']:.4f}  {ics}")
    print(json.dumps(hyp, indent=1))
    print(json.dumps(out["coeficientes_MR_estandarizados"], indent=1))
    for e in episodes:
        print(f"  {e['anio']} {e['pais'][:28]:<28} p {e['p_MR_c']:.3f} puesto {e['puesto']}/{e['de']}  mob {e['mob_lag']:.2f}")
    print(json.dumps(out["casos_dentro_de_muestra"], indent=1))


if __name__ == "__main__":
    main()
