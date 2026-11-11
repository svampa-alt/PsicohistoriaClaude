"""EXP-003: indice T (EXP-001, pesos sin ajustar) frente a golpes de Estado.

Solo biblioteca estandar. Lee data/exp003_panel.csv (generado por
src/exp003_build_panel.py) y compara, con corte temporal preespecificado,
baselines simples contra logisticas sobre T y sus componentes.

PREESPECIFICADO: corte 1960-1989 / 1990-2014, modelos B0, B1, MT, MH, MX,
ridge=1, 1000 replicas bootstrap por bloques anuales, semilla 20261111.
EXPLORATORIO: MT_expansivo y MX_expansivo (reajuste anual con anios previos).
"""
import argparse
import csv
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from psicohistoria import evaluate_baseline, evaluate_entity_baseline  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TRAIN_START, TEST_START, TEST_END = 1960, 1990, 2014
RIDGE = 1.0
B1_STRENGTH = 5.0
BOOT_REPS = 1000
SEED = 20261111
WEIGHTS = (0.40, 0.35, 0.25)  # EXP-001, no ajustados con datos
FACTIONAL = ("Factional", "Factional/Restricted",
             "Electoral Transition: Persistent Conflict/Coercion")
PLACEHOLDER = "/*__EXP003_JSON__*/null"

FEATURES = {
    "MT": ("T",),
    "MH": ("coups_prev10",),
    "MX": ("E", "P", "I", "loggdp_lag", "coups_prev10", "ExI", "PxI"),
}
EXPLORATORY = {"MT_expansivo": "MT", "MX_expansivo": "MX"}


# ---------- indice T (definicion unica, usada tambien por el constructor) ----------

def clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def tension_e(growth):
    """Tension economica: 0.5 con crecimiento nulo, 1 con caida >= 10%, 0 con alza >= 10%."""
    return clip(0.5 - growth / 0.2)


def tension_p(polcomp):
    """Polarizacion binaria: 1 si la competencia politica (Polity) es faccional."""
    return 1.0 if polcomp in FACTIONAL else 0.0


def tension_i(polity2):
    """Fragilidad institucional: maxima en regimenes intermedios (polity2 = 0)."""
    return clip(1.0 - abs(polity2) / 10.0)


def tension_t(e, p, i):
    return WEIGHTS[0] * e + WEIGHTS[1] * p + WEIGHTS[2] * i


# ---------- lectura ----------

