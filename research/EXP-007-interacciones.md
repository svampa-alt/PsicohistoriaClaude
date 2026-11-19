# EXP-007 — Las interacciones E×I y P×I no aportan: empeoran

Fecha: 2026-11-19 · Issue #3 · Estado: **ejecutado** según el [preregistro](EXP-007-preregistro.md) (commit `23a6156`) · [Resultados JSON](EXP-007-results.json)

## Pregunta

¿Las interacciones E×I y P×I del modelo MX mejoran las predicciones fuera de muestra? Se comparó MX contra el mismo modelo sin interacciones (MXs), sobre el panel con V-Dem de EXP-006, entrenado en 1960–1989 y evaluado en 1990–2025.

## Resultado principal: 1990–2025 (5.559 países-año, 109 eventos, 36 bloques anuales)

| Modelo | Brier | AUC |
|---|---|---|
| MX_c (con interacciones) | 0,01894 | 0,810 |
| **MXs_c (sin interacciones)** | **0,01877** | **0,817** |
| MX (sin corrección) | 0,02083 | 0,815 |
| MXs (sin corrección) | 0,02030 | 0,832 |

| Hipótesis preregistrada | Resultado |
|---|---|
| I1: las interacciones bajan el Brier | **Refutada, en dirección contraria:** Δ = +0,00018, IC [+0,00003; +0,00033]. Las interacciones **empeoran** el Brier con un intervalo que excluye 0. |
| I2: las interacciones suben el AUC | **No cumplida:** Δ = −0,006, IC [−0,022; +0,011]. |

## Por ventana (secundario)

| Ventana | Eventos | Δ Brier MX_c − MXs_c | Δ AUC | Δ Brier sin corrección (MX − MXs) |
|---|---|---|---|---|
| 1990–2011 | 78 | +0,00029 [+0,00006; +0,00051] | −0,010 | +0,00050 [+0,00014; +0,00083] |
| 2012–2019 | 14 | +0,00005 [−0,00004; +0,00015] | −0,013 | +0,00051 [+0,00012; +0,00093] |
| 2020–2025 | 17 | −0,00005 [−0,00021; +0,00009] | −0,037 [−0,061; 0,000] | +0,00068 [+0,00023; +0,00112] |

Sin la corrección de nivel, el modelo sin interacciones es mejor en las tres ventanas, siempre con intervalos que excluyen cero. Con la corrección, empata o gana en todas salvo una diferencia mínima a favor de MX_c en 2020–2025. En ningún caso las interacciones mejoran el orden de los países (AUC).

## Exploratorio

- Solo E×I: Brier 0,01878 y AUC 0,818 en 1990–2025, prácticamente igual a sin interacciones.
- Solo P×I: Brier 0,01892 y AUC 0,810: el que más empeora. El daño viene sobre todo de P×I.

## Interpretación

1. **Resultado negativo claro para la hipótesis original del índice.** La idea de que la tensión económica o la polarización «pesan más» en regímenes frágiles no mejora el pronóstico; lo empeora levemente. Con este diseño, las interacciones agregan ruido.
2. **El modelo más simple es mejor.** MXs_c (E, P, I, PIB y golpes previos, sin interacciones) es el mejor modelo preespecificable del laboratorio hasta ahora. En 2020–2025 ordena con AUC 0,898.
3. **Consecuencia para los experimentos anteriores.** Las conclusiones de EXP-004 a 006 sobre MX_c no cambian, porque se refieren a lo que se preregistró. Pero un próximo experimento debería usar MXs_c como modelo principal, y ese cambio se registra como **decisión posterior a ver resultados** (exploratoria) hasta probarlo en datos nuevos.

## Límites

- Las ventanas ya habían sido usadas para evaluar MX; la comparación es nueva pero los datos no.
- Con ridge = 1, interacciones muy correlacionadas con sus componentes pueden quedar mal estimadas; otra especificación (centrar antes de multiplicar, por ejemplo) podría dar otro resultado. Queda como hipótesis para un experimento nuevo, no como excusa para este.
- Asociación predictiva, no causal.

## Reproducir

```bash
python -m unittest discover -s tests
python src/exp007_interacciones.py
```
