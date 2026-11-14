# EXP-004 — Preregistro: corrección de tasa base (tendencia temporal)

Fecha de registro: 2026-11-14 · Issue: #4 · Estado: **preespecificado, no ejecutado** al momento de este commit.

## Advertencia de honestidad

Este diseño se escribe **después** de conocer los resultados de EXP-003 sobre la misma ventana de prueba (1990–2011 efectivos), incluido el dato de que las variantes expansivas (exploratorias) mejoran. Por lo tanto la prueba no es virgen: un resultado favorable aquí es evidencia **más débil** que una confirmación genuina y deberá repetirse sobre años nuevos cuando se actualicen las fuentes (issue #1, hoy bloqueado por la red de la sesión). Lo que sí queda fijado antes de ejecutar: fórmulas, k, filas, métricas y criterio de descarte.

## Hipótesis

EXP-003 mostró que MT y MX ordenan bien el riesgo pero sobreestiman porque la tasa de golpes cayó tras 1990. Hipótesis: **corregir solo el nivel** (sin reajustar pendientes) con la tasa global reciente, usando únicamente años anteriores, alcanza para que MX supere a B0 y a MH en Brier.

## Datos y filas

Mismo panel `data/exp003_panel.csv` (SHA-256 en `data/exp003_manifest.json`), mismo corte: entrenamiento 1960–1989, prueba 1990–2014 (3.175 filas, 74 eventos). Todas las comparaciones sobre las mismas filas de prueba.

## Definiciones (fijas)

- Tasa reciente para el año t, con k = **10**: `r_t = (golpes + 0.5) / (n + 1)` sobre las filas del panel con año en [t−k, t−1]. Solo usa outcomes anteriores a t.
- Tasa de entrenamiento: `r_0 = (golpes + 0.5) / (n + 1)` sobre 1960–1989.
- **Corrección por desplazamiento** (cero parámetros ajustados): para un modelo M de EXP-003 con probabilidad p,
  `p_c = sigmoide( logit(p) + logit(r_t) − logit(r_0) )`.
  Los coeficientes de M son exactamente los de EXP-003 (ajustados en 1960–1989, ridge = 1).
- Modelos: `MX_c` (primario), `MT_c` y `MH_c` (secundarios).
- Secundario adicional `MX_tend`: logística (Newton, ridge = 1, estandarización con el entrenamiento) sobre las variables de MX más `r_t` como covariable, ajustada en 1961–1989 (1960 no tiene años previos en el panel; para 1961–1969 la ventana usa los años disponibles desde 1960).

## Métricas y contraste

Brier, skill vs B0, AUC, calibración en 5 quintiles, e IC 95 % por bootstrap de bloques anuales (1.000 réplicas, semilla 20261111) del Δ Brier **vs B0 y vs MH**.

- **H1 (primaria):** Brier(MX_c) < Brier(B0) con IC 95 % del Δ que excluye 0.
- **H2:** Brier(MX_c) < Brier(MH) con IC 95 % que excluye 0.
- **H3:** Brier(MX_c) < Brier(MH_c) con IC que excluye 0 (¿aportan E, P, I y PIB algo más allá de la historia de golpes, una vez corregido el nivel?).

**Criterio de descarte:** si el IC de H1 incluye 0, la hipótesis queda no demostrada; si Brier(MX_c) ≥ Brier(B0), queda refutada en esta muestra. Se publica cualquiera sea el resultado.

## Exploratorio (rotulado así)

Sensibilidad a k ∈ {5, 20}. Cualquier otra variante que se agregue después de ver resultados.

## Fuera de alcance

Sin pronósticos a futuro. No se modifican los resultados ni la demo de EXP-003.