def read_exp003_panel(path):
    rows = []
    with open(path, encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            row = {"entity": raw["country"], "year": int(raw["year"]),
                   "outcome": int(raw["outcome"])}
            for key in ("E", "P", "I", "T", "loggdp_lag", "coups_prev10"):
                row[key] = float(raw[key])
            row["gdp_dup"] = int(raw.get("gdp_lag_duplicado") or 0)
            rows.append(row)
    return add_interactions(rows)


def add_interactions(rows):
    for row in rows:
        row["ExI"] = row["E"] * row["I"]
        row["PxI"] = row["P"] * row["I"]
    return sorted(rows, key=lambda r: (r["year"], r["entity"]))


# ---------- logistica por Newton con ridge ----------

def _solve(a, b):
    """Eliminacion gaussiana con pivoteo parcial."""
    n = len(b)
    m = [list(a[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            raise ValueError("Sistema singular")
        m[col], m[pivot] = m[pivot], m[col]
        for r in range(col + 1, n):
            f = m[r][col] / m[col][col]
            if f:
                for c in range(col, n + 1):
                    m[r][c] -= f * m[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (m[i][n] - sum(m[i][j] * x[j] for j in range(i + 1, n))) / m[i][i]
    return x


def _sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def fit_logistic(xs, ys, ridge=RIDGE, max_iter=100, tol=1e-10):
    """Minimiza -logL + (ridge/2)*||beta||^2 (intercepto sin penalizar).

    Estandariza con media y desvio de los datos recibidos (entrenamiento).
    Devuelve un dict utilizable por predict_logistic.
    """
    n, k = len(xs), len(xs[0])
    if n == 0 or len(ys) != n:
        raise ValueError("Datos de entrenamiento invalidos")
    mean = [sum(x[j] for x in xs) / n for j in range(k)]
    sd = []
    for j in range(k):
        var = sum((x[j] - mean[j]) ** 2 for x in xs) / n
        sd.append(math.sqrt(var) if var > 1e-18 else 1.0)
    z = [[1.0] + [(x[j] - mean[j]) / sd[j] for j in range(k)] for x in xs]
    beta = [0.0] * (k + 1)
    for _ in range(max_iter):
        grad = [0.0] * (k + 1)
        hess = [[0.0] * (k + 1) for _ in range(k + 1)]
        for row, y in zip(z, ys):
            p = _sigmoid(sum(b * v for b, v in zip(beta, row)))
            w = p * (1.0 - p)
            d = p - y
            for a in range(k + 1):
                grad[a] += d * row[a]
                ra = w * row[a]
                for b in range(a, k + 1):
                    hess[a][b] += ra * row[b]
        for a in range(k + 1):
            for b in range(a):
                hess[a][b] = hess[b][a]
        for a in range(1, k + 1):
            grad[a] += ridge * beta[a]
            hess[a][a] += ridge
        hess[0][0] += 1e-12
        step = _solve(hess, grad)
        beta = [b - s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < tol:
            break
    return {"beta": beta, "mean": mean, "sd": sd}


def predict_logistic(model, x):
    z = model["beta"][0]
    for b, v, m, s in zip(model["beta"][1:], x, model["mean"], model["sd"]):
        z += b * (v - m) / s
    return _sigmoid(z)


# ---------- metricas ----------

def brier_score(ps, ys):
    return sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ps)


def auc(ps, ys):
    """Probabilidad de que un positivo reciba mayor p que un negativo (empates = 0.5)."""
    n_pos = sum(ys)
    n_neg = len(ys) - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    rank_sum = 0.0
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and ps[order[j + 1]] == ps[order[i]]:
            j += 1
        mid = (i + j) / 2.0 + 1.0
        rank_sum += mid * sum(ys[order[t]] for t in range(i, j + 1))
        i = j + 1
    return (rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def calibration(ps, ys, bins=5):
    order = sorted(range(len(ps)), key=lambda i: (ps[i], i))
    out = []
    for b in range(bins):
        idx = order[b * len(order) // bins:(b + 1) * len(order) // bins]
        if idx:
            out.append({"quintil": b + 1, "n": len(idx),
                        "p_media": sum(ps[i] for i in idx) / len(idx),
                        "tasa_observada": sum(ys[i] for i in idx) / len(idx),
                        "eventos": sum(ys[i] for i in idx)})
    return out


def block_bootstrap_delta(ps, base, ys, years, reps=BOOT_REPS, seed=SEED):
    """IC95 de Brier(modelo) - Brier(base), remuestreando anios completos."""
    acc = defaultdict(lambda: [0.0, 0])
    for p, b, y, year in zip(ps, base, ys, years):
        acc[year][0] += (p - y) ** 2 - (b - y) ** 2
        acc[year][1] += 1
    blocks = [acc[year] for year in sorted(acc)]
    rng = random.Random(seed)
    deltas = []
    for _ in range(reps):
        num = den = 0
        for _ in blocks:
            s, n = blocks[rng.randrange(len(blocks))]
            num += s
            den += n
        deltas.append(num / den)
    deltas.sort()

    def q(f):
        pos = f * (len(deltas) - 1)
        lo = int(math.floor(pos))
        hi = min(lo + 1, len(deltas) - 1)
        return deltas[lo] + (deltas[hi] - deltas[lo]) * (pos - lo)

    return [q(0.025), q(0.975)]


# ---------- experimento ----------

def _matrix(rows, feats):
    return [[r[f] for f in feats] for r in rows]


def run_models(rows, test_start=TEST_START, ridge=RIDGE, strength=B1_STRENGTH,
               exploratory=True):
    """Devuelve predicciones alineadas sobre las mismas filas de prueba.

    Ninguna prediccion del anio t usa outcomes de anios >= t.
    """
    rows = sorted(rows, key=lambda r: (r["year"], r["entity"]))
    train = [r for r in rows if r["year"] < test_start]
    test = [r for r in rows if r["year"] >= test_start]
    if not train or not test:
        raise ValueError("El corte debe dejar entrenamiento y prueba")
    key = lambda p: (p["year"], p["entity"])  # noqa: E731
    preds, models = {}, {}
    b0 = {key(p): p["p"] for p in evaluate_baseline(rows, test_start)["predictions"]}
    b1 = {key(p): p["p"] for p in
          evaluate_entity_baseline(rows, test_start, strength)["predictions"]}
    preds["B0"] = [b0[key(r)] for r in test]
    preds["B1"] = [b1[key(r)] for r in test]
    y_train = [r["outcome"] for r in train]
    for name, feats in FEATURES.items():
        model = fit_logistic(_matrix(train, feats), y_train, ridge)
        models[name] = model
        preds[name] = [predict_logistic(model, [r[f] for f in feats]) for r in test]
    if exploratory:
        by_year = defaultdict(list)
        for r in rows:
            by_year[r["year"]].append(r)
        for name, base in EXPLORATORY.items():
            feats = FEATURES[base]
            cache = {}
            for year in sorted({r["year"] for r in test}):
                past = [r for y in sorted(by_year) if y < year for r in by_year[y]]
                model = fit_logistic(_matrix(past, feats), [r["outcome"] for r in past], ridge)
                for r in by_year[year]:
                    cache[key(r)] = predict_logistic(model, [r[f] for f in feats])
            preds[name] = [cache[key(r)] for r in test]
    return {"train": train, "test": test, "predictions": preds, "models": models}


def summarize(run, reps=BOOT_REPS, seed=SEED):
    test, preds = run["test"], run["predictions"]
    ys = [r["outcome"] for r in test]
    years = [r["year"] for r in test]
    b0 = brier_score(preds["B0"], ys)
    out = {}
    for name, ps in preds.items():
        bs = brier_score(ps, ys)
        entry = {"brier": bs, "skill_vs_B0": 1.0 - bs / b0, "auc": auc(ps, ys),
                 "p_media": sum(ps) / len(ps),
                 "calibracion_quintiles": calibration(ps, ys),
                 "tipo": "exploratorio" if name in EXPLORATORY else "preespecificado"}
        if name != "B0":
            entry["delta_brier_vs_B0"] = bs - b0
            entry["delta_brier_ic95_bootstrap_anual"] = block_bootstrap_delta(
                ps, preds["B0"], ys, years, reps, seed)
        if name in run["models"]:
            m = run["models"][name]
            entry["variables"] = list(FEATURES[name])
            entry["coeficientes_estandarizados"] = dict(
                zip(("intercepto",) + FEATURES[name], m["beta"]))
        out[name] = entry
    return out


def build_demo(run, rows, summary):
    test, preds = run["test"], run["predictions"]
    countries = defaultdict(lambda: {"years": [], "MT": [], "MX": [], "B0": [], "coup": [], "T": []})
    for i, r in enumerate(test):
        c = countries[r["entity"]]
        c["years"].append(r["year"])
        c["coup"].append(r["outcome"])
        c["T"].append(round(r["T"], 3))
        for name in ("MT", "MX", "B0"):
            c[name].append(round(preds[name][i], 4))
    coup_years = defaultdict(list)
    for r in rows:
        if r["outcome"]:
            coup_years[r["entity"]].append(r["year"])
    for name, c in countries.items():
        c["coup_years_panel"] = coup_years.get(name, [])
    return {
        "experimento": "EXP-003",
        "aviso": "Proyecto recreativo y educativo. No es un pronostico operativo.",
        "corte": {"entrenamiento": [TRAIN_START, TEST_START - 1], "prueba": [TEST_START, TEST_END]},
        "n_prueba": len(test), "eventos_prueba": sum(r["outcome"] for r in test),
        "modelos": {k: {"brier": round(v["brier"], 5), "auc": None if v["auc"] is None else round(v["auc"], 3),
                        "skill": round(v["skill_vs_B0"], 4), "tipo": v["tipo"],
                        "ic95": [round(x, 5) for x in v.get("delta_brier_ic95_bootstrap_anual", [])] or None}
                    for k, v in summary.items()},
        "countries": dict(sorted(countries.items())),
    }


def render_page(template, demo):
    if PLACEHOLDER not in template:
        raise ValueError("La plantilla no contiene el marcador " + PLACEHOLDER)
    payload = json.dumps(demo, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return template.replace(PLACEHOLDER, payload.replace("</", "<\\/"))


def sensitivity(rows):
    """EXPLORATORIO: repite los modelos preespecificados sin las filas cuyo PIB
    en t-1 esta duplicado en la fuente (URSS/Rusia, Yugoslavia, Checoslovaquia)."""
    kept = [r for r in rows if not r.get("gdp_dup")]
    summary = summarize(run_models(kept, exploratory=False))
    return {"filas_excluidas": len(rows) - len(kept),
            "n_prueba": sum(r["year"] >= TEST_START for r in kept),
            "eventos_prueba": sum(r["outcome"] for r in kept if r["year"] >= TEST_START),
            "modelos": {k: {"brier": v["brier"], "skill_vs_B0": v["skill_vs_B0"], "auc": v["auc"],
                            "delta_brier_ic95_bootstrap_anual": v.get("delta_brier_ic95_bootstrap_anual")}
                        for k, v in summary.items()}}


def _rate(rows):
    return sum(r["outcome"] for r in rows) / len(rows)


def main():
    parser = argparse.ArgumentParser(description="EXP-003: indice T vs golpes de Estado")
    parser.add_argument("--panel", type=Path, default=ROOT / "data" / "exp003_panel.csv")
    parser.add_argument("--results", type=Path, default=ROOT / "research" / "EXP-003-results.json")
    parser.add_argument("--demo", type=Path, default=ROOT / "docs" / "exp003_demo.json")
    parser.add_argument("--template", type=Path, default=ROOT / "docs" / "_plantilla.html")
    parser.add_argument("--page", type=Path, default=ROOT / "docs" / "index.html")
    args = parser.parse_args()

    rows = read_exp003_panel(args.panel)
    run = run_models(rows)
    summary = summarize(run)
    train, test = run["train"], run["test"]
    results = {
        "experimento": "EXP-003",
        "pregunta": "El indice T de EXP-001 (pesos sin ajustar), medido en t-1, anticipa intentos de golpe en t mejor que baselines simples?",
        "preespecificado": {
            "corte": {"entrenamiento": [TRAIN_START, TEST_START - 1], "prueba": [TEST_START, TEST_END]},
            "modelos": ["B0", "B1", "MT", "MH", "MX"], "ridge": RIDGE, "B1_strength": B1_STRENGTH,
            "bootstrap": {"bloques": "anio", "replicas": BOOT_REPS, "semilla": SEED},
            "pesos_T": dict(zip(("E", "P", "I"), WEIGHTS))},
        "exploratorio": sorted(EXPLORATORY),
        "panel": {"filas": len(rows), "eventos": sum(r["outcome"] for r in rows),
                  "paises": len({r["entity"] for r in rows})},
        "entrenamiento": {"n": len(train), "eventos": sum(r["outcome"] for r in train), "tasa": _rate(train)},
        "prueba": {"n": len(test), "eventos": sum(r["outcome"] for r in test), "tasa": _rate(test)},
        "modelos": summary,
        "sensibilidad_exploratoria_sin_pib_duplicado": sensitivity(rows),
        "advertencia": "Asociacion predictiva, no causal. MT_expansivo y MX_expansivo son exploratorios.",
    }
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                            encoding="utf-8")
    demo = build_demo(run, rows, summary)
    args.demo.parent.mkdir(parents=True, exist_ok=True)
    args.demo.write_text(json.dumps(demo, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n",
                         encoding="utf-8")
    if args.template.exists():
        args.page.write_text(render_page(args.template.read_text(encoding="utf-8"), demo), encoding="utf-8")
    else:
        print(f"AVISO: no existe {args.template}; no se genero la pagina", file=sys.stderr)

    print(f"Panel: {len(rows)} filas, {results['panel']['eventos']} eventos | "
          f"prueba: {len(test)} obs, {results['prueba']['eventos']} eventos")
    print(f"{'modelo':<14}{'Brier':>9}{'skill':>9}{'AUC':>7}  IC95 dBrier vs B0")
    for name, m in summary.items():
        ci = m.get("delta_brier_ic95_bootstrap_anual")
        ci_txt = f"[{ci[0]:+.5f}, {ci[1]:+.5f}]" if ci else "-"
        tag = " (exploratorio)" if m["tipo"] == "exploratorio" else ""
        print(f"{name:<14}{m['brier']:>9.5f}{m['skill_vs_B0']:>+9.4f}{m['auc']:>7.3f}  {ci_txt}{tag}")


if __name__ == "__main__":
    main()
