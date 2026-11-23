# EXP-010 — Población y urbanización no mejoran el pronóstico

Fecha: 2026-11-23 · Estado: **ejecutado** según el [preregistro](EXP-010-preregistro.md) (commit `68eedfb`) · [Panel](EXP-010-panel-demografia.md) · [Resultados JSON](EXP-010-results.json)

## Qué se probó

¿Agregar población (log) y urbanización del Banco Mundial al mejor modelo (MXs_c: E, P, I, PIB y golpes previos, con corrección de tasa base) mejora el pronóstico de golpes fuera de muestra? Todos los modelos se entrenaron con 1960–1989 y se evaluaron sobre las mismas filas.

## 1990–2025 (5.518 países-año, 108 eventos)

| Modelo | Brier | AUC | p media | IC 95 % Δ vs B0 | IC 95 % Δ vs MH | IC 95 % Δ vs MXs_c |
|---|---|---|---|---|---|---|
| B0 | 0,02003 | 0,601 | 4,9 % | — | [+0,00010; +0,00070] | [+0,00106; +0,00163] |
| MH | 0,01965 | 0,707 | 4,8 % | [−0,00070; −0,00010] | — | [+0,00064; +0,00125] |
| **MXs_c** | **0,01870** | **0,814** | 2,1 % | [−0,00163; −0,00106] | [−0,00125; −0,00064] | — |
| MXd_c (con demografía) | 0,01875 | 0,800 | 1,8 % | [−0,00158; −0,00098] | [−0,00124; −0,00053] | [−0,00004; +0,00017] |

| Hipótesis preregistrada | Resultado |
|---|---|
| G1: la demografía baja el Brier | **No cumplida**: Δ +0,00005, IC [−0,00004; +0,00017] |
| G2: la demografía sube el AUC | **Refutada en dirección contraria**: Δ −0,014, IC [−0,025; −0,003]. Empeora el orden. |
| G3: MXd_c mejor que B0 y MH | Cumplida (lo arrastra el resto del modelo, no la demografía) |

En 2020–2025 (17 eventos) el patrón es el mismo: MXd_c tiene peor Brier que MXs_c (IC [+0,00004; +0,00017]) y un AUC algo menor.

## Por qué

En el entrenamiento, la urbanización tiene un coeficiente negativo fuerte (−0,47 estandarizado) y el PIB pasa a casi cero (+0,01): urbanización y riqueza miden casi lo mismo y se reparten el efecto. La población aporta poco (−0,14). Agregar variables correlacionadas sin información nueva solo suma ruido de estimación.

## Interpretación

1. **Resultado negativo, el segundo seguido.** Como las interacciones en EXP-007, más variables no mejoran el modelo: lo empeoran levemente.
2. **El modelo simple sigue siendo el mejor:** MXs_c (E, P, I, PIB y golpes previos).
3. Para mejorar no alcanza con agregar columnas de bases macro: probablemente hagan falta variables con información distinta (conflictos armados, protestas, elecciones), hoy bloqueadas o sin cargar.

## Límites

- 1990–2025 ya se había usado para elegir MXs: evidencia débil, pero el resultado es en contra de la hipótesis, así que eso no lo infla.
- Se perdieron 257 filas por falta de datos demográficos (incluidas la URSS, Yugoslavia y Checoslovaquia); los números de MXs_c difieren levemente de EXP-007 por eso.
- Asociación predictiva, no causal.

## Reproducir

```bash
python -m unittest discover -s tests
python src/exp010_evaluate.py
```
