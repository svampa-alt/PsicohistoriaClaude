"""EXP-006: evaluacion preregistrada (research/EXP-006-preregistro.md).

Panel con V-Dem (data/exp006_panel.csv). Entrena en 1960-1989 y evalua:
- confirmatorio 2020-2025;
- secundario A 2012-2019 (comparable con EXP-005, que usaba Polity);
- secundario B 2020-2023 (sin el PIB empalmado del Banco Mundial).
Reutiliza exp003_model, exp004_tendencia y exp005_evaluate sin cambios.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp003_model as m  # noqa: E402
import exp004_tendencia as t  # noqa: E402
import exp005_evaluate as e5  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BLOCKS = (("confirmatorio_2020_2025", 2020, 2025),
          ("secundario_A_2012_2019", 2012, 2019),
          ("secundario_B_2020_2023", 2020, 2023))
RENAME = {"C1_MXc_mejor_que_B0": "D1_MXc_mejor_que_B0",
          "C2_MXc_mejor_que_MH": "D2_MXc_mejor_que_MH",
          "C3_MXc_mejor_que_MHc": "D3_MXc_mejor_que_MHc"}


def evaluate(rows, reps=m.BOOT_REPS):
    full = t.run(rows, test_start=m.TEST_START, k=t.K_PRE, with_tend=False)
    out = {}
    for name, lo, hi in BLOCKS:
        sub = e5.restrict(full, lo, hi)
        summary = t.summarize(sub, reps=reps)
        ys = [r["outcome"] for r in sub["test"]]
        by_year = {}
        for r, mx, b0 in zip(sub["test"], sub["predictions"]["MX_c"], sub["predictions"]["B0"]):
            d = by_year.setdefault(r["year"], {"n": 0, "eventos": 0, "p_MX_c": 0.0, "p_B0": 0.0})
            d["n"] += 1
            d["eventos"] += r["outcome"]
            d["p_MX_c"] += mx
            d["p_B0"] += b0
        for d in by_year.values():
            d["tasa"] = d["eventos"] / d["n"]
            d["p_MX_c"] /= d["n"]
            d["p_B0"] /= d["n"]
        out[name] = {"n": len(ys), "eventos": sum(ys), "tasa": sum(ys) / len(ys), "modelos": summary,
                     "hipotesis": {RENAME[k]: v for k, v in e5.hypotheses(summary).items()},
                     "por_anio": by_year}
    return full, out


def main():
    parser = argparse.ArgumentParser(description="EXP-006: evaluacion con V-Dem")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp006_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-006-results.json")
    args = parser.parse_args()
    rows = m.read_exp003_panel(args.panel)
    full, blocks = evaluate(rows)
    train = [r for r in rows if r["year"] < m.TEST_START]
    coefs = {k: dict(zip(("intercepto",) + m.FEATURES[k], full_model["beta"]))
             for k, full_model in m.run_models(rows, exploratory=False)["models"].items()}
    out = {"experimento": "EXP-006", "preregistro": "research/EXP-006-preregistro.md",
           "panel": {"filas": len(rows), "eventos": sum(r["outcome"] for r in rows)},
           "entrenamiento": {"n": len(train), "eventos": sum(r["outcome"] for r in train)},
           "coeficientes_estandarizados": coefs, "r_0": full["r_0"], "r_t_por_anio": full["rates"], **blocks}
    args.results.write_text(json.dumps(out, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    f = lambda ci: f"[{ci[0]:+.5f}, {ci[1]:+.5f}]" if ci else "-".ljust(22)  # noqa: E731
    for name, b in blocks.items():
        print(f"\n== {name}: {b['n']} obs, {b['eventos']} eventos, tasa {b['tasa']:.4f}")
        for k, e in b["modelos"].items():
            print(f"{k:<7}{e['brier']:>9.5f}{e['skill_vs_B0']:>+9.4f}{e['auc']:>7.3f}{e['p_media']:>8.4f}  "
                  f"{f(e.get('ic95_vs_B0'))}  {f(e.get('ic95_vs_MH'))}")
        for h, v in b["hipotesis"].items():
            print(h, "CUMPLIDA" if v["cumplida"] else "no cumplida", f(v["ic95"]))
    print("\npor año (confirmatorio):")
    for y, d in sorted(blocks["confirmatorio_2020_2025"]["por_anio"].items()):
        print(y, d["n"], d["eventos"], f"tasa {d['tasa']:.4f}  MX_c {d['p_MX_c']:.4f}  B0 {d['p_B0']:.4f}")


if __name__ == "__main__":
    main()
