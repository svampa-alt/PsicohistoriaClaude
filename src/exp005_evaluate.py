"""EXP-005: evaluacion confirmatoria preregistrada (research/EXP-005-preregistro.md).

Entrena en 1960-1989 del panel nuevo (data/exp005_panel.csv) y evalua:
- confirmatorio: anios 2012-2019 (nunca evaluados antes);
- secundario: 1990-2011 (comparacion con EXP-003/004, no confirmatorio).
Reutiliza exp003_model y exp004_tendencia sin cambios. Solo biblioteca estandar.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp003_model as m  # noqa: E402
import exp004_tendencia as t  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIRM = (2012, 2019)
SECONDARY = (1990, 2011)
MODELS = ("B0", "MH", "MT", "MX", "MX_c", "MT_c", "MH_c")


def restrict(result, lo, hi):
    """Subconjunto de filas de prueba entre lo y hi, con las mismas predicciones."""
    idx = [i for i, r in enumerate(result["test"]) if lo <= r["year"] <= hi]
    return {"test": [result["test"][i] for i in idx],
            "predictions": {k: [v[i] for i in idx] for k, v in result["predictions"].items() if k in MODELS}}


def hypotheses(summary):
    mx = summary["MX_c"]
    out = {}
    for name, ref in (("C1_MXc_mejor_que_B0", "B0"), ("C2_MXc_mejor_que_MH", "MH"), ("C3_MXc_mejor_que_MHc", "MH_c")):
        ci = mx[f"ic95_vs_{ref}"]
        out[name] = {"delta": mx[f"delta_brier_vs_{ref}"], "ic95": ci, "cumplida": ci[1] < 0}
    return out


def evaluate(rows, reps=m.BOOT_REPS):
    full = t.run(rows, test_start=m.TEST_START, k=t.K_PRE, with_tend=False)
    blocks = {}
    for name, (lo, hi) in (("confirmatorio_2012_2019", CONFIRM), ("secundario_1990_2011", SECONDARY)):
        sub = restrict(full, lo, hi)
        summary = t.summarize(sub, reps=reps)
        blocks[name] = {"n": len(sub["test"]), "eventos": sum(r["outcome"] for r in sub["test"]),
                        "tasa": sum(r["outcome"] for r in sub["test"]) / len(sub["test"]),
                        "modelos": summary, "hipotesis": hypotheses(summary)}
    return full, blocks


def main():
    parser = argparse.ArgumentParser(description="EXP-005: confirmacion preregistrada")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp005_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-005-results.json")
    args = parser.parse_args()
    rows = m.read_exp003_panel(args.panel)
    full, blocks = evaluate(rows)
    train = [r for r in rows if r["year"] < m.TEST_START]
    out = {"experimento": "EXP-005", "preregistro": "research/EXP-005-preregistro.md",
           "panel": {"filas": len(rows), "eventos": sum(r["outcome"] for r in rows)},
           "entrenamiento": {"n": len(train), "eventos": sum(r["outcome"] for r in train)},
           "r_0": full["r_0"], "r_t_por_anio": full["rates"], **blocks}
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    f = lambda ci: f"[{ci[0]:+.5f}, {ci[1]:+.5f}]" if ci else "-".ljust(22)  # noqa: E731
    for name, b in blocks.items():
        print(f"\n== {name}: {b['n']} obs, {b['eventos']} eventos, tasa {b['tasa']:.4f}")
        print(f"{'modelo':<7}{'Brier':>9}{'skill':>9}{'AUC':>7}{'p_med':>8}  IC vs B0                IC vs MH")
        for k, e in b["modelos"].items():
            print(f"{k:<7}{e['brier']:>9.5f}{e['skill_vs_B0']:>+9.4f}{e['auc']:>7.3f}{e['p_media']:>8.4f}  "
                  f"{f(e.get('ic95_vs_B0'))}  {f(e.get('ic95_vs_MH'))}")
        for h, v in b["hipotesis"].items():
            print(h, "CUMPLIDA" if v["cumplida"] else "no cumplida", f(v["ic95"]))


if __name__ == "__main__":
    main()
