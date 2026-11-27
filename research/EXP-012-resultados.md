# EXP-012 — Caídas por protesta o rebelión: ordena, no calibra, y no vio la Primavera Árabe

Fecha: 2026-11-27 · Estado: **ejecutado** según el [preregistro](EXP-012-preregistro.md) (commit `dcf3933`) · [Panel y episodios](EXP-012-panel-caidas.md) · [Resultados JSON](EXP-012-results.json)

## Qué se probó

Si el modelo del laboratorio, entrenado con 1960–1989, anticipa en 1990–2014 las caídas de gobernantes por **protesta popular o rebelión armada** (Archigos), una familia de eventos distinta de los golpes. El modelo usa E, P, I, PIB, eventos previos de la familia, poder militar y movilización masiva.

## Resultados (1990–2014: 3.832 países-año, 28 eventos, tasa 0,7 %)

| Modelo | Brier | AUC | p media | IC 95 % Δ vs B0 | IC 95 % Δ vs MHr |
|---|---|---|---|---|---|
| B0 · tasa histórica | 0,00726 | 0,276 | 0,61 % | — | [−0,00001; +0,00001] |
| MHr · caídas previas | 0,00726 | 0,594 | 0,49 % | [−0,00001; +0,00001] | — |
| MR (sin corrección) | 0,00723 | 0,787 | 0,38 % | [−0,00010; +0,00004] | [−0,00010; +0,00004] |
| **MR_c** (preregistrado) | 0,00731 | **0,762** | 0,59 % | [−0,00007; +0,00020] | [−0,00007; +0,00020] |

| Hipótesis preregistrada | Resultado |
|---|---|
| R1: MR_c mejor que B0 en Brier | **No cumplida** |
| R2: MR_c mejor que MHr en Brier | **No cumplida** |
| R3: AUC de MR_c ≥ 0,70 | **Cumplida** (0,762) |

### Episodios de prueba: dónde los ubicaba el modelo (puesto de riesgo en su año)

- **Bien anticipados (top 10):** Georgia 1992 (4.º de 150), Afganistán 2001 (4.º), Haití 1990 (5.º), República Centroafricana 2003 (5.º), Congo-Kinshasa 1997 (6.º), RCA 2013 (7.º), Costa de Marfil 2000 (8.º), Ecuador 2000 (9.º), Etiopía 1991, Azerbaiyán 1993 y Egipto 2013 (10.º).
- **No vistos:** la Primavera Árabe de 2011. Egipto quedó en el puesto 107 de 158, Libia en el 124 y Túnez en el 50. También las «revoluciones de colores»: Georgia 2003 (54.º), Kirguistán 2005 y 2010 (88.º a 90.º) y Georgia 2007 (86.º).

### Casos históricos prioritarios (dentro de muestra, no son pronósticos)

Con el modelo ajustado sobre 1960–1989, que incluye esos años:

- Irán 1979: puesto 8 de 130.
- Filipinas 1986: puesto 6 de 131.
- Rumania 1989: puesto 34 de 131.

## Interpretación

1. **El modelo ordena el riesgo de estas caídas fuera de muestra** (AUC 0,76), sobre todo cuando vienen de guerras civiles o Estados frágiles: Chad, Congo, RCA, Afganistán.
2. **No mejora las probabilidades.** Con una tasa de 0,7 %, ningún modelo le gana a la tasa histórica en Brier, y la corrección de nivel empeora el resultado. Para eventos tan raros, el Brier casi no distingue modelos.
3. **Falla en las revoluciones «sorpresa»** de regímenes autoritarios estables y de ingreso medio, como Túnez, Egipto y Libia en 2011. Ese es justamente el tipo de evento que más interesaría anticipar, y los datos estructurales del año anterior no lo ven.
4. **Los coeficientes son distintos de los de los golpes.** Acá pesan sobre todo la tensión económica (+0,77) y la polarización (+0,72). La historia de caídas previas no aporta (−0,05). Tiene sentido: es otro mecanismo.

## Límites

- 28 eventos en 25 años; con eventos tan raros, el Brier tiene poca potencia.
- La movilización de t−1 puede ser la misma protesta que tumba al gobernante. Aun así, en 2011 el modelo no la vio: Egipto y Libia tenían movilización media en 2010.
- Archigos termina en 2014; su licencia no está verificada.
- Asociación predictiva, no causal. Sin pronósticos a futuro.

## Reproducir

```bash
python -m unittest discover -s tests
python src/exp012_evaluate.py
```
