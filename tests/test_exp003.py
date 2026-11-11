"""Pruebas sinteticas de EXP-003 (sin datos reales ni dependencias externas)."""
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import exp003_model as m  # noqa: E402


def synthetic_panel(seed=7, entities=12, years=range(1970, 2000)):
    """Panel sintetico donde el riesgo crece con T y con los golpes previos."""
    rng = random.Random(seed)
    rows = []
    for e in range(entities):
        for year in years:
            growth = rng.uniform(-0.15, 0.15)
            polity2 = rng.randint(-10, 10)
            comp = rng.choice(["Factional", "Suppressed", "Institutionalized Electoral"])
            ee, pp, ii = m.tension_e(growth), m.tension_p(comp), m.tension_i(polity2)
            t = m.tension_t(ee, pp, ii)
            prev = rng.randint(0, 3)
            p_true = 1 / (1 + math.exp(-(-3.0 + 4.0 * t + 0.5 * prev)))
            rows.append({"entity": f"E{e:02d}", "year": year,
                         "outcome": int(rng.random() < p_true),
                         "E": ee, "P": pp, "I": ii, "T": t,
                         "loggdp_lag": rng.uniform(6, 10), "coups_prev10": float(prev)})
    return m.add_interactions(rows)


class IndexBounds(unittest.TestCase):
    def test_e_limits(self):
        self.assertEqual(m.tension_e(0.0), 0.5)
        self.assertEqual(m.tension_e(-0.10), 1.0)
        self.assertEqual(m.tension_e(-5.0), 1.0)
        self.assertEqual(m.tension_e(0.10), 0.0)
        self.assertEqual(m.tension_e(3.0), 0.0)
        self.assertAlmostEqual(m.tension_e(0.05), 0.25)

    def test_p_is_binary(self):
        for label in m.FACTIONAL:
            self.assertEqual(m.tension_p(label), 1.0)
        for label in ("Suppressed", "Restricted", "Institutionalized Electoral",
                      "Electoral Transition: Limited Conflict/Coercion", None, ""):
            self.assertEqual(m.tension_p(label), 0.0)

    def test_i_limits(self):
        self.assertEqual(m.tension_i(0), 1.0)
        self.assertEqual(m.tension_i(10), 0.0)
        self.assertEqual(m.tension_i(-10), 0.0)
        self.assertAlmostEqual(m.tension_i(-4), 0.6)
        self.assertEqual(m.tension_i(25), 0.0)

    def test_t_limits_and_exp001_weights(self):
        self.assertEqual(m.WEIGHTS, (0.40, 0.35, 0.25))
        self.assertEqual(m.tension_t(0, 0, 0), 0.0)
        self.assertAlmostEqual(m.tension_t(1, 1, 1), 1.0)
        self.assertAlmostEqual(m.tension_t(0.65, 0.70, 0.40), 0.605)  # ejemplo de EXP-001
        rng = random.Random(1)
        for _ in range(500):
            t = m.tension_t(m.tension_e(rng.uniform(-1, 1)),
                            m.tension_p(rng.choice(list(m.FACTIONAL) + ["x"])),
                            m.tension_i(rng.uniform(-12, 12)))
            self.assertTrue(0.0 <= t <= 1.0)


class Metrics(unittest.TestCase):
    def test_auc_extremes(self):
        self.assertEqual(m.auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]), 1.0)
        self.assertEqual(m.auc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]), 0.0)
        self.assertEqual(m.auc([0.3, 0.3, 0.3, 0.3], [0, 1, 0, 1]), 0.5)
        self.assertIsNone(m.auc([0.1, 0.2], [0, 0]))
        self.assertIsNone(m.auc([0.1, 0.2], [1, 1]))
        self.assertAlmostEqual(m.auc([0.1, 0.4, 0.35, 0.8], [0, 0, 1, 1]), 0.75)

    def test_brier_and_calibration(self):
        self.assertAlmostEqual(m.brier_score([0.0, 1.0, 0.5], [0, 1, 1]), 0.25 / 3)
        bins = m.calibration([i / 100 for i in range(100)], [0] * 50 + [1] * 50)
        self.assertEqual([b["n"] for b in bins], [20] * 5)
        self.assertEqual(bins[0]["tasa_observada"], 0.0)
        self.assertEqual(bins[-1]["tasa_observada"], 1.0)

    def test_bootstrap_zero_delta_and_determinism(self):
        ps = [0.2, 0.4, 0.6, 0.8]
        ys = [0, 0, 1, 1]
        years = [1, 1, 2, 2]
        self.assertEqual(m.block_bootstrap_delta(ps, ps, ys, years, reps=50), [0.0, 0.0])
        worse = [0.5] * 4
        a = m.block_bootstrap_delta(ps, worse, ys, years, reps=200, seed=3)
        self.assertEqual(a, m.block_bootstrap_delta(ps, worse, ys, years, reps=200, seed=3))
        self.assertLess(a[1], 0.0)


