# EXP-004 — Corrección de tasa base (tendencia temporal)

Fecha: 2026-11-14 · Issue #4 · Estado: **ejecutado** · [Preregistro](EXP-004-preregistro.md) (commit `fa36501`, anterior a la ejecución) · [Resultados](EXP-004-results.json)

## Pregunta

EXP-003 mostró que el índice T ordena bien el riesgo de golpe pero sobreestima, porque la tasa cayó tras 1990. ¿Alcanza con corregir **solo el nivel**, usando la tasa global de los 10 años anteriores, sin reajustar ninguna pendiente?

## Método (preespecificado)

Mismo panel, mismas 3.175 filas de prueba (74 eventos; 1990–2011 efectivos) y mismos coeficientes de EXP-003. Para cada año t se calcula `r_t`, la tasa suavizada de golpes en [t−10, t−1], y se desplaza la probabilidad en escala logit: `p_c = sigmoide(logit(p) + logit(r_t) − logit(r_0))`, con `r_0` = 6,44 % (entrenamiento). Cero parámetros nuevos ajustados. `MX_tend` agrega `r_t` como covariable de la logística (ajuste 1961–1989).

## Resultados

| Modelo | Brier | Skill vs B0 | AUC | p media | IC 95 % Δ vs B0 | IC 95 % Δ vs MH |
|---|---|---|---|---|---|---|
| B0 | 0,02370 | — | 0,640 | 5,5 % | — | — |
| MH | 0,02313 | +2,4 % | 0,687 | 4,9 % | [−0,00096; −0,00019] | — |
| MX (EXP-003) | 0,02446 | −3,2 % | 0,801 | 5,7 % | [−0,00038; +0,00194] | [+0,00043; +0,00222] |
| **MX_c** | **0,02227** | **+6,0 %** | 0,807 | 3,2 % | **[−0,00199; −0,00084]** | **[−0,00127; −0,00044]** |
| MT_c | 0,02270 | +4,2 % | 0,755 | 4,1 % | [−0,00144; −0,00051] | [−0,00093; +0,00011] |
| MH_c | 0,02237 | +5,6 % | 0,721 | 2,6 % | [−0,00158; −0,00111] | [−0,00117; −0,00037] |
| MX_tend | 0,02290 | +3,4 % | 0,808 | 4,4 % | [−0,00159; −0,00000] | [−0,00075; +0,00032] |

Tasa observada en la prueba: 2,3 %.

| Hipótesis | Resultado |
|---|---|
| H1: MX_c mejor que B0 | **Cumplida** — IC [−0,00199; −0,00084] |
| H2: MX_c mejor que MH | **Cumplida** — IC [−0,00127; −0,00044] |
| H3: MX_c mejor que MH_c | **No cumplida** — Δ = −0,00010, IC [−0,00062; +0,00048] |

Exploratorio (sensibilidad a k): con k=5, MX_c 0,02217; con k=20, MX_c 0,02259. El orden entre modelos corregidos no es estable: con k=20, MH_c (0,02243) queda por delante de MX_c.

## Interpretación

1. **La corrección de nivel funciona.** Es el primer modelo del laboratorio basado en el índice que supera a B0 y a MH en Brier con intervalos que excluyen cero, y lo hace sin perder discriminación (AUC 0,807).
2. **Pero el mérito es de la tasa base, no del índice.** La misma corrección aplicada al modelo más simple (MH_c, solo golpes previos) logra casi el mismo Brier, y H3 no se cumple: no está demostrado que E, P, I y el PIB aporten precisión de probabilidad más allá de la historia de golpes. Sí aportan orden: AUC 0,807 contra 0,721.
3. **Sigue sobreestimando**, menos que antes: MX_c predice 3,2 % en promedio contra 2,3 % observado, porque la ventana de 10 años reacciona con retraso a una tasa que baja.
4. Meter la tasa como covariable (MX_tend) rinde menos que el desplazamiento sin parámetros: en el entrenamiento la tasa varió poco, así que su coeficiente se estima mal.

## Límites

- **La prueba no era virgen.** El diseño se fijó conociendo los resultados de EXP-003 sobre esta misma ventana. Vale como evidencia débil; la confirmación requiere años nuevos (issue #1).
- Hereda todos los límites de EXP-003: PIB hasta 2010, 16 % de filas descartadas, P binario, PIB duplicado en Estados sucesores, codificación retrospectiva.
- Asociación predictiva, no causal. No habilita todavía pronósticos a futuro: H3 no se cumplió y falta la confirmación fuera de la ventana conocida.

## Reproducir

```bash
python -m unittest discover -s tests
python src/exp004_tendencia.py
```
