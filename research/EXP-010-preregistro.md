# EXP-010 — Preregistro: variables demográficas (población y urbanización)

Fecha de registro: 2026-11-22 · Estado: **preespecificado, no ejecutado**. Se publica antes de construir el panel y de calcular cualquier predicción.

## Por qué

La hoja de ruta pide variables demográficas y fuentes nuevas, y la red bloquea UCDP y COW. El Banco Mundial (accesible) tiene población y urbanización con cobertura casi completa desde 1960. La literatura sobre golpes asocia el riesgo con el tamaño del país y la urbanización (más capital concentrada, más fácil un golpe); acá se prueba si eso **mejora el pronóstico fuera de muestra**.

## Fuentes

Banco Mundial (WDI), API pública, descargada el 2026-11-22, 1958–2024: `SP.POP.TOTL` (población total) y `SP.URB.TOTL.IN.ZS` (población urbana, %). Hashes en el manifiesto. Se descartó la inflación (`FP.CPI.TOTL.ZG`): menos de la mitad de los países tiene datos en los años sesenta, y eso vaciaría el entrenamiento.

## Panel

`data/exp006_panel.csv` (V-Dem) más dos columnas, ambas de t−1: `lpop_lag` = log(población) y `urb_lag` = urbanización / 100. Unión por ISO3, con la misma tabla Polity→ISO de EXP-005. Las filas sin dato demográfico (por ejemplo URSS, Yugoslavia y Checoslovaquia, que el Banco Mundial no publica como agregados) quedan **fuera de todos los modelos**, para comparar sobre las mismas filas.

## Modelos

Entrenamiento 1960–1989; logística por Newton, ridge 1, estandarización con el entrenamiento; nivel con la corrección de EXP-004 (k = 10).

- **MXs_c:** E, P, I, log PIB, golpes previos (el mejor de EXP-007).
- **MXd_c:** lo anterior más `lpop_lag` y `urb_lag`.
- B0 y MH, como siempre.

## Hipótesis (1990–2025, bloques anuales, 1.000 réplicas, semilla 20261111)

- **G1:** Brier(MXd_c) < Brier(MXs_c), IC del Δ que excluye 0.
- **G2:** AUC(MXd_c) > AUC(MXs_c), IC que excluye 0.
- **G3:** MXd_c mejor que B0 y que MH en Brier, IC que excluye 0.

Secundario: las mismas comparaciones en 2020–2025.

## Límites declarados

- 1990–2025 ya se usó para elegir MXs: la comparación es nueva, pero los datos no son vírgenes.
- El Banco Mundial reconstruye series de Estados que en t−1 no existían como tales (repúblicas soviéticas antes de 1991): se usan tal como se publican.
- Población y urbanización cambian lento: es más probable que aporten orden (AUC) que nivel.
