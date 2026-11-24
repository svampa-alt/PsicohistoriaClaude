# EXP-011 — Preregistro: poder militar y movilización masiva (V-Dem)

Fecha de registro: 2026-11-24 · Estado: **preespecificado, no ejecutado**. Se publica antes de construir el panel y de calcular cualquier predicción.

## Por qué

EXP-007 y EXP-010 mostraron que agregar variables redundantes (interacciones, demografía) no mejora el modelo. La conclusión fue buscar **información de otro tipo**. Las fuentes de conflictos (UCDP, COW) siguen bloqueadas por la red, pero V-Dem v16, ya descargado y verificado (SHA-256 `39b412d3…dc3d95ea`), trae dos medidas directamente ligadas al mecanismo de un golpe:

- `v2x_ex_military` (0–1): en qué medida el poder del jefe de Estado o de gobierno descansa en los militares. Cobertura del 100 % desde 1958.
- `v2cagenmob` (escala continua): frecuencia y tamaño de la movilización masiva en las calles. Cobertura del 98,7 %.

La literatura asocia los golpes con regímenes ya militarizados (la «trampa del golpe») y con crisis de movilización. Acá se prueba si eso **mejora el pronóstico fuera de muestra**.

## Panel

`data/exp006_panel.csv` (V-Dem, 1960–2025) más dos columnas de t−1, con el mismo cruce Polity→COW de EXP-006:

- `mil_lag` = `v2x_ex_military`.
- `mob_lag` = `v2cagenmob` reescalado a [0, 1] con los cuantiles 5 % y 95 % de las filas de entrenamiento 1960–1989 (igual que P_v en EXP-006).

Las filas sin alguno de los dos datos quedan fuera de **todos** los modelos.

## Modelos

Entrenamiento 1960–1989; logística por Newton, ridge 1, estandarización con el entrenamiento; nivel con la corrección de EXP-004 (k = 10).

- **MXs_c:** E, P, I, log PIB, golpes previos (el mejor hasta ahora).
- **MXm_c:** lo anterior más `mil_lag` y `mob_lag`.
- B0 y MH.

## Hipótesis (1990–2025, bloques anuales, 1.000 réplicas, semilla 20261111)

- **M1:** Brier(MXm_c) < Brier(MXs_c), IC del Δ que excluye 0.
- **M2:** AUC(MXm_c) > AUC(MXs_c), IC que excluye 0.
- **M3:** MXm_c mejor que B0 y que MH en Brier, IC que excluye 0.

Secundario: 2020–2025. Exploratorio (rotulado así): cada variable por separado.

## Límites declarados

- 1990–2025 ya se usó para elegir MXs: evidencia débil si sale favorable.
- `v2x_ex_military` puede subir **porque** hubo un golpe; como se usa en t−1, captura golpes de años anteriores y se superpone con «golpes previos».
- V-Dem se codifica retrospectivamente.
