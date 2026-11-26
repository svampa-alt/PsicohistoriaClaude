# EXP-012 — Preregistro: caídas de gobernantes por protesta popular o rebelión

Fecha de registro: 2026-11-26 · Estado: **preespecificado, no ejecutado**. Se publica antes de construir el panel de eventos y de calcular cualquier predicción.

## Por qué

La hoja de ruta pide ≥30 episodios históricos con períodos comparables sin evento, y menciona como prioritarios la revolución iraní (1979) y la caída del Muro de Berlín (1989). Hasta ahora el laboratorio solo predijo golpes militares. Esta es una **familia de eventos distinta**: el gobernante cae por la calle o por las armas de rebeldes, no por los militares.

## Fuente

Archigos (Goemans, Gleditsch y Chiozza), leída de `archigos.rda` del paquete AuthoritarianismBook, en el mismo commit fijado de EXP-003 (`51716224…`). Cubre hasta el 31/12/2014. Hash SHA-256 del archivo en el manifiesto. Licencia de Archigos: **no verificada** en origen.

## Evento

`outcome = 1` en el año t si al menos un gobernante del país dejó el cargo con `exitcode` que empieza con «Popular Protest» o «Removed by Rebels» (con o sin apoyo extranjero). Hay **57 episodios desde 1960**: 22 antes de 1990 (por ejemplo Corea 1960, Irán 1979, Filipinas 1986, Rumania 1989) y 35 entre 1990 y 2014. La lista completa con nombre y fecha queda en el manifiesto.

Cada episodio es individual y verificable, y los controles son los demás países-año sin evento: cubre la meta de ≥30 episodios de la hoja de ruta para esta familia.

## Panel

`data/exp011_panel.csv` (V-Dem, con poder militar y movilización), años 1960–2014. Unión por código: Gleditsch-Ward (Archigos) contra COW (panel), idénticos salvo casos documentados en el código. Se agrega `rev_prev10`: años con al menos un evento de esta familia en t−10..t−1.

## Modelos

Entrenamiento 1960–1989; prueba **1990–2014**. Logística por Newton, ridge 1, estandarización con el entrenamiento; nivel con la corrección de EXP-004 (k = 10, aplicada a la tasa de esta familia).

- **B0:** tasa histórica de esta familia.
- **MHr:** logística sobre `rev_prev10` (el análogo de MH).
- **MR_c:** E, P, I, log PIB, `rev_prev10`, poder militar y movilización (`mil_lag`, `mob_lag`), con corrección de nivel.

## Hipótesis (1990–2014, bloques anuales, 1.000 réplicas, semilla 20261111)

- **R1:** Brier(MR_c) < Brier(B0), IC del Δ que excluye 0.
- **R2:** Brier(MR_c) < Brier(MHr), IC que excluye 0.
- **R3:** AUC(MR_c) ≥ 0,70.
- Se informan además, como descriptivo, el puesto y el percentil de riesgo de cada episodio de prueba.

Los episodios anteriores a 1990 (Irán 1979, Rumania 1989) están en el entrenamiento: su puesto se informará como **ajuste dentro de muestra**, no como pronóstico.

## Límites declarados

- 35 eventos en 25 años: potencia baja.
- La movilización masiva en t−1 puede ser la misma protesta que tumba al gobernante si empezó el año anterior: riesgo de que el modelo «vea venir» lo que ya está pasando. Se informará.
- V-Dem es retrospectivo. Archigos termina en 2014.
- Sin pronósticos a futuro.
