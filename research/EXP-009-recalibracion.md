# EXP-009 — Recalibración rápida del nivel

Fecha: 2026-11-21 · Issue #4 · Estado: **ejecutado** según el [preregistro](EXP-009-preregistro.md) (commit `3c58eab`) · [Resultados JSON](EXP-009-results.json)

## Qué se probó

En vez de corregir el nivel con la tasa global de golpes de los 10 años previos (MXs_c10, el método de EXP-004), cada año se reajusta el intercepto del modelo con **sus propios errores de los 5 años previos** (MXs_r5). Modelo base: MXs, sin interacciones (EXP-007), entrenado en 1960–1989 sobre el panel V-Dem.

## 1990–2025 (5.559 países-año, 109 eventos, tasa 2,0 %)

| Modelo | Brier | AUC | p media | IC 95 % Δ vs B0 | IC 95 % Δ vs MH | IC 95 % Δ vs MXs_c10 |
|---|---|---|---|---|---|---|
| B0 | 0,02004 | 0,604 | 4,9 % | — | [+0,00011; +0,00070] | [+0,00097; +0,00158] |
| MH | 0,01965 | 0,705 | 4,7 % | [−0,00070; −0,00011] | — | [+0,00056; +0,00119] |
| MXs (sin corregir) | 0,02031 | 0,832 | 4,9 % | [−0,00047; +0,00094] | [+0,00014; +0,00115] | [+0,00090; +0,00211] |
| MXs_c10 (referencia) | 0,01877 | 0,817 | 2,1 % | [−0,00158; −0,00097] | [−0,00119; −0,00056] | — |
| MXs_c5 (secundario) | 0,01875 | 0,815 | 1,95 % | [−0,00158; −0,00100] | [−0,00122; −0,00055] | [−0,00011; +0,00008] |
| **MXs_r5** | **0,01875** | **0,825** | 2,3 % | **[−0,00159; −0,00100]** | **[−0,00119; −0,00059]** | [−0,00011; +0,00008] |

| Hipótesis preregistrada | Resultado |
|---|---|
| K1: MXs_r5 mejor que MXs_c10 en 1990–2025 | **No cumplida**: Δ −0,00002, IC [−0,00011; +0,00008] (empate) |
| K2: MXs_r5 mejor que B0 y que MH | **Cumplida**, ambos IC excluyen 0 |
| K3: menor brecha de nivel en 2020–2025 | **Cumplida**: 0,42 puntos contra 0,94 de MXs_c10 |

## 2020–2025 (la ola reciente; 934 filas, 17 eventos, tasa 1,8 %)

| Modelo | Brier | AUC | p media |
|---|---|---|---|
| B0 | 0,01829 | 0,502 | 3,9 % |
| MH | 0,01792 | 0,754 | 4,2 % |
| MXs (sin corregir) | **0,01737** | **0,903** | 4,3 % |
| MXs_c10 | 0,01748 | 0,898 | 0,9 % |
| MXs_r5 | 0,01731 | 0,884 | 1,4 % |

En esta ventana MXs_r5 le gana a MXs_c10 (IC [−0,00031; −0,00001]), pero no era una hipótesis preregistrada, así que queda como observación.

### Año por año (probabilidad media)

| Año | Tasa observada | MXs_r5 | MXs_c10 |
|---|---|---|---|
| 2016 | 0,6 % | 1,7 % | 1,0 % |
| 2018 | 0,0 % | 1,3 % | 1,0 % |
| 2021 | 3,8 % | 1,0 % | 0,9 % |
| 2023 | 1,9 % | 1,5 % | 0,9 % |
| 2025 | 2,0 % | 1,8 % | 0,9 % |

## Interpretación

1. **En el período largo, empate.** Recalibrar con los errores propios no le gana a la corrección por tasa global en 1990–2025: las dos ganan igual a B0 y MH.
2. **Se adapta mejor cuando la tendencia cambia.** Después de la ola de 2021, MXs_r5 sube su nivel y para 2024–2025 casi acierta la tasa (1,8 % contra 2,0 %), mientras MXs_c10 sigue clavado en 0,9 %. La brecha media de 2020–2025 se reduce a la mitad.
3. **Ninguno anticipa un salto.** En 2021 los dos predijeron alrededor de 1 % y hubo 3,8 %. Un método que mira hacia atrás solo puede reaccionar después.
4. **Dato llamativo:** en 2020–2025 el modelo **sin ninguna corrección** (MXs) tiene un Brier casi igual al mejor y el AUC más alto. La corrección ayudó cuando los golpes bajaban (1990–2019) y estorba cuando suben. Elegir el nivel sigue siendo el problema abierto.

## Límites

- 1990–2025 ya se había usado en EXP-004 a 008: evidencia débil. La prueba limpia será 2026, cuando haya datos.
- Se amortiguó el paso de Newton para evitar divergencias en datos sintéticos extremos; en los datos reales los resultados son idénticos con y sin amortiguar (verificado).
- Asociación predictiva, no causal. Sin pronósticos a futuro.

## Reproducir

```bash
python -m unittest discover -s tests
python src/exp009_recalibracion.py
```
