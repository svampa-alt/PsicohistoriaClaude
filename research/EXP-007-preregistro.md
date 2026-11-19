# EXP-007 — Preregistro: ¿aportan las interacciones E×I y P×I?

Fecha de registro: 2026-11-19 · Issue #3 · Estado: **preespecificado, no ejecutado**. Se publica antes de calcular cualquier predicción del modelo sin interacciones.

## Pregunta

La hoja de ruta exige comprobar si las interacciones mejoran las predicciones fuera de muestra. MX incluye E×I y P×I, pero ningún experimento aisló su aporte. EXP-006 mostró que MX_c (con V-Dem) le gana a MH_c; falta saber si eso se debe a las interacciones o a las variables principales.

## Advertencia de honestidad

Las ventanas de prueba (1990–2025) ya se usaron para evaluar MX en EXP-005 y EXP-006. Lo que **no** se calculó nunca es el modelo sin interacciones, así que la comparación es nueva, pero los datos no son vírgenes.

## Diseño

- Panel: `data/exp006_panel.csv` (V-Dem, 1960–2025), sin cambios. SHA-256 en `data/exp006_manifest.json`.
- Entrenamiento 1960–1989; logística por Newton, ridge = 1, estandarización con el entrenamiento.
- **MX** = E, P, I, log PIB, golpes previos, E×I, P×I (como en EXP-003 a 006).
- **MXs** (sin interacciones) = E, P, I, log PIB, golpes previos.
- Ambos con y sin corrección de tasa base (k = 10, como en EXP-004): MX_c y MXs_c.
- Prueba: **1990–2025 completo** (36 bloques anuales, más potencia que las ventanas sueltas).
- Métricas: Brier y AUC, con IC 95 % del Δ por bootstrap de bloques anuales (1.000 réplicas, semilla 20261111). Para el AUC, el Δ se recalcula en cada réplica.

## Hipótesis (1990–2025)

- **I1 (primaria):** Brier(MX_c) < Brier(MXs_c), con IC del Δ que excluye 0.
- **I2:** AUC(MX_c) > AUC(MXs_c), con IC del Δ que excluye 0.
- Si el IC de I1 incluye 0: el aporte de las interacciones queda **no demostrado**. Si Brier(MX_c) > Brier(MXs_c) con IC que excluye 0: las interacciones **empeoran** y deberían salir del modelo.

## Secundarios

- Las mismas comparaciones por ventana: 1990–2011, 2012–2019, 2020–2025.
- Sin corrección: MX contra MXs.

## Exploratorio (rotulado así)

Cada interacción por separado (solo E×I, solo P×I).

## Límites declarados

- Ventanas ya conocidas por MX; resultado más débil que una confirmación.
- E, P e I están en [0, 1] y las interacciones están muy correlacionadas con sus componentes: con ridge = 1 los coeficientes se encogen, y el aporte puede quedar diluido.
- Sin pronósticos a futuro.
