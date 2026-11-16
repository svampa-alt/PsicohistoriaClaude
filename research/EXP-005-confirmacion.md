# EXP-005 — Confirmación sobre años nuevos (2012–2019)

Fecha: 2026-11-16 · Issues #1 y #4 · Estado: **ejecutado** según el [preregistro](EXP-005-preregistro.md) (commit `9aa2763`, anterior al panel y a esta evaluación) · [Panel](EXP-005-panel-actualizado.md) · [Resultados JSON](EXP-005-results.json)

## Qué se probó

Si la corrección de tasa base de EXP-004 (MX_c) sigue ganando en años que **ningún experimento había evaluado**. Modelos entrenados con 1960–1989 del panel nuevo (Powell & Thyne 2026, Maddison 2023, Polity5), sin ningún ajuste posterior. Corrección con la tasa de golpes de los 10 años previos (k = 10).

## Resultado confirmatorio: 2012–2019 (1.245 países-año, 14 con intento de golpe, tasa 1,1 %)

| Modelo | Brier | Skill vs B0 | AUC | p media | IC 95 % Δ vs B0 | IC 95 % Δ vs MH |
|---|---|---|---|---|---|---|
| B0 · tasa histórica | 0,01211 | — | 0,600 | 4,3 % | — | — |
| MH · golpes previos | 0,01209 | +0,1 % | 0,632 | 4,3 % | [−0,00041; +0,00025] | — |
| MT · índice T | 0,01749 | −44,4 % | 0,796 | 8,1 % | [+0,00409; +0,00661] | [+0,00410; +0,00657] |
| MX · multivariable | 0,01383 | −14,2 % | **0,814** | 4,6 % | [+0,00077; +0,00262] | [+0,00100; +0,00247] |
| **MX_c** | **0,01103** | **+8,9 %** | 0,805 | 1,0 % | **[−0,00131; −0,00081]** | **[−0,00147; −0,00062]** |
| MT_c | 0,01108 | +8,5 % | 0,789 | 1,8 % | [−0,00118; −0,00086] | [−0,00140; −0,00046] |
| MH_c | 0,01108 | +8,5 % | 0,561 | 0,9 % | [−0,00132; −0,00069] | [−0,00153; −0,00046] |

| Hipótesis preregistrada | Resultado |
|---|---|
| C1: MX_c mejor que B0 | **Confirmada** — IC [−0,00131; −0,00081] |
| C2: MX_c mejor que MH | **Confirmada** — IC [−0,00147; −0,00062] |
| C3: MX_c mejor que MH_c | **No confirmada** — Δ = −0,00005, IC [−0,00024; +0,00013] |

## Secundario: 1990–2011 sobre el panel nuevo (3.303 filas, 80 eventos)

Replica EXP-003/004 con fuentes nuevas: MX_c 0,02300 contra B0 0,02449 y MH 0,02393 (C1 y C2 cumplidas); C3 de nuevo no cumplida. MT sigue perdiendo contra B0 sin corrección. Las conclusiones de EXP-003 y EXP-004 se sostienen con otras fuentes.

## Interpretación

1. **Primer resultado confirmado del laboratorio.** Un modelo fijado de antemano, entrenado con 1960–1989, le gana en Brier a la tasa histórica y al modelo de golpes previos en años nunca vistos.
2. **La ganancia en Brier viene de la tasa base.** Con la misma corrección, el modelo de solo golpes previos (MH_c) empata con MX_c. No está demostrado que E, P, I o el PIB mejoren las probabilidades.
3. **Donde el índice sí aporta es en el orden.** En los años nuevos MX_c ordena el riesgo con AUC 0,805 y MH_c con 0,561, casi azar. Los modelos basados en el índice siguen identificando *dónde* hay más riesgo, aunque no *cuánto*. No había hipótesis preregistrada sobre esta diferencia de AUC, así que queda como observación, sin intervalo.
4. **Los modelos sin corrección empeoran mucho en años recientes** (MT −44 %): la sobreestimación crece a medida que los golpes se vuelven más raros.

## Límites (declarados en el preregistro y nuevos)

- **14 eventos en 8 años.** El bootstrap por bloques usa solo 8 años: con tan pocos bloques los intervalos de percentil suelen ser **demasiado estrechos**. Las confirmaciones C1 y C2 deben leerse como favorables pero frágiles.
- Una diferencia de Brier de 0,001 es pequeña en términos absolutos: la tasa base es 1,1 %.
- 2020–2026, con la ola de golpes del Sahel, queda fuera porque Polity5 termina en 2018 (issue #5). Ese período es el próximo test natural y podría invertir la conclusión, porque la tasa volvió a subir.
- Asociación predictiva, no causal. Licencias de las fuentes no verificadas en origen.

## Reproducir

```bash
python -m unittest discover -s tests
python src/exp005_evaluate.py
```
