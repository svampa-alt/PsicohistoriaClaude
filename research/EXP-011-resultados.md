# EXP-011 — El poder militar mejora el orden de riesgo

Fecha: 2026-11-25 · Estado: **ejecutado** según el [preregistro](EXP-011-preregistro.md) (commit `9acd7f8`) · [Panel](EXP-011-panel-militar-movilizacion.md) · [Resultados JSON](EXP-011-results.json)

## Qué se probó

Si agregar al mejor modelo (MXs_c) dos variables de V-Dem que miden mecanismos directos de un golpe mejora el pronóstico fuera de muestra:

- el peso de los militares en el poder ejecutivo (`v2x_ex_military`);
- la movilización masiva en la calle (`v2cagenmob`).

Todos los modelos se entrenaron en 1960–1989 y se evaluaron sobre las mismas filas.

## 1990–2025 (5.551 países-año, 109 eventos)

| Modelo | Brier | AUC | p media | IC 95 % Δ vs B0 | IC 95 % Δ vs MH | IC 95 % Δ vs MXs_c |
|---|---|---|---|---|---|---|
| B0 | 0,02007 | 0,604 | 4,9 % | — | [+0,00012; +0,00071] | [+0,00103; +0,00162] |
| MH | 0,01966 | 0,706 | 4,7 % | [−0,00071; −0,00012] | — | [+0,00059; +0,00123] |
| MXs_c | 0,01875 | 0,818 | 2,1 % | [−0,00162; −0,00103] | [−0,00123; −0,00059] | — |
| **MXm_c** (+ militar + movilización) | **0,01854** | **0,845** | 2,35 % | [−0,00194; −0,00115] | [−0,00150; −0,00078] | [−0,00047; +0,00006] |
| MX_mil_c (exploratorio) | 0,01852 | 0,842 | 2,2 % | [−0,00195; −0,00119] | [−0,00151; −0,00082] | [−0,00048; +0,00002] |
| MX_mob_c (exploratorio) | 0,01876 | 0,822 | 2,2 % | [−0,00162; −0,00100] | [−0,00122; −0,00058] | [−0,00007; +0,00009] |

| Hipótesis preregistrada | Resultado |
|---|---|
| M1: baja el Brier respecto de MXs_c | **No cumplida, por poco**: Δ −0,00021, IC [−0,00047; +0,00006] |
| M2: sube el AUC respecto de MXs_c | **Cumplida**: Δ +0,027, IC [+0,015; +0,039] |
| M3: le gana a B0 y a MH | **Cumplida**, ambos IC excluyen 0 |

## 2020–2025 (934 filas, 17 eventos)

MXm_c tiene el mejor Brier de todos los modelos corregidos (0,01724) y, por primera vez en esta ventana, le gana al modelo de golpes previos sin corregir con un IC que excluye 0 ([−0,00116; −0,00028]). El AUC queda igual que sin las variables (0,894 contra 0,898). Con 17 eventos, todo esto es frágil.

## Coeficientes (entrenamiento, estandarizados)

El poder militar es la variable con más peso del modelo (+0,46), por encima de los golpes previos (+0,35); la movilización suma menos (+0,22). La parte exploratoria lo confirma: casi toda la mejora viene de la variable militar.

## Interpretación

1. **Primer resultado positivo al agregar información.** Después de dos negativos con variables redundantes (EXP-007 y EXP-010), una variable que mide el mecanismo directo de un golpe sí mejora el orden de riesgo, con intervalo que excluye 0.
2. **Regímenes ya militarizados tienen más golpes**, coherente con la literatura sobre la «trampa del golpe». Parte de esto se superpone con «golpes previos», pero agrega información: el modelo mejora aunque ya tenga esa variable.
3. **La mejora en el Brier no alcanza a ser concluyente** (M1). El nivel de probabilidad sigue dependiendo de la corrección de tasa base.
4. **Nuevo modelo de referencia, con salvedad:** MXm_c pasa a ser el mejor, pero 1990–2025 ya se había usado para elegir MXs. Hay que confirmarlo en años nuevos.

## Límites

- Datos no vírgenes (ver arriba).
- `v2x_ex_military` puede subir después de un golpe exitoso; al usarse en t−1, captura golpes anteriores.
- V-Dem se codifica retrospectivamente.
- Asociación predictiva, no causal. Sin pronósticos a futuro.

## Reproducir

```bash
python -m unittest discover -s tests
python src/exp011_evaluate.py
```
