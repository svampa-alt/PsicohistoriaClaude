# EXP-006 — Resultados: V-Dem y prueba en 2020–2025

Fecha: 2026-11-18 · Issue #5 · Estado: **ejecutado** según el [preregistro](EXP-006-preregistro.md) (commit `8f1e144`) · [Panel](EXP-006-panel-vdem.md) · [Resultados JSON](EXP-006-results.json)

## Qué se probó

Modelos entrenados con 1960–1989 sobre el panel con V-Dem: polarización continua (`v2cacamps`) en lugar de P binario, y poliarquía en lugar de polity2. Se evaluaron en 2020–2025, los años de la nueva ola de golpes, que ningún experimento había visto.

## Confirmatorio: 2020–2025 (934 países-año, 17 eventos, tasa 1,8 %)

| Modelo | Brier | Skill vs B0 | AUC | p media | IC 95 % Δ vs B0 | IC 95 % Δ vs MH |
|---|---|---|---|---|---|---|
| B0 · tasa histórica | 0,01829 | — | 0,502 | 3,9 % | — | — |
| MH · golpes previos | 0,01792 | +2,0 % | 0,754 | 4,2 % | [−0,00103; +0,00027] | — |
| MT · índice T | 0,02281 | −24,8 % | 0,704 | 8,2 % | [+0,00323; +0,00640] | [+0,00318; +0,00733] |
| MX · multivariable | 0,01805 | +1,3 % | **0,865** | 4,6 % | [−0,00154; +0,00082] | [−0,00078; +0,00092] |
| **MX_c** | **0,01743** | **+4,7 %** | 0,861 | 0,95 % | **[−0,00109; −0,00062]** | [−0,00124; +0,00026] |
| MT_c | 0,01780 | +2,7 % | 0,687 | 1,7 % | [−0,00084; −0,00009] | [−0,00102; +0,00090] |
| MH_c | 0,01783 | +2,5 % | 0,738 | 0,85 % | [−0,00087; +0,00005] | [−0,00096; +0,00095] |

| Hipótesis preregistrada | Resultado |
|---|---|
| D1: MX_c mejor que B0 | **Cumplida** — IC [−0,00109; −0,00062] |
| D2: MX_c mejor que MH | **No cumplida** — IC [−0,00124; +0,00026] |
| D3: MX_c mejor que MH_c | **Cumplida** — Δ = −0,00040, IC [−0,00081; −0,00010] |

### Año por año

| Año | Países | Golpes | Tasa observada | MX_c (media) | B0 (media) |
|---|---|---|---|---|---|
| 2020 | 157 | 1 | 0,6 % | 0,9 % | 4,0 % |
| 2021 | 157 | 6 | 3,8 % | 1,1 % | 3,9 % |
| 2022 | 157 | 2 | 1,3 % | 0,9 % | 3,9 % |
| 2023 | 157 | 3 | 1,9 % | 0,9 % | 3,8 % |
| 2024 | 153 | 2 | 1,3 % | 1,0 % | 3,8 % |
| 2025 | 153 | 3 | 2,0 % | 1,0 % | 3,8 % |

## Secundarios

- **A, 2012–2019 con V-Dem** (1.256 filas, 14 eventos): MX_c 0,01098, frente a 0,01103 con Polity en EXP-005. Mismo patrón: le gana a B0 y a MH, empata con MH_c. Sustituir Polity por V-Dem **no empeora** nada.
- **B, 2020–2023 sin el PIB del Banco Mundial** (628 filas, 12 eventos): MX_c le gana a B0 (IC [−0,00123; −0,00054]); D2 y D3 no se cumplen (D3 queda al borde: [−0,00094; +0,00001]). El resultado de D3 en el confirmatorio depende en parte de 2024–2025.

## Interpretación

1. **La predicción escrita de antemano se cumplió en parte.** La corrección mira 10 años atrás y **subestima** la nueva ola: MX_c predice en promedio 0,95 % cuando ocurrió 1,8 %, y en 2021 (seis golpes) predijo 1,1 % contra 3,8 % observado. Aun así le gana a B0, porque B0 sobreestima casi el doble de lo que MX_c subestima, y porque MX_c ordena muy bien.
2. **Primera vez que el índice aporta más allá de la tasa base.** D3 se cumple: con V-Dem, MX_c le gana a MH_c, el modelo que solo corrige la historia de golpes. En EXP-004 y EXP-005, con Polity, eso nunca pasó. La polarización continua y la poliarquía ordenan mucho mejor el riesgo reciente (AUC 0,861 contra 0,738).
3. **Pero no le gana al modelo de golpes previos sin corregir (D2).** En años de suba, la tasa histórica alta de MH compensa en parte. Para lo que pasó en 2020–2025, ni subestimar ni sobreestimar es inocuo: el mejor modelo sería uno que ordene como MX y acierte el nivel, y eso todavía no lo tenemos.
4. **La discriminación es lo más sólido del laboratorio:** AUC entre 0,79 y 0,87 en tres ventanas fuera de muestra, con tres fuentes de datos distintas.

## Límites

- 6 bloques anuales y 17 eventos: D3 es el resultado más frágil (el secundario B no lo sostiene por sí solo).
- La subestimación es sistemática: con el diseño actual, la probabilidad absoluta no es confiable en años de cambio de tendencia.
- V-Dem es retrospectivo; el PIB de 2023–2024 viene de otra fuente.
- Asociación predictiva, no causal. Sin pronósticos a futuro: D2 no se cumplió.

## Reproducir

```bash
python -m unittest discover -s tests
python src/exp006_evaluate.py
```