class Logistic(unittest.TestCase):
    def test_recovers_sign(self):
        rng = random.Random(11)
        xs, ys = [], []
        for _ in range(2000):
            a, b = rng.gauss(0, 1), rng.gauss(0, 1)
            p = 1 / (1 + math.exp(-(-1.0 + 1.5 * a - 1.0 * b)))
            xs.append([a, b])
            ys.append(int(rng.random() < p))
        model = m.fit_logistic(xs, ys, ridge=1.0)
        self.assertGreater(model["beta"][1], 0.5)
        self.assertLess(model["beta"][2], -0.3)
        self.assertLess(model["beta"][0], 0.0)
        self.assertGreater(m.predict_logistic(model, [2.0, 0.0]),
                           m.predict_logistic(model, [-2.0, 0.0]))

    def test_ridge_shrinks_and_handles_separation(self):
        xs = [[float(i)] for i in range(10)]
        ys = [0] * 5 + [1] * 5  # separacion perfecta: sin ridge divergiria
        weak = m.fit_logistic(xs, ys, ridge=0.1)
        strong = m.fit_logistic(xs, ys, ridge=10.0)
        self.assertTrue(math.isfinite(weak["beta"][1]))
        self.assertGreater(weak["beta"][1], strong["beta"][1])
        self.assertGreater(strong["beta"][1], 0.0)

    def test_constant_feature_is_safe(self):
        model = m.fit_logistic([[1.0, 3.0], [2.0, 3.0], [3.0, 3.0], [4.0, 3.0]], [0, 0, 1, 1])
        self.assertTrue(all(math.isfinite(b) for b in model["beta"]))

    def test_standardization_uses_training_moments(self):
        model = m.fit_logistic([[0.0], [2.0], [4.0], [6.0]], [0, 0, 1, 1])
        self.assertAlmostEqual(model["mean"][0], 3.0)
        self.assertAlmostEqual(model["sd"][0], math.sqrt(5.0))


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_panel()

    def test_same_rows_for_every_model(self):
        run = m.run_models(self.rows, test_start=1990)
        n = len(run["test"])
        self.assertEqual(n, 12 * 10)
        self.assertEqual(set(run["predictions"]),
                         {"B0", "B1", "MT", "MH", "MX", "MT_expansivo", "MX_expansivo"})
        for ps in run["predictions"].values():
            self.assertEqual(len(ps), n)
            self.assertTrue(all(0.0 < p < 1.0 for p in ps))

    def test_sign_of_t_recovered_in_pipeline(self):
        run = m.run_models(self.rows, test_start=1990, exploratory=False)
        self.assertGreater(run["models"]["MT"]["beta"][1], 0.0)
        self.assertGreater(run["models"]["MH"]["beta"][1], 0.0)

    def test_deterministic(self):
        a = m.summarize(m.run_models(self.rows, test_start=1990), reps=100)
        shuffled = list(self.rows)
        random.Random(5).shuffle(shuffled)
        b = m.summarize(m.run_models(shuffled, test_start=1990), reps=100)
        self.assertEqual(a, b)

    def test_future_labels_do_not_change_first_test_year(self):
        base = m.run_models(self.rows, test_start=1990)
        flipped = [dict(r, outcome=1 - r["outcome"]) if r["year"] >= 1990 else dict(r)
                   for r in self.rows]
        other = m.run_models(flipped, test_start=1990)
        first = [i for i, r in enumerate(base["test"]) if r["year"] == 1990]
        self.assertEqual(len(first), 12)
        for name in base["predictions"]:
            self.assertEqual([base["predictions"][name][i] for i in first],
                             [other["predictions"][name][i] for i in first], name)
        # los modelos de corte fijo no usan ninguna etiqueta de prueba
        for name in ("MT", "MH", "MX"):
            self.assertEqual(base["predictions"][name], other["predictions"][name])
        # y los expansivos SI deben cambiar despues (prueba de que el test discrimina)
        self.assertNotEqual(base["predictions"]["MT_expansivo"], other["predictions"]["MT_expansivo"])

    def test_labels_of_year_t_do_not_change_year_t_predictions(self):
        base = m.run_models(self.rows, test_start=1990)
        flipped = [dict(r, outcome=1 - r["outcome"]) if r["year"] >= 1995 else dict(r)
                   for r in self.rows]
        other = m.run_models(flipped, test_start=1990)
        upto = [i for i, r in enumerate(base["test"]) if r["year"] <= 1995]
        for name in base["predictions"]:
            self.assertEqual([base["predictions"][name][i] for i in upto],
                             [other["predictions"][name][i] for i in upto], name)

    def test_summary_marks_exploratory(self):
        s = m.summarize(m.run_models(self.rows, test_start=1990), reps=50)
        self.assertEqual(s["MT_expansivo"]["tipo"], "exploratorio")
        self.assertEqual(s["MX_expansivo"]["tipo"], "exploratorio")
        for name in ("B0", "B1", "MT", "MH", "MX"):
            self.assertEqual(s[name]["tipo"], "preespecificado")
        self.assertEqual(s["B0"]["skill_vs_B0"], 0.0)
        self.assertNotIn("delta_brier_ic95_bootstrap_anual", s["B0"])

    def test_render_page_embeds_json(self):
        html = m.render_page("<script>const D = " + m.PLACEHOLDER + ";</script>",
                             {"a": "</script>"})
        self.assertNotIn(m.PLACEHOLDER, html)
        self.assertNotIn("</script>\"", html)
        with self.assertRaises(ValueError):
            m.render_page("<html></html>", {})


if __name__ == "__main__":
    unittest.main()
